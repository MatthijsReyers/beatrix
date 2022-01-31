from lib.constants import *
from lib.commands import *
from lib.locations import LOCATIONS_FOR_GUI
from gui.position import PositionManager
from gui.visualizer import Visualizer
from gui.camerafeed import CameraFeed
from gui.topbar import TopBar
from threading import Thread
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QMainWindow, QGroupBox, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, 
    QLabel, QSlider, QPushButton)
import math, time

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
        self.local_visualizer = Visualizer('Local position')
        main_bar.addWidget(self.local_visualizer)
        self.splitter.addWidget(main_bar)
        self.real_visualizer = Visualizer('Remote position')
        main_bar.addWidget(self.real_visualizer)
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

        btn = QPushButton("Get position")
        btn.clicked.connect(self.__on_get_angles)
        layout.addWidget(btn)

        btn = QPushButton("Go home")
        btn.clicked.connect(self.__on_go_home)
        layout.addWidget(btn)

        btn = QPushButton("Close grabber")
        btn.clicked.connect(self.__on_set_grabber(closed=True))
        layout.addWidget(btn)

        btn = QPushButton("Open grabber")
        btn.clicked.connect(self.__on_set_grabber(closed=False))
        layout.addWidget(btn)

        self.position_manager = PositionManager(kinematics)
        self.position_manager.on_position_change(self.local_visualizer.update_position)
        self.position_manager.on_angles_change(self.local_visualizer.update_angles)
        base_splitter.addWidget(self.position_manager)  

        # Autopilot control options box.
        # ===========================================================
        autopilot = QGroupBox()
        autopilot.setTitle('Autopilot state:')
        layout = QVBoxLayout(autopilot)
        self.autopilot_state = QLabel('Stopped')
        layout.addWidget(self.autopilot_state)
        btn = QPushButton('Start')
        btn.clicked.connect(self.__on_set_autopilot(enabled=True))
        layout.addWidget(btn)
        btn = QPushButton('Stop')
        btn.clicked.connect(self.__on_set_autopilot(enabled=False))
        layout.addWidget(btn)
        base_splitter.addWidget(autopilot)  

        # Locations move thing.
        # ===========================================================
        locations = QGroupBox()
        locations.setTitle('Go to location:')
        layout = QVBoxLayout(locations)
        for location in LOCATIONS_FOR_GUI:
            btn = QPushButton(location.name)
            btn.clicked.connect(self.__on_move_location(location))
            layout.addWidget(btn)
        base_splitter.addWidget(locations)  


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
        while self.running:
            (okay, cmd) = self.client.receive_command()
            if okay:
                cmd_type = cmd['type']
                if cmd_type == GET_UPDATE:
                    self.__handle_update(cmd['data'])
            else:
                time.sleep(0.1)

    def __handle_update(self, update):
        if 'angles' in update:
            self.real_visualizer.update_angles(update['angles'])
            pos = self.position_manager.kinematics.get_forward_cartesian(update['angles'])
            self.real_visualizer.update_position(pos)
        if 'autopilot' in update:
            self.autopilot_state.setText(update['autopilot'])

    def __on_move_location(self, location):
        def move():
            print('[*] Sending goto:', location.name)
            angles = location.get_angle_dict()
            self.client.send_set_angles(angles)
            self.position_manager.set_angles(angles)
        return move

    def __on_send_angles(self):
        print('[*] Sending set angles')
        angles = self.position_manager.angles
        self.client.send_set_angles(angles)
    
    def __on_get_angles(self):
        self.client.send_get_update()
        angles = self.real_visualizer.angles
        self.position_manager.set_angles(angles.copy())
        self.local_visualizer.update_angles(angles.copy())

    def __on_go_home(self):
        print('[*] Sending go home')
        self.position_manager.set_angles(INITIAL_ANGLES.copy())
        self.local_visualizer.update_angles(INITIAL_ANGLES.copy())
        self.client.send_set_angles(INITIAL_ANGLES)

    def __on_set_grabber(self, closed):
        def send():
            self.client.send_set_grabber(closed=closed)
        return send

    def __on_set_autopilot(self, enabled):
        def send():
            self.client.send_set_autopilot(enabled=enabled)
        return send