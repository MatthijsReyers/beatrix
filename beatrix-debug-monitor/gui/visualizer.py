from PyQt5.QtWidgets import QLabel, QGroupBox, QBoxLayout
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from ikpy.chain import Chain

class Visualizer(QGroupBox):
    def __init__(self):
        super(QGroupBox, self).__init__()
        self.setTitle("Visualizer")
        self.layout = QBoxLayout(QBoxLayout.Direction.Up, self)

        self.position = (5.0, 5.0, 5.0)

        # Load robot arm chain from URDF file.
        self.chain = Chain.from_urdf_file("./robot.URDF")
        solution = self.chain.inverse_kinematics(self.position)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111, projection='3d')
        self.chain.plot(solution, self.ax)
        
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.update_graph()

    def update_position(self, position):
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