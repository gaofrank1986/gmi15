from random import shuffle
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtCore import Qt
from ..widget.log_page import QTextEditLogger
from PyQt5.uic import loadUi
import logging

class Win_Mlog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self):
        super(Win_Mlog,self).__init__()
        loadUi("./data/ui/mutli_log.ui",self)

        logTextBox = QTextEditLogger(self)
        logging.getLogger("Simc.1").addHandler(logTextBox)
        logging.getLogger("Simc.1").setLevel(logging.DEBUG)

        self.vh.addWidget(logTextBox.widget)

        self.tab1 = QtWidgets.QWidget()
        self.tabs.addTab(self.tab1,"Tab 1")

        logTextBox1 = QTextEditLogger(self)
        logging.getLogger("Simc.2").addHandler(logTextBox1)
        logging.getLogger("Simc.2").setLevel(logging.DEBUG)

        vh = QtWidgets.QVBoxLayout(self.tab1)
        # vh.setGeometry(10,10,390,230)
        vh.addWidget(logTextBox1.widget)

        logging.getLogger("Simc.2").info("hello")

    def display(self):
        self.exec_()
