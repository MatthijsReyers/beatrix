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

INPUT_AREA_CAM_VIEW  = Location(85, 101, 60, 106, 90, "Input area cam view")
INPUT_AREA_GRAB_CENTER = Location(84, 117, 82, 55, 90, "Input area grab center")
PUZZLE_AREA_CAM_VIEW = Location(172, 94, 60, 107, 90, "Puzzle area cam view")

HOVER_ABOVE_PUZZLES = Location(172, 95, 58, 25, 90, "Hover above puzzle")

# ---- Puzzle locations
OCTAGON = Location(175, 114, 88, 60, 90, "Octagon")
ELLIPSE = Location(156, 126, 60, 41, 69, "Ellipse")
SQUARE  = Location(148, 113, 79, 43, 68, "Square")
CIRCLE  = Location(194.7, 142, 25.7, 31.7, 120, "Circle")
SEMICIRCLE = Location(175, 102, 105, 60, 90, "Semicircle")
TRIANGLE   = Location(206.8, 106, 89, 50, 120, "Triangle")
RECTANLGE  = Location(198.4, 126, 59, 40, 115, "Rectangle")
DIAMOND = Location(175, 130, 52, 48, 90, "Diamond")
PENTAGON = Location(161, 138, 30, 34, 80, "Pentagon")

PUZZLE_LOCATIONS = {
    Shape.Octagon: OCTAGON,
    Shape.Ellipse: ELLIPSE,
    Shape.Square:  SQUARE,
    Shape.Circle:  CIRCLE,
    Shape.Semicircle: SEMICIRCLE,
    Shape.Triangle:   TRIANGLE,
    Shape.Rectangle:  RECTANLGE,
    Shape.Diamond: DIAMOND,
    Shape.Pentagon: PENTAGON,
}

LOCATIONS_FOR_GUI = [
    INPUT_AREA_CAM_VIEW, 
    PUZZLE_AREA_CAM_VIEW, 
    OCTAGON
]

