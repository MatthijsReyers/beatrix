from robotarm import RobotArm
from camera import Camera
from lib.kinematics import IkPyKinematics
from lib.chain import beatrix_rep

class Controller():

    def __init__(self, robotarm: RobotArm, camera: Camera):
        self.kinematics = IkPyKinematics(chain=beatrix_rep)
        self.robotarm = robotarm
        self.camera = camera
