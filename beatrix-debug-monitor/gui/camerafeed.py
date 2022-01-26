from PyQt5.QtWidgets import QLabel, QGroupBox, QBoxLayout
from PyQt5.QtGui import QPixmap
from threading import Thread
from pickle import UnpicklingError
from lib.utils import safe_import_cv
import time, qimage2ndarray 

cv2 = safe_import_cv()

class CameraFeed(QGroupBox):
    def __init__(self, client, logger):
        super(QGroupBox, self).__init__()
        self.setTitle("Camera feed")
        self.layout = QBoxLayout(QBoxLayout.Direction.Up)
        self.setLayout(self.layout)
        self.camera_image = QLabel('Camera stream not connected')
        self.layout.addWidget(self.camera_image)

        self.client = client
        self.logger = logger
        self.running = False

    def start(self):
        self.running = True
        self.camera_thread = Thread(target=self.__camera_thread, args=(), daemon=True)
        self.camera_thread.start()

    def stop(self):
        self.running = False
        self.camera_thread.join()

    def __camera_thread(self):
        print('[*] Started camera thread.')
        while self.running:
            try:
                okay, frame = self.client.receive_video()
                if okay:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    image = qimage2ndarray.array2qimage(frame)
                    self.camera_image.setPixmap(QPixmap.fromImage(image))
            except UnpicklingError as e:
                print(e)
            except Exception as e:
                self.logger.exception(e, 'CameraFeed.__camera_thread')
                time.sleep(0.8)