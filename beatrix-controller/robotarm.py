from adafruit_servokit import ServoKit
import time
import math
import numpy as np

MAX_VELOCITY = 90  # Fastest speed of arm in degrees/s
N_SERVOS = 6  # Total number of servos

""" UPDATE
    Dennis: moved the servo actuation to the main RobotArm class. Idea is to insert the set_angle_smooth
    into the RobotArm class and remove the SingleServo class. For now/ testing purposes cosine smooth
    is implemented.
"""


class SingleServo:
    def __init__(self, parameters, port, angle, debug_mode:bool=False):
        self.debug_mode = debug_mode
        self.port = port
        self.angle = angle
        # todo: actually move the servo to the angle?

        self.minangle = parameters["minangle"]
        self.maxangle = parameters["maxangle"]

        self.joint = ServoKit(channels=16)
        self.joint.servo[port].set_pulse_width_range(500, 2500)

    # def set_angle(self, angle):
    #     self.angle = self.bound_angle(angle)
    #     self.joint.servo[self.port].angle = self.angle

    def set_angle_smooth(self, angle, seconds):
        elapsed = 0
        start_angle = self.angle()
        end_angle = self.bound_angle(angle)
        moving_angle = abs(start_angle - end_angle)
        current_angle = start_angle
        dt = .01
        # amound of pos x shift correction
        correction = 1 / (1 - (1 - sigmoid(6)) * 2)
        while elapsed < seconds:
            t = (elapsed / seconds)*12 - 6
            step_size = moving_angle * derivative_sigmoid(t) * ((dt/seconds)*12) * correction
            if end_angle > start_angle:
                current_angle += step_size
                current_angle = min(current_angle, end_angle)
            if end_angle < start_angle:
                current_angle -= step_size
                current_angle = max(current_angle, end_angle)
            self.angle = self.bound_angle(current_angle)
            self.joint.servo[self.port].angle = self.bound_angle(current_angle)
            elapsed += dt
            time.sleep(dt)
        self.angle = self.bound_angle(angle)
        self.joint.servo[self.port].angle = self.bound_angle(angle)

    def bound_angle(self, angle):
        if self.minangle <= angle <= self.maxangle:
            return angle
        elif angle < self.minangle:
            return self.minangle
        elif angle > self.maxangle:
            return self.maxangle

    def get_angle(self):
        # temp fix for shoulder joint
        if self.port != 2:
            return self.angle
        else:
            return 180 - self.angle


class RobotArm:
    """
        Main class to initialise and control the robot arm
        port allocation
            [0:base, 1:shoulder, 2:shoulder mirror, 3:elbow, 4:wrist, 5:grabber]

        parameters
            Shoulder parameters are defined once
            [base, shoulder, elbow, wrist, grabber]
            - angle_bounds: list(5) of dict(2) with 'min angle' and 'max angle'
            - init_pos: list(5) of initial angles

        methods
            - set_angle
            - get_angle
    """

    def __init__(self, angle_bounds, init_pos):
        self.kit = ServoKit(channels=16)
        self.cur_angle = [0, 0, 0, 0, 0]

        # duplicate shoulder parameters for the second shoulder servo
        self.init_pos = init_pos.insert(2, init_pos[1])
        self.angle_bounds = angle_bounds.insert(2, init_pos[1])

        for i in range(N_SERVOS):
            self.kit.servo[N_SERVOS].set_pulse_width_range(500, 2500)
            self.kit.servo[N_SERVOS].angle = init_pos[N_SERVOS]

    def set_arm(self, old_angle, angle, duration):
        """
        Sets the angle of all servos over period of time
        parameters
            - old_angle: list(5) of angles, shoulder ports 1 and 2 share angle
            - angle: list(5) of angles, shoulder ports 1 and 2 share angle
            - duration: float time in seconds
        """
        # todo: update the get_angle with the sensor output

        self.cur_angle = angle

        # duplicate the first shoulder angle for the second one
        old_angle = old_angle.insert(2, angle[1])
        angle = angle.insert(2, angle[1])
        old_angle = np.array(old_angle)
        angle = np.array(angle)
        velocity = abs(old_angle - angle) / duration

        # bound the input angles to the min and max angles
        for i in range(N_SERVOS):
            angle[i] = self.bound_angle(i, angle[i])

        if (velocity > MAX_VELOCITY).any():
            print("Currently no implementation for movement that is too fast\n")
            print(f"Velocities: {velocity} degrees/s")
        else:
            # make the steps courser, reducing execution time
            dtime = 0.02  # 50Hz
            steps = int(duration / dtime)
            if steps > 30:
                dtime = 0.04
                steps = int(duration / dtime)

            # for each step adjust for each servo the angle
            for i in range(steps):
                for port in range(6):
                    new_angle = get_angle_smooth(start_angle = old_angle[port], end_angle = angle[port], seconds = duration, elapsed = (i+1)*dtime, scalar_bounds=1)
                    # new_angle = cosine(old_angle[port], angle[port], duration, steps)
                    self._set_servo(port, new_angle)

    def _set_servo(self, port, angle):
        if port != 2:
            self.kit.servo[port].angle = self.bound_angle(port, angle)
        # exception for the second shoulder servo
        else:
            self.kit.servo[port].angle = self.mirror(self.bound_angle(port, angle))

    def bound_angle(self, port, angle):
        if self.angle_bounds[port]['min angle'] <= angle <= self.angle_bounds[port]['max angle']:
            return angle
        elif angle < self.angle_bounds[port]['min angle']:
            return self.angle_bounds[port]['min angle']
        elif angle > self.angle_bounds[port]['max angle']:
            return self.angle_bounds[port]['max angle']

    def get_angle(self):
        return self.cur_angle

    @staticmethod
    def mirror(angle):
        return 180 - angle


def sigmoid(x):
    """
        Basic implementation of the sigmoid function, may not work well with large negative numbers.
    """
    sigmoid = 1 / (1 + math.exp(-x))
    return sigmoid


def derivative_sigmoid(x):
    sigmoid = sigmoid(x)
    derivative = sigmoid * (1-sigmoid)
    return derivative


def cosine(old_angle, new_angle, duration, step):
    a = old_angle
    b = new_angle
    period = 1/duration
    return a + b - b*math.cos(period*3.1415*step)

def get_angle_smooth(start_angle, end_angle, seconds, elapsed, scalar_bounds):
    """
        Go to a different angle in a smooth motion
        Arguments:
            start_angle: the angle of the servo before this function was called
            end_angle: the angle we want the servo to go too
            seconds: how long the motion should last
            elapsed: how much time has passed
            scalar_bounds: how aggressively it should accelerate/decelerate, should be in (0,1], else it will default to 1
        Returns: new angle given the elapsed time
    """
    moving_angle = abs(start_angle - end_angle)  # the degrees the servo has to move
    bound = 6*scalar_bounds  # the interval of the sigmoid, [-bound, bound]
    if scalar_bounds > 1 or scalar_bounds <= 0:
        bound=6
    correction = 1/(1 - (1 - sigmoid(bound))*2) # correction scalar so that the sigmoid will go from 0 to 1 on the interval
    time = ((elapsed) / seconds)*bound*2 - bound
    if end_angle > start_angle:
        return start_angle + correction*(sigmoid(time)-sigmoid(-bound))*moving_angle
    if end_angle < start_angle:
        return start_angle - correction*(sigmoid(time)-sigmoid(-bound))*moving_angle