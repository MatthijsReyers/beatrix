from controller import Controller
from autopilot import AutoPilot
from debugserver import DebugServer
import json

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

    def exec_cmd(self, cmd: bytes, client:(str,int)):
        """ Parses and executes a debug controller command. """
        try:
            cmd = cmd.decode('utf-8')
            cmd = json.loads(cmd)
            cmd_type = cmd['type']
            if cmd_type in self.command_funcs:
                func = self.command_funcs[cmd['type']]
                func(**cmd['data'])
            else:
                print('Received invalid command:', cmd)
        except Exception as e:
            print('Caught exception when parsing command:', type(e), '\n', e)

    def _cmd_home(self):
        pass

    def _cmd_get_pos(self):
        pass

    def _cmd_set_pos(self, position: (float, float, float)):
        pass

    def _cmd_get_ang(self):
        pass

    def _cmd_set_ang(self, angles: dict):
        try:
            print('Received setting angles command:', angles)
            if self.autopilot.running:
                print('Autopilot is running, ignoring command.')
            else:
                print(angles)
                self.controller.move_angles(angles)
        except Exception as e:
            print(e)
            print('Caught exception when parsing command:', type(e), '\n', e)