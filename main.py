import ctypes

from PyQt6.QtWidgets import QApplication

import myhardware
import custom_widgets

if __name__ == '__main__':
    hardware = myhardware.MyHardware()
    hardware.enable()

    myappid = "mycompany.myproduct.subproduct.version"  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication([])
    app.setApplicationName("3-axis")
    app.setWindowIcon
    app.setStyle("fusion")

    widget = custom_widgets.MainWidget(hardware)
    widget.show()

    app.exec()
