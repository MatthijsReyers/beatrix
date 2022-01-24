from lib.clientsock import ClientSocket
from lib.logger import Logger
import pickle, cv2, json

VIDEO_BUFFER_SIZE = 1000000
VIDEO_PORT = 37020
CONTROL_PORT = 4400

RASP_IP = '127.0.0.1'
# RASP_IP = '192.168.23.211'

class DebugClient():
    def __init__(self, logger=None):
        self.control_socket = ClientSocket(RASP_IP, CONTROL_PORT)
        self.video_socket = ClientSocket(RASP_IP, VIDEO_PORT)

        self.logger = logger if logger != None else Logger()

    def start(self):
        logger.log('Connecting to control server.')
        self.control_socket.start()
        self.video_socket.start()

    def stop(self, event):
        logger.log('Exiting, closing sockets.')
        self.control_socket.close()
        self.video_socket.close()

    def is_connected(self):
        return self.control_socket.is_connected() and self.video_socket.is_connected()

    def recieve_video(self) -> (bool, any):
        okay, data = self.video_socket.receive(buffer_size=1000000)
        if okay:
            data = pickle.loads(data)
            return (True, cv2.imdecode(data, cv2.IMREAD_COLOR))
        return (False, None)
        
    def receive_command(self) -> (bool, object):
        """ Tries to receive a command from the server. """
        try:
            okay, cmd = self.control_socket.receive(buffer_size=1024*4)
            if okay:
                cmd = json.loads(cmd)
                if cmd['type'] != None: return (True, cmd)
                else:
                    self.logger.warn('Received invalid command')
        except Exception as e:
            self.logger.exception(e, 'DebugClient.receive_command')
        return (False, {})

    def send_set_position_cmd(self, position: (float, float, float)):
        """ Sends a command to set the position of the robot arm. """
        self._send_cmd({
            'type': 'SET_POSITION',
            'data': {
                'x': position[0],
                'y': position[1],
                'z': position[2]
            }
        })

    def send_get_position_cmd(self):
        """ Sends a command to get the current position of the robot arm. """
        self._send_cmd({
            'type': 'GET_POSITION',
            'data': {}
        })

    def send_go_home_cmd(self):
        """ Sends a command to move the robot arm to its home position. """
        self._send_cmd({
            'type': 'GO_HOME',
            'data': {}
        })

    def _send_cmd(self, cmd):
        try:
            packet = json.dumps(cmd)
            self.control_socket.send(packet)
        except Exception as e:
            self.logger.exception(e, 'DebugClient._send_cmd')