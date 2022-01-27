from PyQt5.QtWidgets import QLabel, QGroupBox, QBoxLayout
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from lib.constants import HOME_POSITION, HOME_ANGLES
import numpy as np
from math import pi, radians, degrees
from ikpy.link import OriginLink, URDFLink
from lib.chain import beatrix_rep

from ikpy.chain import Chain


class Visualizer(QGroupBox):
    def __init__(self):
        super(QGroupBox, self).__init__()
        self.setTitle("Visualizer")
        self.layout = QBoxLayout(QBoxLayout.Direction.Up, self)

        self.position = (5.0, 5.0, 5.0)

        self.figure = Figure(figsize=(10, 10), dpi=100)
        self.position = HOME_POSITION
        self.angles   = HOME_ANGLES

        self.chain  = beatrix_rep
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
        self.ax.set_zlim([0, 50])
        self.ax.set_xlim([-50, 50])
        self.ax.set_ylim([-50, 50])

        zeroes = np.array([0, 0, radians(90), radians(10), radians(88), 0])
        test1 = np.array([0, radians(30), radians(70), radians(30), radians(40), 0])
        solution = self.chain.inverse_kinematics(self.position)
        # self.chain.plot(solution, self.ax)

        # self.print_solution()

        self.chain.plot(self.angles, self.ax)

        self.ax.scatter(
            self.position[0], self.position[1], self.position[2],
            marker="x", c="red")

        self.canvas.draw()

    def print_solution(self):
        import math
        solution = self.chain.inverse_kinematics(self.position)
        for angle in solution:
            print(' {:.2f} '.format(degrees(angle)), end='')
        print('')



