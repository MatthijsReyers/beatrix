from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SO_SNDBUF, SOL_SOCKET, \
    SO_BROADCAST, SO_REUSEPORT, AF_INET6
from threading import Thread
import pickle, struct, cv2

VIDEO_BUFFER_SIZE = 1000000
VIDEO_PORT = 37020
CONTROL_PORT = 4400

class DebugServer():
    def __init__(self):
        self.control_socket = socket(AF_INET, SOCK_STREAM)
        self.control_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.control_socket.bind(('', CONTROL_PORT))
        self.control_socket.settimeout(0.2)

        self.video_socket = socket(AF_INET, SOCK_DGRAM)
        self.video_socket.setsockopt(SOL_SOCKET, SO_SNDBUF,VIDEO_BUFFER_SIZE)

        self.conn_thread = None
        self.control_conns = dict()

        self.running = False
        self.video_thread = None
        self.sending_frame = False
        self.frame_counter = 0

    def stop(self):
        self.running = False

        # Close all socket connections.
        for conn in self.control_conns.values():
            conn.close()

        # Close all sockets
        self.control_socket.close()

    def start(self):
        self.running = True

        self.conn_thread = Thread(
            target=self.__connection_thread, 
            args=(self.control_socket, self.control_conns))   
        self.conn_thread.setDaemon(True)
        self.conn_thread.start()

    def __connection_thread(self, sock, conns):
        sock.listen(10)
        while self.running:
            try:
                # Accept incomming connections.
                conn, addr = sock.accept()
                # Close old connections if we already had them.
                if addr in conns:
                    conns[addr].close()
                conns[addr] = conn
                print(f'[*] Opened connection from: {addr}')
            except: pass

    def send_video_frame(self, frame):
        if not self.sending_frame:
            self.sending_frame = True
            if self.video_thread:
                self.video_thread.join()
            self.video_thread = Thread(target=self.__sending_thread, args=(frame,))
            self.video_thread.start()

    def __sending_thread(self, frame):
        _, frame = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        frame_bytes = pickle.dumps(frame)
        for (ip, _) in self.control_conns.keys():
            self.video_socket.sendto(frame_bytes, (ip, VIDEO_PORT))
        self.sending_frame = False






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
        server.control_socket.close()