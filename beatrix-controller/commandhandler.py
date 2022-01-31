from typing import Tuple
from controller import Controller
from autopilot import AutoPilot
from debugserver import DebugServer
from lib.constants import INITIAL_ANGLES
import lib.commands as cmd
import json

class CommandHandler:
    def __init__(self, server, controller: Controller, autopilot: AutoPilot):
        self.controller = controller
        self.autopilot = autopilot
        self.server = server

        self.command_funcs = {
            cmd.GET_UPDATE: self._cmd_get_update,
            cmd.SET_POSITION: self._cmd_set_pos,
            cmd.SET_ANGLES: self._cmd_set_ang,
            cmd.SET_GRABBER: self._cmd_grabber,
            cmd.SET_AUTOPILOT: self._cmd_autopilot,
        }

    def exec_cmd(self, cmd: bytes, client: Tuple[str,int]):
        """ Parses and executes a debug controller command. """
        try:
            cmd = cmd.decode('utf-8')
            cmd = json.loads(cmd)
            cmd_type = cmd['type']
            print(cmd)
            if cmd_type in self.command_funcs:
                func = self.command_funcs[cmd['type']]
                func(**cmd['data'])
            else:
                print('Received invalid command:', cmd)
        except Exception as e:
            print('Caught exception when parsing command:', type(e), '\n', e)

    def NoRunningAutopilot(func):
        """ Decorator that prevents the executing of command handler functions when the autopilot is 
        currently running. """
        def decorator(*args, **kwargs):
            if args[0].autopilot.is_running():
                print('[!] Autopilot is running, ignoring command.')
            else:
                func(*args, **kwargs)
        return decorator

    # @NoRunningAutopilot
    # def _cmd_home(self):
    #     print('[CMD] Go home')
    #     self.controller.robotarm.set_arm(INITIAL_ANGLES, 30)

    def _cmd_get_update(self):
        self.server.send_update(
            angles=self.controller.robotarm.get_current_angles(),
            autopilot_state=self.autopilot.state,
            # grabber=self.controller.robotarm
        )

    @NoRunningAutopilot
    def _cmd_set_pos(self, position: Tuple[float, float, float]):
        print('[CMD] Set position:', list(position))
        self.controller._move_arm_to_workspace_coordinate(position)

    @NoRunningAutopilot
    def _cmd_set_ang(self, angles: dict):
        print('[CMD] Set angles:', list(angles.values()))
        self.controller.robotarm.set_arm(angles, 30)

    @NoRunningAutopilot
    def _cmd_grabber(self, closed: bool):
        print('[CMD] Grabber', 'closed' if closed else 'open')
        self.controller.robotarm.set_grabber(closed)

    def _cmd_autopilot(self, enabled: bool):
        print('[CMD]', 'Start' if enabled else 'Stop', 'autopilot')
        if enabled: self.autopilot.start()
        else: self.autopilot.stop()
