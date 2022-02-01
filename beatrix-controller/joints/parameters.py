
class JointParameters:
    def __init__(self, init_angle, min_angle, max_angle, servo_port, actuation_range, mirrored=False):
        self.initial_angle = init_angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.servo_port = servo_port
        self.actuation_range = actuation_range
        self.mirrored = mirrored

    def __str__(self) -> str:
        return f"""JointParameters(
\tinitial_angle={self.initial_angle},
\tmin_angle={self.min_angle},
\tmax_angle={self.max_angle},
\tservo_port={self.servo_port},
\tactuation_range={self.actuation_range},
\tmirrored={self.mirrored})"""

    def deepcopy(self):
        new_obj = JointParameters(self.initial_angle, self.min_angle, self.max_angle, self.servo_port, self.actuation_range, self.mirrored)
        return new_obj
