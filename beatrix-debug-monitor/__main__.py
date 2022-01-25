from gui.mainwindow import MainWindow
from debugclient import DebugClient
from configfile import ConfigFile
from lib.logger import Logger
import ikpy, gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

logger = Logger()
config = ConfigFile(logger)
client = DebugClient(logger, config)
window = MainWindow(client, logger, config)

def stopapp(event):
    """ This function is responsible for propagating the stop signal to the various modules and threads 
    of the application. """
    logger.log('Exiting application.')
    client.stop()
    config.save()

# Connect to debug server.
client.connect()

# Start Gtk3 GUI.
window.connect("destroy", Gtk.main_quit)
window.connect("destroy", stopapp)
window.show_all()
window.start()
Gtk.main()
