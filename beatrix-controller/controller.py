from lib.kinematics import IkPyKinematics
from lib.chain import beatrix_rep
from lib.constants import *
from lib.locations import Location, INPUT_AREA_CAM_VIEW, PUZZLE_AREA_CAM_VIEW
from typing import Tuple
from objectrecognition import ObjectRecognizer
from lib.shapes import Shape
from lib.locations import PUZZLE_LOCATIONS
from objectrecognition import draw_on_image
from lib.kinematics import WristOrientation
import cv2

HOVER_DIST = 10


class Controller:

    def __init__(self, robotarm: 'RobotArm', camera: 'Camera', object_recognizer: ObjectRecognizer):
        self.kinematics = IkPyKinematics(chain=beatrix_rep)
        self.robotarm = robotarm
        self.camera = camera
        self.object_recognizer = object_recognizer

    def _move_arm_to_workspace_coordinate(self, position: Tuple[float, float, float],
                                          wrist_orientation: WristOrientation = WristOrientation.UNSET):
        """
            Moves the robot arm to a 3d point in space
        Args:
            x: coordinate
            y: coordinate
            z: height coordinate
        """
        new_angles = self.kinematics.inverse(position=(position[0], position[1], position[2]), wrist_orientation=wrist_orientation)
        self.robotarm.set_arm(new_angles=new_angles)

    def go_to_location(self, location: Location):
        """
        Moves the robot arm to a specific pre defined location
        Args:
            location: location object including joint angles
        """
        angles = location.get_angle_dict()
        self.robotarm.set_arm(angles)

    def hover_above_coordinates(self, coordinates: Tuple[float,float,float], 
            wrist_orientation: WristOrientation = WristOrientation.UNSET):
        self._move_arm_to_workspace_coordinate((
            coordinates[0],
            coordinates[1],
            coordinates[2] + HOVER_DIST,
        ), wrist_orientation=wrist_orientation)

    def hover_above_location(self, location: Location, wrist_orientation: WristOrientation = WristOrientation.UNSET):
        """

        Args:
            wrist_orientation:
            location:
        """
        angles = location.get_angle_dict()
        coordinates = self.kinematics.get_forward_cartesian(angles)
        self.hover_above_coordinates(coordinates, wrist_orientation)

    def classify_current_view(self) -> 'RecognizedObject':
        """

        Returns:

        """
        latest_frame = self.camera.get_latest_frame()
        if latest_frame is None:
            return None

        classified_shapes = self.object_recognizer.object_recognition(latest_frame)
        draw_on_image(latest_frame, classified_shapes)
        cv2.imwrite('LatestClassify.jpg', latest_frame)
        classified_shapes = list(filter(lambda y: y.label != Shape.Unknown, classified_shapes))
        if len(classified_shapes) == 0:
            return None

        classified_shapes = sorted(classified_shapes, key=lambda y: y.confidence)

        if classified_shapes[-1].label not in PUZZLE_LOCATIONS.keys():
            print('Did not find puzzle shape!')
            classified_shapes[-1].label = Shape.Octagon
        return classified_shapes[-1]


