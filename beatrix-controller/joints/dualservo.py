from joints.parameters import JointParameters
from joints.singleservo import SingleServo

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