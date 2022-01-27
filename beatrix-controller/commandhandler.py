from controller import Controller
from autopilot import AutoPilot
from debugserver import DebugServer



class CommandHandler:
    def __init__(self, controller: Controller):
        self.controller = controller
        self.autopilot = AutoPilot(controller=controller)

        self.command_funcs = {
            'GO_HOME': self._cmd_home,
            'GET_POS': self._cmd_get_pos,
            'SET_POS': self._cmd_set_pos,
            'GET_ANG': self._cmd_get_ang,
            'SET_ANG': self._cmd_set_ang
        }

    def exec_cmd(self, cmd: bytes):
        """ Parses and executes a debug controller command. """
        try:
            cmd = cmd.decode('utf-8')
            cmd = json.loads(cmd)
            cmd_type = cmd['type']
            if cmd_type == self.command_funcs:
                func = self.command_funcs['__cmd_'+cmd['type']]
                func(**cmd['data'])
            else:
                print('Received invalid command:', cmd)
        except Exception as e:
            print('Caught exception when parsing command:\n', e)

    def _cmd_home(self):
        pass

    def _cmd_get_pos(self):
        pass

    def _cmd_set_pos(self, position: (float, float, float)):
        pass

    def _cmd_get_ang(self):
        pass

    def _cmd_set_ang(self, angles: dict):
        print('Received setting angles command:', angles)