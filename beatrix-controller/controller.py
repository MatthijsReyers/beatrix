from robotarm import RobotArm
from camera import Camera
from lib.kinematics import IkPyKinematics
from lib.chain import beatrix_rep
from lib.constants import *
from lib.locations import Location, INPUT_AREA_CAM_VIEW, PUZZLE_AREA_CAM_VIEW


class Controller:

    def __init__(self, robotarm: RobotArm, camera: Camera):
        self.kinematics = IkPyKinematics(chain=beatrix_rep)
        self.robotarm = robotarm
        self.camera = camera

    def _move_arm_to_workspace_coordinate(self, x, y, z):
        """
            Moves the robot arm to a 3d point in space
        Args:
            x: coordinate
            y: coordinate
            z: height coordinate
        """
        new_angles = self.kinematics.inverse(position=(x, y, z))
        self.robotarm.set_arm(new_angles=new_angles)

    def go_to_location(self, location: Location):
        pass
