from lib.serversock import ServerSocket
from threading import Thread
import pickle, struct, cv2

VIDEO_BUFFER_SIZE = 1000000
VIDEO_PORT = 37020
CONTROL_PORT = 4400

class DebugServer():
    def __init__(self):
        self.video_socket = ServerSocket(VIDEO_PORT, buffer_size=VIDEO_BUFFER_SIZE)
        self.control_socket = ServerSocket(CONTROL_PORT)

    def start(self):
        self.video_socket.start()
        self.control_socket.start()

    def stop(self):
        self.video_socket.stop()
        self.control_socket.stop()

    def send_video_frame(self, frame):
        try:
            _, frame = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
            frame_bytes = pickle.dumps(frame)
            self.video_socket.send(frame_bytes)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    server = DebugServer()
    server.start()
    
    cam = cv2.VideoCapture(0)
    
    try:
        while(True):
            okay, frame = cam.read()
            if okay:
                server.send_video_frame(frame)
        cam.release()
    finally:
        server.stop()