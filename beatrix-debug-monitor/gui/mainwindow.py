from lib.constants import HOME_POSITION
from gui.visualizer import Visualizer
from gui.camerafeed import CameraFeed
from gui.topbar import TopBar
from threading import Thread
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QLabel, QSlider)

class MainWindow(QMainWindow):
    def __init__(self, client, logger, config):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Beatrix debug monitor")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.central_widget.setLayout(self.layout)
        
        self.position = [40.0, 0.0, 10.0]

        self.logger = logger
        self.config = config
        self.client = client

        self.topbar = TopBar(client, config)
        self.layout.addWidget(self.topbar)

        # Splitter with resizeable things.
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.layout.addWidget(self.splitter)

        # Main bar with visualizer and camera feed.
        main_bar = QSplitter()
        self.camera_feed = CameraFeed(client, logger)
        main_bar.addWidget(self.camera_feed)
        self.visualizer = Visualizer()
        self.visualizer.update_position(self.position)
        main_bar.addWidget(self.visualizer)
        self.splitter.addWidget(main_bar)

        # Second bar with logs and position options
        base_splitter = QSplitter()
        self.splitter.addWidget(base_splitter)

        self.__init_position_frame()
        base_splitter.addWidget(self.position_frame)  
        self.update_position(self.position)      

        # self.box.add(v_bar)

        # # self.__init_position_frame()
        
        # # self.angles = [45,45,45,45,45,45]
        # # self.__init_angles_frame()

        # # self.grid = Gtk.Grid()
        # # self.grid.set_vexpand(True)
        # # self.grid.set_hexpand(True)
        # # self.add(self.grid)
        # self.connect('destroy', self.stop)
        # # self.update_position(self.position)

    def start(self):
        self.running = True
        self.camera_feed.start()
        self.command_thread = Thread(target=self.__command_thread, args=(), daemon=True)
        self.command_thread.start()

    def stop(self, event):
        print('[*] Exiting, joining threads.')
        self.running = False
        self.camera_feed.stop()
        self.command_thread.join()

    def update_position(self, position):
        self.position = position
        self.visualizer.update_position(position)
        for i in range(3):
            self.position_sliders[i].setValue(position[i])

    def __init_position_frame(self):
        self.position_frame = QGroupBox()
        self.position_frame.setTitle("Position")

        self.position_sliders = []

        sliders = QHBoxLayout(self.position_frame)
        # sliders.set_orientation(Gtk.Orientation.VERTICAL)

        for axis in range(3):
            slider = QSlider(Qt.Orientation.Horizontal, self.position_frame)
            slider.setMinimum(-50)
            slider.setMaximum(50)
            slider.valueChanged.connect(self.__on_slider_move(axis))
            sliders.addWidget(slider)
            self.position_sliders.append(slider)
        

    def __init_angles_frame(self):
        pass

    def __command_thread(self):
        print('[*] Started command thread.')

    def __on_slider_move(self, axis):
        def update(value):
            self.position[axis] = value
            self.update_position(self.position)
        return update

    def __on_go_home(self):
        self.update_position(HOME_POSITION)
        self.send_go_home_cmd()
