from robotarm import RobotArm
from camera import Camera

class Controller():
    def __init__(self, camera:'Camera', robotarm:'RobotArm'):
        self.camera = camera
        self.robotarm = robotarm
        self.command_funcs = {
            'GO_HOME': self._cmd_home,
            'GET_POS': self._cmd_get_pos,
            'SET_POS': self._cmd_set_pos
        }

    def exec_cmd(self, cmd):
        """ Executes a debug controller command. """
        cmd_type = cmd['type']
        if cmd_type == self.command_funcs:
            func = self.command_funcs['__cmd_'+cmd['type']]
            func(**cmd['data'])
        else:
            print('Received invalid command:', cmd)

    def _cmd_home(self):
        pass

    def _cmd_get_pos(self):
        pass

    def _cmd_set_pos(self, position: (float, float, float)):
        pass