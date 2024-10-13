from PyQt6.QtCore import Qt, QTimer, QThread
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import *

from motion_platform import MotionPlatform


class MainWidget(QWidget):
    def __init__(self, motion_plotform: MotionPlatform, parent=None):
        super().__init__(parent)

        self.manual_control_widget = ManualControlWidget(motion_plotform)
        self.enable_widget = EnableWidget(motion_plotform)

        layout = QVBoxLayout()
        layout.addWidget(self.manual_control_widget)
        layout.addWidget(self.enable_widget)

        self.setLayout(layout)


class EnableWidget(QWidget):
    def __init__(self, motion_plotform: MotionPlatform, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()

        button = QPushButton()
        button.setText('Enable')
        button.clicked.connect(motion_plotform.enable)
        layout.addWidget(button)

        self.setLayout(layout)

        timer = QTimer()
        timer.timeout.connect(lambda: button.setEnabled(not motion_plotform.isEnabled()))

        self.bgthread = QThread()
        self.bgthread.started.connect(lambda: timer.start(500))
        self.bgthread.start()


class ManualControlWidget(QWidget):
    def __init__(self, motion_plotform: MotionPlatform, parent=None):
        super().__init__(parent)

        layout = QFormLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(15)
        jog_axis_widget = JogAxisWidget(motion_plotform)
        layout.addRow(
            QLabel("Jog Axis"),
            jog_axis_widget
        )
        layout.addRow(
            QLabel("Jog Distance (mm)"),
            JogDistanceWidget(jog_axis_widget.setJogDistance),
        )
        layout.addRow(
            QLabel("Jog speed (mm/s)"),
            JogSpeedWidget(jog_axis_widget.setJogSpeed)
        )
        self.setLayout(layout)


class JogAxisWidget(QWidget):
    def __init__(self, motion_plotform: MotionPlatform, parent=None):
        super().__init__(parent)
        self.jog_distance = 0
        self.jog_speed = 0.0

        xy_buttons = QGridLayout()
        button = QToolButton()
        button.setIcon(load_icon("chevron-up.png"))
        button.clicked.connect(lambda: motion_plotform.moveIncrementY(self.jog_distance, self.jog_speed))
        xy_buttons.addWidget(button, 0, 1)
        button = QToolButton()
        button.setIcon(load_icon("chevron-left.png"))
        button.clicked.connect(lambda: motion_plotform.moveIncrementX(-self.jog_distance, self.jog_speed))
        xy_buttons.addWidget(button, 1, 0)
        button = QToolButton()
        button.setIcon(load_icon("home.png"))
        button.clicked.connect(motion_plotform.homeXY)
        xy_buttons.addWidget(button, 1, 1)
        button = QToolButton()
        button.setIcon(load_icon("chevron-right.png"))
        button.clicked.connect(lambda: motion_plotform.moveIncrementX(self.jog_distance, self.jog_speed))
        xy_buttons.addWidget(button, 1, 2)
        button = QToolButton()
        button.setIcon(load_icon("chevron-down.png"))
        button.clicked.connect(lambda: motion_plotform.moveIncrementY(-self.jog_distance, self.jog_speed))
        xy_buttons.addWidget(button, 2, 1)

        z_buttons = QGridLayout()
        button = QToolButton()
        button.setIcon(load_icon("chevron-up.png"))
        # button.clicked.connect(lambda: self.onMoveButtonClicked("Z"))
        z_buttons.addWidget(button, 0, 0)
        button = QToolButton()
        button.setIcon(load_icon("home.png"))
        # button.clicked.connect(lambda: self.onHomeButtonClicked("Z"))
        z_buttons.addWidget(button, 1, 0)
        button = QToolButton()
        button.setIcon(load_icon("chevron-down.png"))
        # button.clicked.connect(lambda: self.onMoveButtonClicked("Z-"))
        z_buttons.addWidget(button, 2, 0)

        layout = QGridLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(10)

        layout.addWidget(QLabel("X/Y"), 0, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel("Z"), 0, 1, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(xy_buttons, 1, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(z_buttons, 1, 1, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def setJogDistance(self, jog_distance):
        self.jog_distance = jog_distance

    def setJogSpeed(self, jog_speed):
        self.jog_speed = jog_speed


class JogDistanceWidget(QWidget):
    def __init__(self, set_jog_distance_func, parent=None):
        super().__init__(parent)
        self.set_jog_distance_func = set_jog_distance_func

        layout = QHBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        dists = ["1", "10", "100", "200"]
        self.buttons = []
        for i, dist in enumerate(dists):
            button = QToolButton()
            button.setText(dist)
            button.setCheckable(True)
            button.clicked.connect(lambda _, i=i: self.onButtonClicked(i))
            layout.addWidget(button)
            self.buttons.append(button)

        self.setLayout(layout)

        self.onButtonClicked(0)

    def onButtonClicked(self, i):
        for button in self.buttons:
            button.setChecked(False)
        self.buttons[i].setChecked(True)
        self.set_jog_distance_func(float(self.buttons[i].text()))


class JogSpeedWidget(QWidget):
    def __init__(self, set_jog_speed_func, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        number_box = QSpinBox()
        number_box.setRange(1, 2000)
        number_box.setSingleStep(100)
        number_box.setValue(10)
        number_box.valueChanged.connect(lambda: set_jog_speed_func(number_box.value()))
        layout.addWidget(number_box)

        self.setLayout(layout)

        set_jog_speed_func(number_box.value())


def load_icon(filename) -> QIcon:
    return QIcon("./icons/" + filename)
