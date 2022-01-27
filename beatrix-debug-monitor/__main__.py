from PyQt5.QtWidgets import QApplication
from gui.mainwindow import MainWindow
from debugclient import DebugClient
from configfile import ConfigFile
from lib.kinematics import IkPyKinematics
from lib.logger import Logger
from lib.chain import beatrix_rep
import sys

logger = Logger()
config = ConfigFile(logger)
client = DebugClient(logger, config)
kinematics = IkPyKinematics(beatrix_rep)

# Connect to debug server.
client.connect()

# Create and start Qt5 based GUI.
app = QApplication(sys.argv)
window = MainWindow(client, kinematics, logger, config)
window.start()
window.show()
app.exec()

# Cleanup stuff
logger.log('Exiting application.')
client.stop()
config.save()

