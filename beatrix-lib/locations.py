from lib.constants import BASE_JOINT_ID, SHOULDER_JOINT_ID, ELBOW_JOINT_ID, WRIST_JOINT_ID, WRIST_TURN_JOINT_ID


class Location:

    def __init__(self, base, shoulder, elbow, wrist, wrist_turn):
        self.base = base
        self.shoulder = shoulder
        self.elbow = elbow
        self.wrist = wrist
        self.wrist_turn = wrist_turn

    def get_angle_dict(self) -> dict:
        return {
            BASE_JOINT_ID: self.base,
            SHOULDER_JOINT_ID: self.shoulder,
            ELBOW_JOINT_ID: self.elbow,
            WRIST_JOINT_ID: self.wrist,
            WRIST_TURN_JOINT_ID: self.wrist_turn,
        }


TABLE_Z_COORDINATE = 5  # TODO

INPUT_AREA_CAM_VIEW = Location(0, 0, 0, 0, 0)  # TODO
PUZZLE_AREA_CAM_VIEW = Location(0, 0, 0, 0, 0)  # TODO
