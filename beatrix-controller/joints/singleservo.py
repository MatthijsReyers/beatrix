from joints.parameters import JointParameters

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

    def __init__(self, parameters: JointParameters, pca9685, angle, debug_mode: bool = False, offset = 0):
        self.offset = offset
        self.debug_mode = debug_mode
        self.current_angle = angle
        self.old_angle = angle
        self.new_angle = angle

        self.port = parameters.servo_port
        self.min_angle = parameters.min_angle
        self.max_angle = parameters.max_angle
        self.actuation_range = parameters.actuation_range
        self.mirrored = parameters.mirrored

        if not self.debug_mode:
            from adafruit_motor import servo
            self.pca = pca9685
            self.servo = servo.Servo(pca9685.channels[self.port], min_pulse=500, max_pulse=2500,
                                     actuation_range=self.actuation_range)

        # Update angle of servo
        self.set_angle(angle, angle)

    def set_angle(self, angle, new_angle):
        self.new_angle = self.bound_angle(new_angle)
        self.current_angle = self.bound_angle(angle)
        if self.new_angle == self.current_angle:
            self.old_angle = self.new_angle
        if not self.debug_mode:
            if not self.mirrored:
                self.servo.angle = self.__hard_actuation_bound(self.current_angle + self.offset)
            if self.mirrored:
                self.servo.angle = self.actuation_range - self.__hard_actuation_bound(self.current_angle + self.offset)
        # else:
        #     print('Servo',self.port,'going to',self.new_angle)

    def bound_angle(self, angle):
        """Bound the angle with the min and max angle parameters of the servo"""
        if self.min_angle <= angle <= self.max_angle:
            return angle
        elif angle < self.min_angle:
            return self.min_angle
        elif angle > self.max_angle:
            return self.max_angle

    def __hard_actuation_bound(self, angle):
        if angle < 0:
            return 0
        elif angle > self.actuation_range:
            return self.actuation_range
        else:
            return angle

