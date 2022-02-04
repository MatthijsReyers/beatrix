from re import S
from typing import Tuple
from PyQt5.QtWidgets import (QSplitter, QTabWidget, QWidget, QGridLayout, QGroupBox, QLabel, QSlider, 
    QLineEdit, QSizePolicy, QVBoxLayout, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from lib.constants import *
from lib.kinematics import Kinematics, WristOrientation

POSITION_LIMIT = 50

class PositionManager(QSplitter):
    def __init__(self, kinematics: Kinematics):
        super(QSplitter, self).__init__()
        self.kinematics = kinematics

        self.wrist_orientation = WristOrientation.UNSET

        self.position = [0,0,0]
        self.position_callbacks = []
        self.position_sliders = []
        self.position_texts = []

        self.angles = INITIAL_ANGLES.copy()
        self.angles_callbacks = []
        self.angle_sliders = dict()
        self.angle_texts = dict()

        tab_widget = QTabWidget()
        self.addWidget(tab_widget)

        self.__init_postion_tab()
        tab_widget.addTab(self.position_tab, 'Position')

        self.__init_angles_tab()
        tab_widget.addTab(self.angles_tab, 'Angles')

        self.__init_wrist_angle_frame()

    def on_angles_change(self, callback:callable):
        """ Registers a callback function to be called whenever the user manually changes one of the 
        angles via this GUI menu. """
        self.angles_callbacks.append(callback)

    def on_position_change(self, callback:callable):
        """ Registers a callback function to be called whenever the user manually changes the position 
        goal via this GUI menu. """
        self.position_callbacks.append(callback)

    def set_position(self, pos:Tuple[float,float,float], update_kin:bool=True):
        """ Sets the position while updating all of the GUI elements and calling the registered callback
        functions. (Note: Do NOT call this within a callback handler to avoid infinite recursion)."""
        self.position = pos
        if update_kin:
            self.angles = self.kinematics.inverse(self.position, self.wrist_orientation)
            self.set_angles(self.angles, update_kin=False)
        for i in range(len(self.position)):
            slider = self.position_sliders[i] 
            slider.blockSignals(True)
            slider.setValue(round(self.position[i]))
            slider.blockSignals(False)
            self.position_texts[i].setText('{0:.2f}'.format(self.position[i]))
        for callback in self.position_callbacks:
            callback(pos)

    def set_angles(self, angles:dict, update_kin:bool=True):
        """ Sets the angles while updating all of the GUI elements and calling the registered callback
        functions. (Note: Do NOT call this within a callback handler to avoid infinite recursion). """
        self.angles = angles
        if update_kin:
            self.position = list(self.kinematics.get_forward_cartesian(angles))
            self.set_position(self.position, update_kin=False)
        for (joint, angle) in self.angles.items():
            slider = self.angle_sliders[joint]
            slider.blockSignals(True)
            slider.setValue(round(angle))
            slider.blockSignals(False)
            self.angle_texts[joint].setText('{0:.2f}'.format(angle))
        for callback in self.angles_callbacks:
            callback(angles)

    def __init_wrist_angle_frame(self):
        self.wrist_angle_box = QGroupBox()
        self.wrist_angle_box.setTitle('Wrist angle')
        layout = QVBoxLayout(self.wrist_angle_box)
        # layout.addWidget(QLabel('Wrist angle:'))
        buttons = QButtonGroup()
        buttons.setExclusive(True)
        for orient in WristOrientation:
            btn = QRadioButton(str(orient))
            if orient == self.wrist_orientation:
                btn.setChecked(True)
            layout.addWidget(btn)
            buttons.addButton(btn, orient.value)
            btn.toggled.connect(self.__on_wrist_btn(orient.value))
        self.addWidget(self.wrist_angle_box)

    def __on_wrist_btn(self, i):
        def update(ok):
            if ok: self.wrist_orientation = WristOrientation(i)
        return update

    def __init_postion_tab(self):
        self.position_tab = QWidget()
        layout = QGridLayout(self.position_tab)

        labels = ['X:', 'Y:', 'Z:']
        for axis in range(len(self.position)):
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
            line_edit.setText('{0:.2f}'.format(self.position[axis]))
            self.position_texts.append(line_edit)

            layout.addWidget(label, axis,0, 1,1)
            layout.addWidget(line_edit, axis,1, 1,1)
            layout.addWidget(slider, axis,2, 1,3)

        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 0)

    def __on_pos_slider(self, axis):
        def update(value):
            self.position[axis] = value
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
        for (i, (joint, angle)) in enumerate(self.angles.items()):
            label = QLabel(joint.capitalize().replace('_joint', '').replace('_', ' '))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0,i, 1,1)

            line_edit = QLineEdit()
            line_edit.setAlignment(Qt.AlignCenter)
            line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            line_edit.editingFinished.connect(self.__on_angle_text(joint))
            line_edit.setText('{0:.2f}'.format(angle))
            self.angle_texts[joint] = line_edit
            layout.addWidget(line_edit, 1,i, 1,1)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setValue(round(angle))
            slider.valueChanged.connect(self.__on_angle_slider(joint))
            slider.setMinimum(ANGLE_BOUNDS[joint][0])
            slider.setMaximum(ANGLE_BOUNDS[joint][1])
            self.angle_sliders[joint] = slider
            layout.addWidget(slider, 2, i, 1,1)

    def __on_angle_slider(self, joint):
        def update(value):
            self.angles[joint] = value
            self.set_angles(self.angles)
        return update

    def __on_angle_text(self, joint):
        def update():
            inputbox = self.angle_texts[joint]
            okay, value = self.__text_to_int(inputbox.text())
            if okay:
                self.angles[joint] = value
                self.set_angles(self.angles)
            else:
                inputbox.setText('{0:.2f}'.format(self.angles[joint]))
        return update

    def __text_to_int(self, text) -> Tuple[bool, float]:
        if len(text) == 0:
            return (True, 0)
        try:
            text = text.replace(' ','')
            text = text.replace(',','.')
            num = float(text)
            return (True, num)
        except:
            return (False, None)
