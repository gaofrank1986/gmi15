from PyQt5 import QtWidgets,QtGui,QtCore
import logging

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setStyleSheet("background-color: rgb(224, 234, 244);")

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent, name,fmt):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        # logTextBox.setFormatter(logging.Formatter("%(asctime)s — %(message)s",datefmt='%m-%d,%H:%M'))
        # logging.getLogger('Main').addHandler(logTextBox)
        logTextBox.setFormatter(fmt)
        logging.getLogger(name).addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger(name).setLevel(logging.DEBUG)
        logging.getLogger(name).propagate = False



        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)

        self.save = logTextBox.widget
        self.resize(1300, 500)