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
from time import time
from time import process_time

HOVER_DIST = 10


class Controller:
    """
    Contains pre defined operations to be executed by the robot arm

    """


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
            position: Tuple of (X, Y, Z) coordinates
            wrist_orientation: Desired orientation of the end effector (z-axial locked with wrist)
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
        """
        Moves the robot arm to a location HOVER_DIST above the given coordinates
        Args:
            coordinates: coordinates that should be hovered above
            wrist_orientation: Desired orientation of the end effector (z-axial locked with wrist)
        """
        self._move_arm_to_workspace_coordinate((
            coordinates[0],
            coordinates[1],
            coordinates[2] + HOVER_DIST,
        ), wrist_orientation=wrist_orientation)

    def hover_above_location(self, location: Location, wrist_orientation: WristOrientation = WristOrientation.UNSET):
        """
        Moves the robot arm to a location HOVER_DIST above the given location
        Args:
            location: location that should be hovered above
            wrist_orientation: Desired orientation of the end effector (z-axial locked with wrist)
        """
        angles = location.get_angle_dict()
        coordinates = self.kinematics.get_forward_cartesian(angles)
        self.hover_above_coordinates(coordinates, wrist_orientation)

    def classify_current_view(self) -> 'RecognizedObject':
        """
        Retrieves view from camera and classifies the image according to the object classifier of this
        control class

        Returns: RecognizedObject of which the object classifier is most certain it is correct
                None if no classification was produced (or unknown classification)

        """

        start_time = process_time()

        latest_frame = self.camera.get_latest_frame()
        if latest_frame is None:
            return None

        classified_shapes = self.object_recognizer.object_recognition(latest_frame)
        draw_on_image(latest_frame, classified_shapes)
        file_string = f"classify-{time()}.jpg"

        cv2.imwrite(file_string, latest_frame)
        classified_shapes = list(filter(lambda y: y.label != Shape.Unknown, classified_shapes))
        if len(classified_shapes) == 0:
            return None

        classified_shapes = sorted(classified_shapes, key=lambda y: y.confidence)

        if classified_shapes[-1].label not in PUZZLE_LOCATIONS.keys():
            print('Did not find puzzle shape!')
            classified_shapes[-1].label = Shape.Octagon

        end_time = process_time()
        total_time = end_time - start_time

        print("*** Classifying image took {} seconds(?)".format(total_time))

        return classified_shapes[-1]


