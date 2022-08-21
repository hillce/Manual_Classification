from PyQt5 import QtCore, QtGui

def general_layout(widget,dark_mode=False):
    widget.setWindowTitle('Perspectum Diagnostics Quality Control')
    widget.setWindowIcon(QtGui.QIcon('./GUI_images/Icon.jpg'))

    # Set window background color
    widget.setAutoFillBackground(True)
    p = widget.palette()
    if dark_mode:
        p.setColor(widget.backgroundRole(), QtCore.Qt.black)
        widget.setStyleSheet("QLabel, QGroupBox {color: white; font: 12pt}")
    else:
        p.setColor(widget.backgroundRole(), QtCore.Qt.white)
        widget.setStyleSheet("QLabel, QGroupBox {font: 12pt}")
    widget.setPalette(p)