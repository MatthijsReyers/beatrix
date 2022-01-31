from lib.kinematics import IkPyKinematics
from lib.chain import beatrix_rep
from lib.constants import *
from lib.locations import Location, INPUT_AREA_CAM_VIEW, PUZZLE_AREA_CAM_VIEW
from typing import Tuple
from autopilot import AutoPilot


class Controller:

    def __init__(self, robotarm: 'RobotArm', camera: 'Camera'):
        self.kinematics = IkPyKinematics(chain=beatrix_rep)
        self.robotarm = robotarm
        self.camera = camera

    def _move_arm_to_workspace_coordinate(self, position: Tuple[float,float,float]):
        """
            Moves the robot arm to a 3d point in space
        Args:
            x: coordinate
            y: coordinate
            z: height coordinate
        """
        new_angles = self.kinematics.inverse(position=(position[0], position[1], position[2]))
        self.robotarm.set_arm(new_angles=new_angles)

    def go_to_location(self, location: Location):
        """
        Moves the robot arm to a specific pre defined location
        Args:
            location: location object including joint angles
        """
        angles = location.get_angle_dict()
        self.robotarm.set_arm(angles)
