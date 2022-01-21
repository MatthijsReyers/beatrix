from mainwindow import MainWindow
from debugclient import DebugClient
import ikpy, gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

client = DebugClient()
client.connect()

window = MainWindow(client)
window.connect("destroy", Gtk.main_quit)
window.show_all()
window.start()
Gtk.main()