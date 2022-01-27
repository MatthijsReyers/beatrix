from lib.constants import *
from gui.position import PositionManager
from gui.visualizer import Visualizer
from gui.camerafeed import CameraFeed
from gui.topbar import TopBar
from threading import Thread
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QLabel, QSlider, QPushButton)
import math

class MainWindow(QMainWindow):
    def __init__(self, client, kinematics, logger, config):
        super(QMainWindow, self).__init__()
        self.setWindowTitle("Beatrix debug monitor")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        self.central_widget.setLayout(self.layout)
        
        self.logger = logger
        self.config = config
        self.client = client
        self.kinematics = kinematics

        self.topbar = TopBar(client, config)
        self.layout.addWidget(self.topbar)

        # Splitter with resizeable things.
        self.splitter = QSplitter()
        self.splitter.setOrientation(Qt.Orientation.Vertical)
        self.layout.addWidget(self.splitter)

        # Main bar with visualizer and camera feed.
        # ===========================================================
        main_bar = QSplitter()
        self.camera_feed = CameraFeed(client, logger)
        main_bar.addWidget(self.camera_feed)
        self.visualizer = Visualizer()
        main_bar.addWidget(self.visualizer)
        self.splitter.addWidget(main_bar)

        # Second bar with logs and position options
        # ===========================================================
        base_splitter = QSplitter()
        self.splitter.addWidget(base_splitter)

        button_row = QWidget()
        layout = QVBoxLayout(button_row)
        base_splitter.addWidget(button_row)  
        
        btn = QPushButton("Set position")
        btn.clicked.connect(self.__on_send_angles)
        layout.addWidget(btn)

        btn = QPushButton("Go home")
        btn.clicked.connect(self.__on_go_home)
        layout.addWidget(btn)

        self.position_manager = PositionManager(kinematics)
        self.position_manager.on_position_change(self.visualizer.update_position)
        self.position_manager.on_angles_change(self.visualizer.update_angles)
        base_splitter.addWidget(self.position_manager)  


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

    def __command_thread(self):
        print('[*] Started command thread.')

    def __on_send_angles(self):
        print('[*] Sending set angles')
        angles = self.position_manager.angles
        self.client.send_set_angles_cmd({
            BASE_JOINT_ID:       math.degrees(angles[1]),
            SHOULDER_JOINT_ID:   math.degrees(angles[2]),
            ELBOW_JOINT_ID:      math.degrees(angles[3]),
            WRIST_JOINT_ID:      math.degrees(angles[4]),
            WRIST_TURN_JOINT_ID: math.degrees(angles[5]),
        })
    
    def __on_go_home(self):
        print('[*] Sending go home')
        self.position_manager.set_home()
        self.client.send_go_home_cmd()