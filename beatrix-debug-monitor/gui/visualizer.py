from PyQt5.QtWidgets import QLabel, QGroupBox, QBoxLayout
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from lib.constants import HOME_POSITION, HOME_ANGLES
from lib.chain import ik_chain
from ikpy.chain import Chain

class Visualizer(QGroupBox):
    def __init__(self):
        super(QGroupBox, self).__init__()
        self.setTitle("Visualizer")
        self.layout = QBoxLayout(QBoxLayout.Direction.Up, self)

        self.position = HOME_POSITION
        self.angles   = HOME_ANGLES
        
        self.chain  = ik_chain
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.update_graph()

    def update_position(self, position):
        self.position = position
        self.update_graph()

    def update_angles(self, angles):
        self.angles = angles
        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        self.ax.set_zlim([0,50])
        self.ax.set_xlim([-50,50])
        self.ax.set_ylim([-50,50])

        self.chain.plot(self.angles, self.ax)

        self.ax.scatter(
            self.position[0], self.position[1], self.position[2], 
            marker="x", c="red")

        self.canvas.draw()
