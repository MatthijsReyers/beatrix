from robotarm import RobotArm
from camera import Camera
from lib.kinematics import IkPyKinematics
from lib.chain import beatrix_rep

class Controller():

    def __init__(self, robotarm: RobotArm, camera: Camera):
        self.kinematics = IkPyKinematics(chain=beatrix_rep)
        self.robotarm = robotarm
        self.camera = camera



    def _move_arm_to_workspace(self, x, y, z):
        solution_angles = self.kinematics.inverse(position=(x, y, z))

        new_angles = {

        }
