from typing import Tuple
from controller import Controller
from autopilot import AutoPilot
from debugserver import DebugServer
import lib.commands as cmd
import json

class CommandHandler:
    def __init__(self, server: DebugServer, controller: Controller, autopilot: AutoPilot):
        self.controller = controller
        self.autopilot = autopilot
        self.server = server
        self.command_funcs = {
            cmd.TAKE_PICTURE: self._cmd_take_picture,
            cmd.GET_UPDATE: self._cmd_get_update,
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

    def _cmd_take_picture(self):
        """ Called to execute a TAKE_PICTURE command, saves the latest camera frame to the /pix folder as a 
        jpg encoded file. """
        print('[CMD] Take picture')
        self.controller.camera.save_frame()

    def _cmd_get_update(self):
        """ Called to execute a GET_UPDATE command, gets the current controller state and sends it back 
        to all connected debug clients. """
        print('[CMD] Get update. ')
        self.server.send_update(
            angles=self.controller.robotarm.get_current_angles(),
            autopilot_state=self.autopilot.state,
            # grabber=self.controller.robotarm
        )

    @NoRunningAutopilot
    def _cmd_set_ang(self, angles: dict):
        """ Called to execute a SET_ANGLES command, sets the angles of the servo motors. """
        print('[CMD] Set angles:', list(angles.values()))
        self.controller.robotarm.set_arm(angles, 30)

    @NoRunningAutopilot
    def _cmd_grabber(self, closed: bool):
        """" Called to execute a SET_GRABBER command, opens or closes the grabber. """
        print('[CMD] Grabber', 'closed' if closed else 'open')
        self.controller.robotarm.set_grabber(closed)

    def _cmd_autopilot(self, enabled: bool):
        """ Called to execute a SET_AUTOPILOT command, enabled or disabled the autopilot and blocks 
        until the state change has finished. """
        print('[CMD]', 'Start' if enabled else 'Stop', 'autopilot')
        if enabled: self.autopilot.start()
        else: self.autopilot.stop()
