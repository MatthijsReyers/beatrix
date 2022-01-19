from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
import ikpy, gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class DebugWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Beatrix debug info")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(1200,800)
        
        self.grid = Gtk.Grid()
        self.grid.set_vexpand(True)
        self.grid.set_hexpand(True)
        self.add(self.grid)

        figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = figure.add_subplot(111, projection='3d')
        self.canvas = FigureCanvas(figure)
        self.canvas.set_size_request(400, 300)
        self.canvas.set_vexpand(True)

        self.visualizer_frame = Gtk.Frame()
        self.visualizer_frame.set_label("Visualizer")
        self.visualizer_frame.set_size_request(400, 100)
        self.visualizer_frame.set_hexpand(True)
        self.visualizer_frame.add(self.canvas)
        self.grid.attach(self.visualizer_frame, 4, 0, 3, 1)

        self.position_frame = Gtk.Frame()
        self.position_frame.set_label("Position")
        self.position_frame.set_vexpand(True)
        self._init_position_frame()
        self.grid.attach(self.position_frame, 4, 4, 1, 1)

        self.camera_frame = Gtk.Frame()
        self.camera_frame.set_label("Camera feed")
        self.camera_frame.set_size_request(400, 300)
        self.camera_frame.set_hexpand(True)
        self.grid.attach(self.camera_frame, 0, 0, 3, 1)

    def _init_position_frame(self):
        scales = Gtk.Box(spacing=6)
        scales.set_orientation(Gtk.Orientation.VERTICAL)

        for axis in range(3):
            scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -5, 5, 0.1)
            scale.set_value_pos(Gtk.PositionType.RIGHT)
            scale.set_hexpand(True)
            scale.set_has_origin(False)
            scale.set_value_pos(0.0)
            scales.add(scale)

        scales_frame = Gtk.Frame()
        scales_frame.add(scales)
        self.position_frame.add(scales_frame)

    def _on_position_update(self, axis):
        pass