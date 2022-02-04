from lib.constants import VIDEO_PORT, CONTROL_PORT, VIDEO_BUFFER_SIZE
from lib.serversock import ServerSocket
import lib.commands as cmd
from pickle import UnpicklingError
import pickle, struct, cv2, json

class DebugServer():
    def __init__(self):
        self.video_socket = ServerSocket(VIDEO_PORT, buffer_size=VIDEO_BUFFER_SIZE)
        self.control_socket = ServerSocket(CONTROL_PORT)

    def start(self, command_handler):
        """ Starts all threads required for debug server and opens required sockets. """
        self.video_socket.start()
        self.control_socket.start()
        self.control_socket.on_receive(command_handler.exec_cmd)

    def stop(self):
        """ Stops and joins all debug server threads and gracefully closes all sockets. """
        self.video_socket.stop()
        self.control_socket.stop()

    def send_video_frame(self, frame):
        """ Encodes and sends a cv2 image frame back to all connected clients' video feeds. """
        try:
            _, frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            frame_bytes = pickle.dumps(frame)
            length = struct.pack('>I', len(frame_bytes))
            self.video_socket.send(length+frame_bytes)
        except UnpicklingError as e:
            print('Video decode error.')
        except Exception as e:
            print(e)

    def send_command(self, cmd):
        """ Sends a command back to all the connected debug clients. """
        try:
            data = json.dumps(cmd).encode('utf-8')
            length = struct.pack('>I', len(data))
            self.control_socket.send(length+data)
        except Exception as e:
            print('Caught exception:')
            print(e)

    def send_update(self, angles:dict=None, autopilot_state:str=None, grabber:bool=None):
        """ Sends an update of the current controller state to all the connected debug clients, all 
        parameters are optional and only for the provided parameters an update will be sent.

        Args:
            angles: Angle ID to degrees dictionary as used everywhere else in the codebase
            autopilot_state: String representing the current state of the autopilot (on,off,etc.)
            grabber: Boolean representing the open/closed state of the grabber, True for closed
         """
        data = dict()
        if angles != None: 
            data['angles'] = angles
        if autopilot_state != None:
            data['autopilot'] = str(autopilot_state)
        if grabber != None:
            data['grabber'] = grabber
        self.send_command({
            'type': cmd.GET_UPDATE,
            'data': data
        })