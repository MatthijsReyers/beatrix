from robotarm import RobotArm
from camera import Camera
from lib.kinematics import IkPyKinematics
from lib.chain import beatrix_rep
from lib.constants import *


class Controller:

    def __init__(self, robotarm: RobotArm, camera: Camera):
        self.kinematics = IkPyKinematics(chain=beatrix_rep)
        self.robotarm = robotarm
        self.camera = camera

    def move_angles(self, angles:dict):
        self.robotarm.set_arm(angles, 15)

    def _move_arm_to_workspace_coordinate(self, x, y, z):
        solution_angles = self.kinematics.inverse(position=(x, y, z))

        new_angles = {
            BASE_JOINT_ID: solution_angles[1],
            SHOULDER_JOINT_ID: solution_angles[2],
            ELBOW_JOINT_ID: solution_angles[3],
            WRIST_JOINT_ID: solution_angles[4],
            WRIST_TURN_JOINT_ID: solution_angles[5]
        }
        self.robotarm.set_arm(new_angles=new_angles)
