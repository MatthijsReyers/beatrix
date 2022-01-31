from controller import Controller
from autopilot import AutoPilot
from debugserver import DebugServer
from lib.constants import INITIAL_ANGLES
import json

class CommandHandler:
    def __init__(self, server, controller: Controller):
        self.controller = controller
        self.autopilot = AutoPilot(controller=controller)
        self.server = server

        self.command_funcs = {
            'GO_HOME': self._cmd_home,
            'GET_POS': self._cmd_get_pos,
            'SET_POS': self._cmd_set_pos,
            'GET_ANG': self._cmd_get_ang,
            'SET_ANG': self._cmd_set_ang,
            'GRABBER': self._cmd_grabber,
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
        print('[CMD] Go home')
        self.controller.robotarm.set_arm(INITIAL_ANGLES, 30)

    def _cmd_get_pos(self):
        pass

    def _cmd_set_pos(self, position: (float, float, float)):
        pass

    def _cmd_get_ang(self):
        pass

    def _cmd_set_ang(self, angles: dict):
        print('[CMD] Set angles:', list(angles.values()))
        if self.autopilot.running:
            print('Autopilot is running, ignoring command.')
        else:
            self.controller.robotarm.set_arm(angles, 30)

    def _cmd_grabber(self, closed: bool):
        print('[CMD] Grabber', 'closed' if closed else 'open')
        if self.autopilot.running:
            print('Autopilot is running, ignoring command.')
        else:
            self.controller.robotarm.set_grabber(closed)
