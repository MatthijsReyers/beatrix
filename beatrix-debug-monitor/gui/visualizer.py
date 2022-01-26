from PyQt5.QtWidgets import QLabel, QGroupBox, QBoxLayout
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from math import pi, radians, degrees
from ikpy.link import OriginLink, URDFLink
from lib.chain import ik_chain

from ikpy.chain import Chain


class Visualizer(QGroupBox):
    def __init__(self):
        super(QGroupBox, self).__init__()
        self.setTitle("Visualizer")
        self.layout = QBoxLayout(QBoxLayout.Direction.Up, self)

        self.position = (5.0, 5.0, 5.0)

        # Load robot arm chain from URDF file.
        # self.chain = Chain.from_urdf_file("./robot.URDF")
        # self.chain = ik_chain
        self.chain = guus_chain
        print("Length chain = {}".format(len(self.chain)))
        print(repr(self.chain))
        for l in self.chain.links:
            print(repr(l))

        solution = self.chain.inverse_kinematics(self.position)

        self.figure = Figure(figsize=(10, 10), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')

        print(type(solution))
        print(solution)


        self.chain.plot(solution, self.ax)

        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.update_graph()

    def update_position(self, position):
        self.position = position
        self.update_graph()

    def update_graph(self):
        self.ax.clear()
        self.ax.set_zlim([0, 50])
        self.ax.set_xlim([-50, 50])
        self.ax.set_ylim([-50, 50])

        zeroes = np.array([0, 0, radians(90), radians(10), radians(88), 0])
        test1 = np.array([0, radians(30), radians(70), radians(30), radians(40), 0])
        solution = self.chain.inverse_kinematics(self.position)
        self.chain.plot(test1, self.ax)

        self.print_solution()

        self.ax.scatter(
            self.position[0], self.position[1], self.position[2],
            marker="x", c="red")

        self.canvas.draw()

    def print_solution(self):
        import math
        solution = self.chain.inverse_kinematics(self.position)
        for angle in solution:
            print(' {:.2f} '.format(angle), end='')
        print('')


guus_chain = Chain(name='guus_chain', links=[
    OriginLink(),
    URDFLink(
        name="base",
        origin_translation=[0, 0, 6],
        origin_orientation=[0, 0, pi],
        rotation=[0, 0, 1],
        bounds=(0, radians(270))
    ),
    URDFLink(
        name="shoulder",
        origin_translation=[0, 0, 3],
        origin_orientation=[-0.5 * pi, 0, 0],
        rotation=[1, 0, 0],
        bounds=(radians(38), radians(90))
    ),
    URDFLink(
        name="elbow",
        origin_translation=[0, 0, 20],
        origin_orientation=[-radians(10), 0, pi],
        rotation=[1, 0, 0],
        bounds=(radians(10), radians(150))
    ),
    URDFLink(
        name="wrist",
        origin_translation=[0, 0, 15],
        origin_orientation=[-radians(88), 0, pi],
        rotation=[1, 0, 0],
        bounds=(radians(0), radians(180))
    ),
    URDFLink(
        name="wrist_turn",
        origin_translation=[0, 0, 10],
        origin_orientation=[0, 0, 0],
        rotation=[1, 0, 0],
        bounds=(radians(0), radians(180))
    ),
],
                   #active_links_mask=[False, True, True, True, True, True]
                   )
