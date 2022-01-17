from robotarm import RobotArm
from camera import Camera

class Controller():
    def __init__(self, camera:'Camera', robotarm:'RobotArm'):
        self.camera = camera
        self.robotarm = robotarm
