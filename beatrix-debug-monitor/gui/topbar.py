from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QButtonGroup, QRadioButton, QSpacerItem, QSizePolicy)

LOCALHOST = 'Localhost'
RASPBERRY_PI = 'Raspberry Pi'

class TopBar(QWidget):
    def __init__(self, client, config):
        super(QWidget, self).__init__()
        self.layout = QHBoxLayout(self)

        self.client = client
        self.config = config


        # Server source select
        # ===========================================================================
        self.source_select = QWidget()
        layout = QVBoxLayout(self.source_select)
        layout.addWidget(QLabel('Connect to:'))
        self.layout.addWidget(self.source_select)

        box = QWidget()
        layout2 = QHBoxLayout(box)
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
        layout.addWidget(QLabel('Raspberry Pi:'))

        box = QWidget()
        layout2 = QHBoxLayout(box)
        layout.addWidget(box)
        
        self.ip = self.config.raspberry_ip
        ip_input = QLineEdit()
        ip_input.setText(self.ip)
        ip_input.textChanged.connect(self.__on_ip_entry)
        layout2.addWidget(ip_input)

        self.ip_btn = QPushButton('OK')
        self.ip_btn.clicked.connect(self.__on_ip_save)
        self.ip_btn.setEnabled(False)
        layout2.addWidget(self.ip_btn)
        
        self.layout.addWidget(self.ip_select)


        # Spacer to keep everything to the left.
        # ===========================================================================
        verticalSpacer = QSpacerItem(300, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(verticalSpacer)


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