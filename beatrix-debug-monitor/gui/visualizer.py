from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QBoxLayout, QGroupBox
from lib.constants import *
from lib.chain import beatrix_rep
from typing import Tuple
from math import radians

class Visualizer(QGroupBox):
    def __init__(self, title: str):
        super(QGroupBox, self).__init__()
        self.setTitle(title)
        self.layout = QBoxLayout(QBoxLayout.Direction.Up, self)

        self.position = [0.0, 0.0, 0.0]
        self.angles   = INITIAL_ANGLES

        self.chain  = beatrix_rep
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')

        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.update_graph()

    def update_position(self, position: Tuple[float,float,float]):
        self.position = position
        self.update_graph()

    def update_angles(self, angles:dict):
        self.angles = angles
        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        self.ax.set_zlim([0, 50])
        self.ax.set_xlim([-50, 50])
        self.ax.set_ylim([-50, 50])

        self.chain.plot([
            0.0,
            radians(self.angles[BASE_JOINT_ID] - 90),
            radians(self.angles[SHOULDER_JOINT_ID]),
            radians(self.angles[ELBOW_JOINT_ID]),
            radians(self.angles[WRIST_JOINT_ID]),
            radians(self.angles[WRIST_TURN_JOINT_ID]),
            0.0,
        ], self.ax)

        self.ax.scatter(
            self.position[0], self.position[1], self.position[2],
            marker="x", c="red")

        self.canvas.draw()
