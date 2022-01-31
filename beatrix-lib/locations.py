from lib.constants import (BASE_JOINT_ID, SHOULDER_JOINT_ID, ELBOW_JOINT_ID, WRIST_JOINT_ID, 
    WRIST_TURN_JOINT_ID)
from lib.shapes import Shape

class Location:
    def __init__(self, base, shoulder, elbow, wrist, wrist_turn, name: str):
        self.base = base
        self.shoulder = shoulder
        self.elbow = elbow
        self.wrist = wrist
        self.wrist_turn = wrist_turn
        self.name = name

    def get_angle_dict(self) -> dict:
        return {
            BASE_JOINT_ID: self.base,
            SHOULDER_JOINT_ID: self.shoulder,
            ELBOW_JOINT_ID: self.elbow,
            WRIST_JOINT_ID: self.wrist,
            WRIST_TURN_JOINT_ID: self.wrist_turn,
        }

    def get_name(self):
        return self.name


TABLE_Z_COORDINATE = 5  # TODO

INPUT_AREA_CAM_VIEW  = Location(90, 90, 64, 107, 90, "Input area cam view")
INPUT_AREA_GRAB_CENTER = Location(97, 118, 68, 38, 90)
PUZZLE_AREA_CAM_VIEW = Location(180, 90, 64, 107, 90, "Puzzle area cam view")

# ---- Puzzle locations
OCTAGON = Location(186, 108, 77.47, 48.27, 0, "Octagon")

PUZZLE_LOCATIONS = {
    Shape.Octagon: OCTAGON
}

LOCATIONS_FOR_GUI = [
    INPUT_AREA_CAM_VIEW, 
    PUZZLE_AREA_CAM_VIEW, 
    OCTAGON
]

