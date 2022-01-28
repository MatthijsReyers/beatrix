
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

        if not self.debug_mode:
            from adafruit_motor import servo
            self.pca = pca9685
            self.grabber = servo.Servo(pca9685.channels[self.port], min_pulse=500, max_pulse=2500,
                                       actuation_range=self.actuation_range)

    def set_angle(self, new_angle):
        new_angle = self.bound_angle(new_angle)
        self.grabber.angle = new_angle

    def set_open(self):
        print("set open")
        #self.grabber.angle = self.open
        self.set_angle(self.open)

    def set_closed(self):
        print("set closed")
        # self.grabber.angle = self.closed
        self.set_angle(self.closed)

    def bound_angle(self, angle):
        if self.min_angle <= angle <= self.max_angle:
            return angle
        elif angle < self.min_angle:
            return self.min_angle
        elif angle > self.max_angle:
            return self.max_angle
