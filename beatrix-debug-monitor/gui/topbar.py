from PyQt5.QtWidgets import (QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QButtonGroup, QRadioButton, QSpacerItem, QSizePolicy)
from PyQt5 import QtCore

LOCALHOST = 'Localhost'
RASPBERRY_PI = 'Raspberry Pi'

class TopBar(QGroupBox):
    def __init__(self, client, config):
        super(QGroupBox, self).__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMaximumHeight(40)
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.client = client
        self.config = config

        # self.setAttribute(WA_StyledBackground, True)
        # self.setStyleSheet("""
        #     background-color: red;
        # """)


        # Server source select
        # ===========================================================================
        self.source_select = QWidget()
        layout = QVBoxLayout(self.source_select)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        label = QLabel('Connect to:')
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumHeight(20)
        layout.addWidget(label)

        self.layout.addWidget(self.source_select)

        box = QWidget()
        layout2 = QHBoxLayout(box)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.setSpacing(0)
        layout.addWidget(box)

        self.local_btn = QRadioButton(LOCALHOST)
        self.remote_btn = QRadioButton(RASPBERRY_PI)

        self.local_btn.setChecked(self.config.local_server)
        self.remote_btn.setChecked(not self.config.local_server)

        self.local_btn.toggled.connect(self.__on_source_select(LOCALHOST))
        self.remote_btn.toggled.connect(self.__on_source_select(RASPBERRY_PI))

        buttons = QButtonGroup()
        buttons.setExclusive(True)
        buttons.addButton(self.local_btn, 1)
        buttons.addButton(self.remote_btn, 2)

        layout2.addWidget(self.local_btn)
        layout2.addWidget(self.remote_btn)


        # Raspberry pi IP address entry box
        # ===========================================================================
        self.ip_select = QWidget()
        self.ip_select.setVisible(not self.config.local_server)
        layout = QVBoxLayout(self.ip_select)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel('Raspberry Pi:')
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setMinimumHeight(20)
        layout.addWidget(label)

        box = QWidget()
        layout2 = QHBoxLayout(box)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        # box.setStyleSheet("""
        #     background-color: red;
        # """)
        layout.addWidget(box)
        
        self.ip = self.config.raspberry_ip
        ip_input = QLineEdit()
        ip_input.setText(self.ip)
        ip_input.setMinimumWidth(190)
        ip_input.setMinimumWidth(200)
        ip_input.textChanged.connect(self.__on_ip_entry)
        layout2.addWidget(ip_input)

        self.ip_btn = QPushButton('OK')
        self.ip_btn.clicked.connect(self.__on_ip_save)
        self.ip_btn.setEnabled(False)
        layout2.addWidget(self.ip_btn)
        
        self.layout.addWidget(self.ip_select)


        # Spacer to keep everything to the left.
        # ===========================================================================
        verticalSpacer = QSpacerItem(800, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(verticalSpacer)


        # Connection state text in the top right.
        # ===========================================================================
        self.connected_label = QLabel('Connecting...')
        self.layout.addWidget(self.connected_label)
        self.client.on_change(self.__on_connect)
        self.__on_connect(self.client.is_connected())

    def __on_source_select(self, btn_name):
        def select(state):
            local = (btn_name == LOCALHOST and state == True)

            if btn_name == RASPBERRY_PI and state:
                self.ip_select.setVisible(True)
            else: self.ip_select.setVisible(False)

            if self.config.local_server != local:
                self.config.local_server = local
                self.client.stop()
                self.client.connect()
        return select

    def __on_ip_entry(self, entry):
        self.ip = entry.replace(' ', '')
        self.ip_btn.setEnabled(not (self.ip == self.config.raspberry_ip))

    def __on_ip_save(self, x):
        self.config.raspberry_ip = self.ip
        if not self.config.local_server:
            self.client.stop()
            self.client.connect()
        self.ip_btn.setEnabled(False)

    def __on_connect(self, connected):
        if connected:
            self.connected_label.setText('Connected')
        else:
            self.connected_label.setText('Not connected')