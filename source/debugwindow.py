import ikpy, gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DebugWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Beatrix debug info")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(600,600)
