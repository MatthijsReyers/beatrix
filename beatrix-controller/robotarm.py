import time
import math
import numpy as np

MAX_VELOCITY = 90  # Fastest speed of arm in degrees/s

# False if running with robot arm, true otherwise.
VIRTUAL_RUN = True

# Only instantiate servos and other physical components when ran with the robot arm
if not VIRTUAL_RUN:
    from board import SCL, SDA
    import busio
    from adafruit_motor import servo
    from adafruit_pca9685 import PCA9685
    I2C = busio.I2C(SCL, SDA)
    PCA = PCA9685(I2C)
    PCA.frequency = 50
if VIRTUAL_RUN:
    PCA = None

# Default parameters, only thing that should be edited is min angle and max angle,
# or if the shoulder is reversed, mirrored for the shoulder
DEFAULT_PARAMETERS = [{"servo": "single", "min angle": 70, "max angle":110, "actuation range": 270,
                       "mirrored": False, "port": 0},  # base
                    {"servo": "dual", "min angle": 70, "max angle":110, "actuation range": 180,
                     "mirrored": [False, True], "port": [1, 2]},  # shoulder
                    {"servo": "single", "min angle": 70, "max angle":110, "actuation range": 180,
                     "mirrored": False, "port": 3},  # elbow
                    {"servo": "single", "min angle": 70, "max angle":110, "actuation range": 180,
                     "mirrored": False, "port": 4},  # wrist
                    {"servo": "single", "min angle": 70, "max angle":110, "actuation range": 180,
                     "mirrored": False, "port": 5}]  # grabber


class SingleServo:
    """
        Main class to control a servo, represents a single servo joint,
        however it is also used by the DualServo class to control the individual servos

        ARGUMENTS
        - parameters: dict(5)
            - servo: type of servo single/dual
            - min angle: in degrees
            - max angle: in degrees
            - actuation range: total range of servo in degrees
            - mirrored: bool, for one of the shoulder joints
            - port: int of input on the PCA9685
        - PCA9685
        _ angle: in degrees, the initial position of the servo
            {base: 0, shoulder: 90, elbow: 90, wrist: 90, grabber: 0}
        - debug_mode: bool

        METHODS
        - set_angle: lineally at max speed

        PARAMETERS
        - old_angle: previous angle ordered
        - new_angle: current angle ordered
        - current_angle: updated every step when moving
    """

    def __init__(self, parameters, pca9685, angle, debug_mode:bool=False):
        """Initialization of the servo."""
        self.debug_mode = debug_mode
        self.current_angle = angle
        self.old_angle = angle
        self.new_angle = angle

        self.port = parameters["port"]
        self.min_angle = parameters["min angle"]
        self.max_angle = parameters["max angle"]
        self.actuation_range = parameters["actuation range"]
        self.mirrored = False
        if parameters["mirrored"]:
            self.mirrored = parameters["mirrored"]

        self.pca = pca9685
        if not VIRTUAL_RUN:
            self.servo = servo.Servo(pca9685.channels[self.port], min_pulse=500, max_pulse=2500,
                                     actuation_range=self.actuation_range)

    def set_angle(self, angle, new_angle):
        self.new_angle = self.bound_angle(new_angle)
        self.current_angle = self.bound_angle(angle)
        if self.new_angle == self.current_angle:
            self.old_angle = self.new_angle
        if not VIRTUAL_RUN:
            if not self.mirrored:
                self.servo.angle = self.current_angle
            if self.mirrored:
                self.servo.angle = self.actuation_range - self.current_angle

    def bound_angle(self, angle):
        """Bound the angle with the min and max angle parameters of the servo"""
        if self.min_angle <= angle <= self.max_angle:
            return angle
        elif angle < self.min_angle:
            return self.min_angle
        elif angle > self.max_angle:
            return self.max_angle


class DualServo:
    """
        Class to control dual-servos/shoulder, same functionality as single servo
    """
    def __init__(self, parameters, pca9685, angle, debug_mode:bool=False):
        self.debug_mode = debug_mode

        self.current_angle = angle
        self.old_angle = angle
        self.new_angle = angle

        self.min_angle = parameters["min angle"]
        self.max_angle = parameters["max angle"]
        self.actuation_range = parameters["actuation range"]
        self.mirrored_left = False
        self.mirrored_right = True
        if parameters["mirrored"]:
            self.mirrored_left = parameters["mirrored"][0]
            self.mirrored_right = parameters["mirrored"][1]
        self.port_left = parameters["port"][0]
        self.port_right = parameters["port"][1]
        parameters_left = {"min angle": self.min_angle, "max angle": self.max_angle,
                           "actuation range": self.actuation_range, "mirrored": self.mirrored_left,
                           "port": self.port_left}
        parameters_right = {"min angle": self.min_angle, "max angle": self.max_angle,
                            "actuation range": self.actuation_range, "mirrored": self.mirrored_right,
                            "port": self.port_right}

        self.pca = pca9685
        self.SingleServo_left = SingleServo(parameters_left, pca9685, angle, debug_mode)
        self.SingleServo_right = SingleServo(parameters_right, pca9685, angle, debug_mode)

    def set_angle(self, angle, new_angle):
        self.new_angle = self.bound_angle(new_angle)
        self.current_angle = self.bound_angle(angle)
        if self.new_angle == self.current_angle:
            self.old_angle = self.new_angle
        self.SingleServo_left.set_angle(self.current_angle, self.new_angle)
        self.SingleServo_right.set_angle(self.current_angle, self.new_angle)
    
    def bound_angle(self, angle):
        if self.min_angle <= angle <= self.max_angle:
            return angle
        elif angle < self.min_angle:
            return self.min_angle
        elif angle > self.max_angle:
            return self.max_angle

    def get_angle(self):
        return self.curent_angle


