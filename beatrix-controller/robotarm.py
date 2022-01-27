import time
import math
import numpy as np
from lib.constants import *

MAX_VELOCITY = 30  # Fastest speed of arm in degrees/s

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
DEFAULT_PARAMETERS = [{"servo": "single", "min angle": 0, "max angle": 270, "actuation range": 270,
                       "mirrored": False, "port": 0},  # base
                      {"servo": "dual", "min angle": 38, "max angle": 90, "actuation range": 180,
                       "mirrored": [True, False], "port": [1, 2]},  # shoulder
                      {"servo": "single", "min angle": 10, "max angle": 150, "actuation range": 180,
                       "mirrored": False, "port": 3},  # elbow
                      {"servo": "single", "min angle": 0, "max angle": 180, "actuation range": 180,
                       "mirrored": False, "port": 4},  # wrist
                      {"servo": "single", "min angle": 0, "max angle": 180, "actuation range": 180,
                       "mirrored": False, "port": 5}]  # wrist turn
GRABBER_PARAMETERS = {"min angle": 80, "max angle": 100, "actuation range": 180,
                      "open": 89, "closed": 91, "port": 6}


class JointParameters:

    def __init__(self, init_angle, min_angle, max_angle, servo_port, actuation_range, mirrored=False):
        self.initial_angle = init_angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.servo_port = servo_port
        self.actuation_range = actuation_range
        self.mirrored = mirrored


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

    def __init__(self, parameters: JointParameters, pca9685, angle, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.current_angle = angle
        self.old_angle = angle
        self.new_angle = angle

        self.port = parameters.servo_port
        self.min_angle = parameters.min_angle
        self.max_angle = parameters.max_angle
        self.actuation_range = parameters.actuation_range
        self.mirrored = parameters.mirrored

        self.pca = pca9685
        if not VIRTUAL_RUN:
            self.servo = servo.Servo(pca9685.channels[self.port], min_pulse=500, max_pulse=2500,
                                     actuation_range=self.actuation_range)

        # Update angle of servo
        self.set_angle(angle)

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

    def __init__(self, parameters: JointParameters, pca9685, angle, debug_mode: bool = False):
        self.debug_mode = debug_mode

        self.current_angle = angle
        self.old_angle = angle
        self.new_angle = angle

        self.min_angle = parameters.min_angle
        self.max_angle = parameters.max_angle
        self.actuation_range = parameters.actuation_range
        self.mirrored_left = parameters.mirrored[0]
        self.mirrored_right = parameters.mirrored[1]

        self.port_left = parameters.servo_port[0]
        self.port_right = parameters.servo_port[1]

        parameters_left = parameters
        parameters_left.mirrored = self.mirrored_left
        parameters_left.servo_port = self.port_left

        parameters_right = parameters
        parameters_right.mirrored = self.mirrored_right
        parameters_right.servo_port = self.port_right

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


class Grabber:
    """
        Class to control the grabber
        PARAMETERS:
        - dict[6]: {"port", "min angle", "max angle", "open", "closed", "actuation range"}

        METHODS:
        - set_angle
        - set_open
        - set_closed
    """

    def __init__(self, parameters, pca9685, angle, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.angle = angle
        self.port = parameters["port"]
        self.min_angle = parameters["min angle"]
        self.max_angle = parameters["max angle"]
        self.open = parameters["open"]
        self.closed = parameters["closed"]
        self.actuation_range = parameters["actuation range"]

        self.pca = pca9685
        if not VIRTUAL_RUN:
            self.grabber = servo.Servo(pca9685.channels[self.port], min_pulse=500, max_pulse=2500,
                                       actuation_range=self.actuation_range)

    def set_angle(self, new_angle):
        new_angle = self.bound_angle(new_angle)
        self.grabber.set_angle(new_angle)

    def set_open(self):
        self.grabber.set_angle(self.open)

    def set_closed(self):
        self.grabber.set_angle(self.closed)

    def bound_angle(self, angle):
        if self.min_angle <= angle <= self.max_angle:
            return angle
        elif angle < self.min_angle:
            return self.min_angle
        elif angle > self.max_angle:
            return self.max_angle


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
            - set_grabber
            - bound_angles
        PARAMETERS
            - joints
                list of joints of which this robot arm consists
    """

    def __init__(self, joint_ids:list=None, debug_mode:bool=False):
        """

        """
        self.N = N_JOINTS
        self.joints = dict()

        self.grabber = Grabber(GRABBER_PARAMETERS, PCA, 90, False)

        if joint_ids == None:
            joint_ids = [
                BASE_JOINT_ID,
                SHOULDER_JOINT_ID,
                ELBOW_JOINT_ID,
                WRIST_JOINT_ID,
                WRIST_TURN_JOINT_ID
            ]

        for j_id in joint_ids:
            parameters = JointParameters(min_angle=ANGLE_BOUNDS[j_id][0], max_angle=ANGLE_BOUNDS[j_id][1],
                                         servo_port=SERVO_PORTS[j_id], mirrored=JOINT_TYPE[j_id]['mirrored'],
                                         actuation_range=ACTUATION_RANGE[j_id],
                                         init_angle=INITIAL_ANGLES[j_id])

            if JOINT_TYPE[j_id]["duality"] == "single":
                self.joints[j_id] = (SingleServo(parameters=parameters, pca9685=PCA,
                                               angle=parameters.initial_angle))
            elif JOINT_TYPE[j_id]["duality"] == "dual":
                self.joints[j_id] = (DualServo(parameters=parameters, pca9685=PCA,
                                             angle=parameters.initial_angle))

        self.set_arm(INITIAL_ANGLES, 1)

    def set_arm(self, new_angles: dict, v_max):
        """
        Sets the angle of all servos smoothly over period of time
        ARGUMENTS
            - new_angle: dict()
                {Joint_id_1: desired angle, Joint_id_2: desired angle, etc...}
                joint id's as in constants file
        PARAMETERS
            - v_max: float time in seconds
        """

        new_angles = self.bound_angles(new_angles)
        old_angles = self.get_current_angles(new_angles.keys())

        if len(new_angles) != len(old_angles):
            raise ValueError("New angles is not the same size as old angles")

        old_angle_arr = np.array(list(old_angles.values()))
        new_angle_arr = np.array(list(new_angles.values()))
        total_angle_arr = new_angle_arr - old_angle_arr

        if v_max > MAX_VELOCITY:
            print("Currently no implementation for movement that is too fast\n")
            print(f"Velocity: {v_max} degrees/s over the max: {MAX_VELOCITY}")
            v_max = MAX_VELOCITY

        duration = (total_angle_arr * math.pi) / (2 * v_max)
        duration = np.max(duration)  # for now, use the max duration of all servos

        dtime = 0.02  # 50Hz
        steps = int(duration / dtime)

        # for each step adjust for each servo the angle
        for step in range(steps):
            current_ptime = time.process_time()
            for j_id, angle in new_angles.items():
                calculated_angle = get_angle_smooth(start_angle=old_angles[j_id],
                                                    end_angle=new_angles[j_id],
                                                    seconds=duration, elapsed=(step + 1) * dtime)
                self._set_servo(self.joints[j_id], calculated_angle, new_angles[j_id])

            time_elapsed = time.process_time() - current_ptime
            if time_elapsed >= dtime:
                print("!!!! Process took longer than control loop time !!!!")
                print("time elapsed = {}".format(time_elapsed))
            else:
                time.sleep(dtime - time_elapsed)

    @staticmethod
    def _set_servo(joint, angle, new_angle):
        joint.set_angle(angle, new_angle)

    def set_grabber(self, state, angle=None):
        """If no angle is parsed, state=0 is open, state=1 is closed"""
        if angle:
            self.grabber.set_angle(angle)
        elif state:
            self.grabber.set_open()
        else:
            self.grabber.set_closed()

    def bound_angles(self, angles: dict):
        for id, angle in angles.items():
            if self.joints[id].min_angle > angle:
                angles[id] = self.joints[id].min_angle
            elif self.joints[id].max_angle < angle:
                angles[id] = self.joints[id].max_angle

        return angles

    def get_current_angles(self, requested_angles=None):
        if requested_angles is None:
            to_be_retrieved_angles = self.joints
        else:
            to_be_retrieved_angles = requested_angles

        angles = dict()
        for j_id in to_be_retrieved_angles:
            angles[j_id] = self.joints[j_id].current_angle
        return angles


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
    time = (elapsed / seconds) * np.pi
    if elapsed < seconds:
        if end_angle > start_angle:
            return start_angle + (-.5 * math.cos(time) + .5) * moving_angle
        if end_angle < start_angle:
            return start_angle - (-.5 * math.cos(time) + .5) * moving_angle
    return end_angle

# if __name__ == "__main__":
#     print(math.cos(np.pi))
#     init_pos = [90, 80, 90, 70, 90]
#     robotarm = RobotArm(DEFAULT_PARAMETERS, init_pos)
#     # new_pos = [40, 30, 40, 30, 50]
#     # robotarm.set_arm(new_pos, 3)
