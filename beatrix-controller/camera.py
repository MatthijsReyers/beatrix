from threading import Thread
import cv2
import objectrecognition
import time

class Camera():
    def __init__(self, debug_server):
        self.debug_server = debug_server

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # 1 is manual, 3 is auto
        self.cap.set(cv2.CAP_PROP_EXPOSURE, 250)

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
                okay, frame = self.cap.read()
                if okay:
                    self.__frame = frame.copy()
                    frame = cv2.resize(frame, dsize=(int(640), int(480)),interpolation=cv2.INTER_AREA)
                    self.debug_server.send_video_frame(frame)
                    time.sleep(0.5)

        finally:
            self.cap.release()

    def get_latest_frame(self):
        frame = self.__frame
        self.__frame = None
        return frame
    
    def save_frame(self):
        frame = self.__frame
        cv2.imwrite(f'pix/{time.time()}.jpg', frame)
