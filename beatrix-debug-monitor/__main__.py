from gui.mainwindow import MainWindow
from debugclient import DebugClient
import ikpy, gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

client = DebugClient()
client.connect()

def stopapp():
    """ This function is responsible for propagating the stop signal to the various modules and threads 
    of the application. """
    logger.log('Exiting application.')
    client.stop()

window = MainWindow(client)
window.connect("destroy", stopapp)
window.connect("destroy", Gtk.main_quit)
window.show_all()
window.start()
Gtk.main()
