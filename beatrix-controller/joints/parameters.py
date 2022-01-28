
class JointParameters:
    def __init__(self, init_angle, min_angle, max_angle, servo_port, actuation_range, mirrored=False):
        self.initial_angle = init_angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.servo_port = servo_port
        self.actuation_range = actuation_range
        self.mirrored = mirrored
