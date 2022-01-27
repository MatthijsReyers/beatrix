from threading import Thread
import cv2

class Camera():
    def __init__(self, debug_server):
        self.debug_server = debug_server

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 2)

        self.running = False

    def start(self):
        self.running = True
        self.camera_thread = Thread(
            target=self.__camera_thread, 
            # daemon=True,
            args=())
        self.camera_thread.start()

    def stop(self):
        self.running = False
        if self.camera_thread != None:
            self.camera_thread.join()

    def __camera_thread(self):
        try:
            while self.running:
                okay, frame = self.cap.read()
                if okay:
                    self.debug_server.send_video_frame(frame)
        finally:
            self.cap.release()
    