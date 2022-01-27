from PyQt5.QtWidgets import QTabWidget, QWidget, QGridLayout, QLabel, QSlider, QLineEdit, QSizePolicy
from PyQt5.QtCore import Qt
import math

POSITION_LIMIT = 50

class PositionManager(QTabWidget):
    def __init__(self, kinematics):
        super(QTabWidget, self).__init__()
        self.kinematics = kinematics

        self.position = [0,0,0]
        self.position_callbacks = []
        self.position_sliders = []
        self.position_texts = []

        self.angles = kinematics.inverse(self.position)
        self.angles_callbacks = []
        self.angle_sliders = []
        self.angle_texts = []

        self.__init_postion_tab()
        self.addTab(self.position_tab, 'Position')

        self.__init_angles_tab()
        self.addTab(self.angles_tab, 'Angles')

    def on_angles_change(self, callback:callable):
        """ Registers a callback function to be called whenever the user manually changes one of the 
        angles via this GUI menu. """
        self.angles_callbacks.append(callback)

    def on_position_change(self, callback:callable):
        """ Registers a callback function to be called whenever the user manually changes the position 
        goal via this GUI menu. """
        self.position_callbacks.append(callback)

    def set_position(self, pos:(int,int,int), update_kin:bool=True):
        """ Sets the position while updating all of the GUI elements and calling the registered callback
        functions. (Note: Do NOT call this within a callback handler to avoid infinite recursion)."""
        self.position = pos
        if update_kin:
            self.angles = self.kinematics.inverse(pos)
            self.set_angles(self.angles, update_kin=False)
        for i in range(3):
            slider = self.position_sliders[i] 
            slider.blockSignals(True)
            slider.setValue(self.position[i])
            slider.blockSignals(False)
            self.position_texts[i].setText(str(self.position[i]))
        for callback in self.position_callbacks:
            callback(pos)

    def set_angles(self, angles:list, update_kin:bool=True):
        """ Sets the angles while updating all of the GUI elements and calling the registered callback
        functions. (Note: Do NOT call this within a callback handler to avoid infinite recursion)."""
        self.angles = angles
        if update_kin:
            self.position = self.kinematics.forward(angles)
            self.set_position(self.position, update_kin=False)
        for (i, angle) in enumerate(self.angles):
            slider = self.angle_sliders[i]
            slider.blockSignals(True)
            slider.setValue(math.degrees(angle))
            slider.blockSignals(False)
            self.angle_texts[i].setText('{0:.2f}'.format(math.degrees(angle)))
        for callback in self.angles_callbacks:
            callback(angles)

    def __init_postion_tab(self):
        self.position_tab = QWidget()
        layout = QGridLayout(self.position_tab)

        labels = ['X:', 'Y:', 'Z:']
        for axis in range(0,3):
            label = QLabel(labels[axis])
            label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            label.setMaximumWidth(13)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            slider.valueChanged.connect(self.__on_pos_slider(axis))
            slider.setMinimum(-POSITION_LIMIT if axis != 2 else 0)
            slider.setMaximum(POSITION_LIMIT)
            self.position_sliders.append(slider)

            line_edit = QLineEdit()
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setMaximumWidth(50)
            line_edit.editingFinished.connect(self.__on_pos_text(axis))
            line_edit.setText(str(self.position[axis]))
            self.position_texts.append(line_edit)

            layout.addWidget(label, axis,0, 1,1)
            layout.addWidget(line_edit, axis,1, 1,1)
            layout.addWidget(slider, axis,2, 1,3)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

    def __on_pos_slider(self, axis):
        def update(value):
            self.position[axis] = math.radians(value)
            self.set_position(self.position)
        return update

    def __on_pos_text(self, axis):
        def update():
            inputbox = self.position_texts[axis]
            okay, value = self.__text_to_int(inputbox.text())
            if okay:
                value = max(-POSITION_LIMIT if axis != 2 else 0, min(POSITION_LIMIT, value))
                self.position[axis] = value
                self.set_position(self.position)
            else:
                inputbox.setText(str(self.position[axis]))
        return update

    def __init_angles_tab(self):
        self.angles_tab = QWidget()
        layout = QGridLayout(self.angles_tab)
        labels = ['-', 'Base', '-', 'Shoulder', 'Elbow', 'Wrist']
        for (i, angle) in enumerate(self.angles):
            label = QLabel(labels[i])
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0,i, 1,1)

            line_edit = QLineEdit()
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            line_edit.editingFinished.connect(self.__on_angle_text(i))
            line_edit.setText('{0:.2f}'.format(math.degrees(angle)))
            self.angle_texts.append(line_edit)
            layout.addWidget(line_edit, 1,i, 1,1)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.valueChanged.connect(self.__on_angle_slider(i))
            slider.setValue(math.degrees(angle))
            slider.setMinimum(0)
            slider.setMaximum(360)
            self.angle_sliders.append(slider)
            layout.addWidget(slider, 2,i, 1,1)

    def __on_angle_slider(self, i):
        def update(value):
            self.angles[i] = math.radians(value)
            self.set_angles(self.angles)
        return update

    def __on_angle_text(self, i):
        def update():
            inputbox = self.angle_texts[i]
            okay, value = self.__text_to_int(inputbox.text())
            if okay:
                self.angles[i] = math.radians(value)
                self.set_angles(self.angles)
            else:
                inputbox.setText('{0:.2f}'.format(math.degrees(self.angles[i])))
        return update

    def __text_to_int(self, text) -> (bool, float):
        if len(text) == 0:
            return (True, 0)
        try:
            text = text.replace(' ','')
            text = text.replace(',','.')
            num = float(text)
            return (True, num)
        except:
            return (False, None)
