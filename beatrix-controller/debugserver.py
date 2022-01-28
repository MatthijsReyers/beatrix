from lib.constants import VIDEO_PORT, CONTROL_PORT, VIDEO_BUFFER_SIZE
from lib.serversock import ServerSocket
from threading import Thread
from pickle import UnpicklingError
import pickle, struct, cv2

class DebugServer():
    def __init__(self):
        self.video_socket = ServerSocket(VIDEO_PORT, buffer_size=VIDEO_BUFFER_SIZE)
        self.control_socket = ServerSocket(CONTROL_PORT)

    def start(self, command_handler):
        self.video_socket.start()
        self.control_socket.start()
        self.control_socket.on_receive(command_handler.exec_cmd)

    def stop(self):
        self.video_socket.stop()
        self.control_socket.stop()

    def send_video_frame(self, frame):
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
        try:
            data = json.dumps(cmd).encode('utf-8')
            length = struct.pack('>I', len(data))
            self.control_socket.send(length+data)
        except Exception as e:
            print('Caught exception:')
            print(e)
