from typing import Tuple, Union
from lib.constants import VIDEO_BUFFER_SIZE, VIDEO_PORT, CONTROL_PORT
from lib.clientsock import ClientSocket
from lib.utils import safe_import_cv
import lib.commands as cmd
import pickle, json, struct, time

cv2 = safe_import_cv()

FRAME_TIMEOUT = 2
CMD_TIMEOUT = 1.5

class DebugClient():
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self._callbacks = []

    def connect(self):
        self.logger.log('Connecting to control server.')
        ip = '127.0.0.1' if self.config.local_server else self.config.raspberry_ip
        self.control_socket = ClientSocket(ip, CONTROL_PORT)
        self.video_socket = ClientSocket(ip, VIDEO_PORT)
        self.control_socket.on_change(self._change_connection_state)
        self.video_socket.on_change(self._change_connection_state)
        self.control_socket.start()
        self.video_socket.start()

    def stop(self):
        self.logger.log('Exiting, closing sockets.')
        self.control_socket.stop()
        self.video_socket.stop()

    def is_connected(self):
        return self.control_socket.is_connected() and self.video_socket.is_connected()

    def on_change(self, callback):
        self._callbacks.append(callback)

    def receive_video(self) -> Tuple[bool, any]:
        start_t = time.time()
        okay, raw_size = self.video_socket.receive(buffer_size=4)
        if okay:
            frame_size = struct.unpack('>I', raw_size)[0]
            frame = b""
            while len(frame) < frame_size and abs(start_t - time.time()) < FRAME_TIMEOUT:
                okay, data = self.video_socket.receive(buffer_size=frame_size-len(frame))
                if okay:
                    frame += data
            if len(frame) < frame_size:
                self.logger.warn('Video frame receiving timed out.')
                return (False, None)
            data = pickle.loads(frame)
            return (True, cv2.imdecode(data, cv2.IMREAD_COLOR))
        else:
            time.sleep(0.1)
        return (False, None)

    def receive_command(self) -> Tuple[bool, Union[dict, None]]:
        """ Tries to receive a command from the server. """
        try:
            start_t = time.time()
            okay, raw_size = self.control_socket.receive(buffer_size=4)
            if okay:
                cmd_size = struct.unpack('>I', raw_size)[0]
                cmd = b""
                while len(cmd) < cmd_size and abs(start_t - time.time()) < CMD_TIMEOUT:
                    okay, data = self.control_socket.receive(buffer_size=cmd_size-len(cmd))
                    if okay:
                        cmd += data
                if len(cmd) < cmd_size:
                    self.logger.warn('Command receiving timed out.')
                    return (False, None)
                return (True, json.loads(cmd))
        except Exception as e:
            self.logger.exception(e, 'DebugClient.receive_command')
        return (False, None)

    def send_get_update(self):
        """ Sends a command to get the current position of the robot arm. """
        self._send_cmd({
            'type': cmd.GET_UPDATE,
            'data': {}
        })

    def send_set_angles(self, angles:dict):
        """ Sends a command to set the servo angles of the robotarm. """
        self._send_cmd({
            'type': cmd.SET_ANGLES,
            'data': {
                'angles': angles
            }
        })

    def send_set_position(self, position: Tuple[float, float, float]):
        """ Sends a command to set the position of the robot arm. """
        self._send_cmd({
            'type': cmd.SET_POSITION,
            'data': {
                'x': position[0],
                'y': position[1],
                'z': position[2]
            }
        })

    def send_set_grabber(self, closed: bool):
        """ Sets the state of the grabber """
        self._send_cmd({
            'type': cmd.SET_GRABBER,
            'data': {
                'closed':closed
            }
        })

    def send_set_autopilot(self, enabled: bool):
        self._send_cmd({
            'type': cmd.SET_AUTOPILOT,
            'data': {
                'enabled':enabled
            }
        })

    def _send_cmd(self, cmd):
        try:
            packet = json.dumps(cmd).encode('utf-8')
            self.control_socket.send(packet)
        except Exception as e:
            self.logger.exception(e, 'DebugClient._send_cmd')

    def _change_connection_state(self, socket, connected):
        if socket == self.control_socket and connected:
            self.send_get_update()
        for callback in self._callbacks:
            callback(self.is_connected())
