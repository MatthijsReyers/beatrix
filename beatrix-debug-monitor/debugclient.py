from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SO_SNDBUF, SOL_SOCKET
import pickle, cv2, json

VIDEO_BUFFER_SIZE = 1000000
VIDEO_PORT = 37020
CONTROL_PORT = 4400

RASP_IP = '127.0.0.1'
# RASP_IP = '192.168.23.211'

class DebugClient():
    def __init__(self):
        self.control_socket = socket(AF_INET, SOCK_STREAM)

        self.video_socket = socket(AF_INET, SOCK_DGRAM)
        self.video_socket.bind(('', VIDEO_PORT))
        self.video_socket.settimeout(0.4)

        self.reconnecting = False

    def connect(self):
        print('[*] Connecting to control server')
        self.running = True
        self.__reconnect()

    def stop(self, event):
        print('[*] Exiting, closing sockets.')
        self.running = False
        self.control_socket.close()

    def is_connected(self):
        return self.control_socket and (self.control_socket.fileno() != -1)

    def recieve_video(self):
        data, addr = self.video_socket.recvfrom(VIDEO_BUFFER_SIZE)
        data = pickle.loads(data)
        return cv2.imdecode(data, cv2.IMREAD_COLOR)
        
    def recieve_command(self):
        try:
            cmd = self.control_socket.recv(1024*4)
            cmd = json.loads(cmd)
            if cmd['type'] != None:
                return cmd
            else:
                print('Received invalid command')
                return {}

        except Exception as e:
            print(e)

    def send_set_position_cmd(self, position: (float, float, float)):
        """ Sends a command to set the position of the robot arm. """
        self.__send_cmd({
            'type': 'SET_POSITION',
            'data': {
                'x': position[0],
                'y': position[1],
                'z': position[2]
            }
        })

    def send_get_position_cmd(self):
        """ Sends a command to get the current position of the robot arm. """
        self.__send_cmd({
            'type': 'GET_POSITION',
            'data': {}
        })

    def send_go_home_cmd(self):
        """ Sends a command to move the robot arm to its home position. """
        self.__send_cmd({
            'type': 'GO_HOME',
            'data': {}
        })

    def __send_cmd(self, cmd):
        try:
            packet = json.dumps(cmd)
            self.control_socket.send(packet)
        except Exception as e:
            print(e)

    def __reconnect(self):
        if not self.reconnecting:
            while self.running and not self.is_connected():
                self.reconnecting = True
                try:
                    self.control_socket = socket(AF_INET, SOCK_STREAM)
                    self.control_socket.connect((RASP_IP, CONTROL_PORT))
                    print('fileno:', self.control_socket.fileno())
                    self.reconnecting = False

                except Exception as e:
                    print('Caught exception:')
                    print(self.control_socket.fileno())
                    print(e)

            self.reconnecting = False


# if __name__ == '__main__':
    
#     client = SocketClient()
#     client.start()

#     while True:
#         frame = client.recieve_video()
#         cv2.imshow('server', frame)
#         if cv2.waitKey(10) == 13:
#             exit(0)