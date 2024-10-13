import logging
from PyQt6.QtWidgets import QApplication
from motion_platform import MotionPlatform
from custom_widgets import MainWidget

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    motion_platform = MotionPlatform()

    app = QApplication([])
    app.setApplicationName("Motion Platform")
    app.setWindowIcon
    app.setStyle("fusion")

    widget = MainWidget(motion_platform)
    widget.show()

    app.exec()
