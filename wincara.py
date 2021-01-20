from random import shuffle
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtCore import Qt

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, width, height, ppl,path):
        super(ClickableLabel, self).__init__()
        # self.resize(80,80)
        pixmap = QtGui.QPixmap(path+ppl+".png")
        if pixmap.isNull():
            pixmap = QtGui.QPixmap("./data/character/icon/empty.png")
        pixmap = pixmap.scaled(width,height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        self.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.setStyleSheet("ClickableLabel::hover"
                                "{"
                                "border : 2px solid blue;"
                                "}") 
        self.setObjectName(ppl)
        # self.resize(width,height)

    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())


class caraWindow(QtWidgets.QDialog):
    def __init__(self,alist,path,lookup=None):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QGridLayout(self)
        self.cara=""
        self.clicked = False
        self.path = path

        num_col=5
        num_row=int(len(alist)/num_col)+1
        font = QtGui.QFont()
        font.setFamily("汉仪文黑-85w")
        font.setPointSize(9)
        for row in range(1,num_row+1):
            for column in range(1,num_col+1):
                try:
                    hlay = QtWidgets.QVBoxLayout()
                    hlay.setContentsMargins(0, 0, 0, 0)
                    item = alist[(row-1)*num_col+column-1]
                    icon = ClickableLabel(80, 80,item,self.path)
                    icon.clicked.connect(self.handleLabelClicked)
                    hlay.addWidget(icon)
                    if not (lookup is None):
                        label = QtWidgets.QLabel(lookup[item])
                        label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
                        label.setFont(font)
                        label.resize(80,5)
                        hlay.addWidget(label)
                    layout.addLayout(hlay, row, column)
                except:
                    pass
        self.setMinimumWidth(500)
        # if not (lookup is None):
        #     self.setMinimumHeight(num_row*(80+60))
        # else:
        # self.setMinimumHeight(num_row*(80+20))

    def handleLabelClicked(self, name):
        print('"%s" clicked' % name)
        self.cara = name
        self.clicked = True
        self.close()

