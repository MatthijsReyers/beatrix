from adafruit_servokit import ServoKit
import time


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

    def set_angle(self, angle):
        if self.minangle < angle < self.maxangle:
            self.angle = angle
            self.joint.servo[self.port].angle = angle
        elif angle < self.minangle:
            self.angle = self.minangle
            self.joint.servo[self.port].angle = self.minangle
        elif angle > self.maxangle:
            self.angle = self.maxangle
            self.joint.servo[self.port].angle = self.maxangle

    def set_angle_smooth(self, angle, seconds):
        elapsed = 0
        start_angle = self.angle()
        end_angle = self.bound_angle(angle)
        moving_angle = abs(start_angle - end_angle)
        current_angle = start_angle
        dt = .01
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
        return self.angle


class DualServo:
    def __init__(self, parameters, ports, angle, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.port1 = ports[0]
        self.port2 = ports[1]
        self.angle = angle
        # todo: move the servo to the angle?

        self.minangle = parameters["minangle"]
        self.maxangle = parameters["maxangle"]

        self.joint = ServoKit(channels=16)
        self.joint.servo[ports[0]].set_pulse_width_range(500, 2500)
        self.joint.servo[ports[1]].set_pulse_width_range(500, 2500)

    def set_angle(self, angle):
        if self.minangle < angle < self.maxangle:
            self.angle = angle
            self.joint.servo[self.port1].angle = angle
            self.joint.servo[self.port2].angle = 180 - angle
        elif angle < self.minangle:
            self.angle = self.minangle
            self.joint.servo[self.port1].angle = self.minangle
            self.joint.servo[self.port2].angle = 180 - self.minangle
        elif angle > self.maxangle:
            self.angle = self.maxangle
            self.joint.servo[self.port1].angle = self.maxangle
            self.joint.servo[self.port2].angle = 180 - self.maxangle

    def get_angle(self):
        return self.angle


class RobotArm:
    def __init__(self, parameters, ports, position):
        self.base = SingleServo(parameters[0], ports[0], position[0])
        self.shoulder = DualServo(parameters[1], ports[1], position[1])
        self.elbow = SingleServo(parameters[2], ports[2], position[2])
        self.wrist = SingleServo(parameters[3], ports[3], position[3])
        self.grabber = SingleServo(parameters[4], ports[4], position[4])

    def set_angle(self, angle):
        """
            Disabled the function since it could very likely damage the arm if the minimum angle and maximum angle of the joints are not properly set.
        """
        pass
        # self.base.set_angle(angle)
        # self.shoulder.set_angle(angle)
        # self.elbow.set_angle(angle)
        # self.wrist.set_angle(angle)
        # self.grabber.set_angle(angle)

    def get_angle(self):
        angels = [self.base.get_angle(), self.shoulder.get_angle(), self.elbow.get_angle(), self.wrist.get_angle(),
                  self.grabber.get_angle()]
        return angels

import math
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
