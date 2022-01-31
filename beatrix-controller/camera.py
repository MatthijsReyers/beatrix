from threading import Thread
import cv2
import objectrecognition

class Camera():
    def __init__(self, debug_server):
        self.debug_server = debug_server

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 2)

        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1088)
        # self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

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
                    self.__frame = frame
        finally:
            self.cap.release()


    # def __camera_thread(self):
    #     try:
    #         while self.running:
    #             okay, frame = self.cap.read()
    #             print("while camera thread okay = {}".format(okay))
    #             if okay:
    #                 objects = objectrecognition.object_recognition(frame)
    #                 objectrecognition.draw_on_image(frame, objects)
    #                 height, width, channels = frame.shape
    #                 frame = cv2.resize(frame, dsize=(int(width * 0.5), int(height * 0.5)),
    #                                    interpolation=cv2.INTER_AREA)
    #                 self.debug_server.send_video_frame(frame)
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         self.cap.release()

    def get_latest_frame(self):
        return self.__frame
    