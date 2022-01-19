from adafruit_servokit import ServoKit


class SingleServo:
    def __init__(self, parameters, port, angle, debug_mode:bool=False):
        self.debug_mode = debug_mode
        self.port = port
        self.angle = angle

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

    def get_angle(self):
        return self.angle


class DualServo:
    def __init__(self, parameters, ports, angle, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.port1 = ports[0]
        self.port2 = ports[1]
        self.angle = angle

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
            self.angle = 0
            self.joint.servo[self.port1].angle = 0
            self.joint.servo[self.port2].angle = 180
        elif angle > self.maxangle:
            self.angle = 180
            self.joint.servo[self.port1].angle = 180
            self.joint.servo[self.port2].angle = 0

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
        self.base.set_angle(angle)
        self.shoulder.set_angle(angle)
        self.elbow.set_angle(angle)
        self.wrist.set_angle(angle)
        self.grabber.set_angle(angle)

    def get_angle(self):
        angels = [self.base.get_angle(), self.shoulder.get_angle(), self.elbow.get_angle(), self.wrist.get_angle(),
                  self.grabber.get_angle()]
        return angels