class RobotArm:
    """
        Main class to initialise and control the robot arm
        - port allocation
            [0:base, 1:shoulder, 2:shoulder mirror, 3:elbow, 4:wrist, 5:grabber]

        ARGUMENTS
        - parameters
            Shoulder parameters are defined once
            [base, shoulder, elbow, wrist, grabber]
            - parameters: list(5) of dict(3) with 'min angle' and 'max angle', 'actuation range'
            - init_pos: list(5) of initial angles

        METHODS
            - set_arm
            - bound_angle

        PARAMETERS
        - old_angle: previous angle ordered
        - new_angle: current angle ordered
        - current_angle: updated every step when moving
    """

    def __init__(self, parameters, init_pos):
        self.N = min(len(parameters), len(init_pos))
        self.joints = list()
        self.current_angle = list()
        self.bounds = list()
        for i in range(self.N):
            self.bounds.append({"min angle": parameters[i]["min angle"],
                                "max angle": parameters[i]["max angle"]})
            if parameters[i]["servo"] == "single":
                self.joints.append(SingleServo(parameters[i], PCA, 90))
            if parameters[i]["servo"] == "dual":
                self.joints.append(DualServo(parameters[i], PCA, 90))        
            self.current_angle.append(90)
        self.set_arm(init_pos, 1)

    def set_arm(self, new_angle, duration):
        """
        Sets the angle of all servos smoothly over period of time
        parameters
            - old_angle: list(5) of angles, shoulder ports 1 and 2 share angle
            - angle: list(5) of angles, shoulder ports 1 and 2 share angle
            - duration: float time in seconds
        """
        # todo: update the get_angle with the sensor output
        new_angle = self.bound_angle(new_angle)
        old_angle = self.bound_angle(self.current_angle)
        self.current_angle = old_angle
        old_angle = np.array(old_angle)
        new_angle = np.array(new_angle)
        velocity = abs(old_angle - new_angle) / duration

        if (velocity > MAX_VELOCITY).any():
            print("Currently no implementation for movement that is too fast\n")
            print(f"Velocities: {velocity} degrees/s")
        else:
            dtime = 0.02  # 50Hz
            steps = int(duration / dtime)

            # for each step adjust for each servo the angle
            for step in range(steps):
                for i in range(self.N):
                    self.current_angle[i] = get_angle_smooth(start_angle=old_angle[i],
                                                             end_angle=new_angle[i],
                                                             seconds=duration,
                                                             elapsed=(step+1)*dtime)
                    self._set_servo(self.joints[i], self.current_angle[i], new_angle[i])
                time.sleep(dtime)

    @staticmethod
    def _set_servo(joint, angle, new_angle):
        joint.set_angle(angle, new_angle)

    def bound_angle(self, angle):
        bound_angle = list()
        for i in range(self.N):
            if self.bounds[i]['min angle'] <= angle[i] <= self.bounds[i]['max angle']:
                bound_angle.append(angle[i])
            elif angle[i] < self.bounds[i]['min angle']:
                bound_angle.append(self.bounds[i]['min angle'])
            elif angle[i] > self.bounds[i]['max angle']:
                bound_angle.append(self.bounds[i]['max angle'])
        return bound_angle


def get_angle_smooth(start_angle, end_angle, seconds, elapsed):
    """
        Go to a different angle in a smooth motion
        Arguments:
            start_angle: the angle of the servo before this function was called
            end_angle: the angle we want the servo to go too
            seconds: how long the motion should last
            elapsed: how much time has passed
        Returns: new angle given the elapsed time
    """
    moving_angle = abs(start_angle - end_angle)  # degrees the servo has to move
    time = (elapsed / seconds)*np.pi
    if elapsed < seconds:
        if end_angle > start_angle:
            return start_angle + (-.5*math.cos(time)+.5)*moving_angle
        if end_angle < start_angle:
            return start_angle - (-.5*math.cos(time)+.5)*moving_angle
    return end_angle


if __name__ == "__main__":
    print(math.cos(np.pi))
    init_pos = [90, 80, 90, 70, 90]
    robotarm = RobotArm(DEFAULT_PARAMETERS, init_pos)
    # new_pos = [40, 30, 40, 30, 50]
    # robotarm.set_arm(new_pos, 3)