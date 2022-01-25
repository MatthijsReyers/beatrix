from lib.consts import VIDEO_BUFFER_SIZE, VIDEO_PORT, CONTROL_PORT
from lib.clientsock import ClientSocket
import pickle, cv2, json, struct, time

FRAME_TIMEOUT = 2

class DebugClient():
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

    def connect(self):
        self.logger.log('Connecting to control server.')
        ip = '127.0.0.1' if self.config.local_server else self.config.raspberry_ip
        self.control_socket = ClientSocket(ip, CONTROL_PORT)
        self.video_socket = ClientSocket(ip, VIDEO_PORT)
        self.control_socket.start()
        self.video_socket.start()

    def stop(self):
        self.logger.log('Exiting, closing sockets.')
        self.control_socket.stop()
        self.video_socket.stop()

    def is_connected(self):
        return self.control_socket.is_connected() and self.video_socket.is_connected()

    def recieve_video(self) -> (bool, any):
        start_t = time.time()
        okay, raw_size = self.video_socket.receive(buffer_size=4)
        if okay:
            frame_size = struct.unpack('>I', raw_size)[0]
            frame = b""
            print(frame_size)
            while len(frame) < frame_size and abs(start_t - time.time()) < FRAME_TIMEOUT:
                okay, data = self.video_socket.receive(buffer_size=frame_size-len(frame))
                frame += data
            if len(frame) < frame_size:
                print('frame timed out')
                return (False, None)
            data = pickle.loads(frame)
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