from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
from matplotlib.figure import Figure
from ikpy.chain import Chain
import gi, cv2

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

class Visualizer(Gtk.Frame):
    def __init__(self):
        super().__init__()
        self.set_label("Visualizer")
        self.set_size_request(400, 100)
        self.set_hexpand(True)

        self.position = (5.0, 5.0, 5.0)

        # Load robot arm chain from URDF file.
        self.chain = Chain.from_urdf_file("./robot.URDF")
        solution = self.chain.inverse_kinematics(self.position)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.chain.plot(solution, self.ax)
        
        self.canvas = FigureCanvas(self.figure)
        self.canvas.set_size_request(400, 300)
        self.canvas.set_vexpand(True)
        self.add(self.canvas)

        self.update_graph()

    def update_position(self, position: (float, float, float)):
        self.position = position
        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        self.ax.set_zlim([0,50])
        self.ax.set_xlim([-50,50])
        self.ax.set_ylim([-50,50])

        solution = self.chain.inverse_kinematics(self.position)
        self.chain.plot(solution, self.ax)
        
        self.ax.scatter(
            self.position[0], self.position[1], self.position[2], 
            marker="x", c="red")

        self.canvas.draw()