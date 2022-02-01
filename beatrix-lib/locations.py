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
INPUT_AREA_GRAB_CENTER = Location(95.0, 108, 77, 46, 90, "Input area grab center")
PUZZLE_AREA_CAM_VIEW = Location(180, 90, 64, 107, 90, "Puzzle area cam view")

# ---- Puzzle locations
OCTAGON = Location(186.0, 108, 77.47, 48.27, 0, "Octagon")
ELLIPSE = Location(168.0, 121.31, 54.63, 36, 165, "Ellipse")
SQUARE  = Location(156.9, 108, 83, 45, 146, "Square")
CIRCLE  = Location(201, 135.36, 18.5955905287035, 23, 74, "Circle")
SEMICIRCLE = Location(185.71, 96, 99, 51.0, 0.0, "Semicircle")
TRIANGLE   = Location(215.28, 98, 100, 58, 30, "Triangle")
RECTANLGE  = Location(205.0, 119, 62, 41, 151, "Rectangle")

PUZZLE_LOCATIONS = {
    Shape.Octagon: OCTAGON,
    Shape.Ellipse: ELLIPSE,
    Shape.Square:  SQUARE,
    Shape.Circle:  CIRCLE,
    Shape.Semicircle: SEMICIRCLE,
    Shape.Triangle:   TRIANGLE,
    Shape.Rectangle:  RECTANLGE
}

LOCATIONS_FOR_GUI = [
    INPUT_AREA_CAM_VIEW, 
    PUZZLE_AREA_CAM_VIEW, 
    OCTAGON
]

