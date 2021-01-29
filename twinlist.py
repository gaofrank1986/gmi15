from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi

class TwoListSelection(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TwoListSelection, self).__init__(parent)
        self.setup_layout()

    def setup_layout(self):
        lay = QtWidgets.QHBoxLayout(self)
        self.mInput = QtWidgets.QListWidget()
        self.mOuput = QtWidgets.QListWidget()

        self.mButtonToSelected = QtWidgets.QPushButton(">>")
        self.mBtnMoveToAvailable= QtWidgets.QPushButton(">")
        self.mBtnMoveToSelected= QtWidgets.QPushButton("<")
        self.mButtonToAvailable = QtWidgets.QPushButton("<<")

        vlay = QtWidgets.QVBoxLayout()
        vlay.addStretch()
        vlay.addWidget(self.mButtonToSelected)
        vlay.addWidget(self.mBtnMoveToAvailable)
        vlay.addWidget(self.mBtnMoveToSelected)
        vlay.addWidget(self.mButtonToAvailable)
        vlay.addStretch()

        self.mBtnUp = QtWidgets.QPushButton("Up")
        self.mBtnDown = QtWidgets.QPushButton("Down")

        vlay2 = QtWidgets.QVBoxLayout()
        vlay2.addStretch()
        vlay2.addWidget(self.mBtnUp)
        vlay2.addWidget(self.mBtnDown)
        vlay2.addStretch()

        lay.addWidget(self.mInput)
        lay.addLayout(vlay)
        lay.addWidget(self.mOuput)
        lay.addLayout(vlay2)

        self.update_buttons_status()
        self.connections()

    @QtCore.pyqtSlot()
    def update_buttons_status(self):
        self.mBtnUp.setDisabled(not bool(self.mOuput.selectedItems()) or self.mOuput.currentRow() == 0)
        self.mBtnDown.setDisabled(not bool(self.mOuput.selectedItems()) or self.mOuput.currentRow() == (self.mOuput.count() -1))
        self.mBtnMoveToAvailable.setDisabled(not bool(self.mInput.selectedItems()) or self.mOuput.currentRow() == 0)
        self.mBtnMoveToSelected.setDisabled(not bool(self.mOuput.selectedItems()))

    def connections(self):
        self.mInput.itemSelectionChanged.connect(self.update_buttons_status)
        self.mOuput.itemSelectionChanged.connect(self.update_buttons_status)
        self.mBtnMoveToAvailable.clicked.connect(self.on_mBtnMoveToAvailable_clicked)
        self.mBtnMoveToSelected.clicked.connect(self.on_mBtnMoveToSelected_clicked)
        self.mButtonToAvailable.clicked.connect(self.on_mButtonToAvailable_clicked)
        self.mButtonToSelected.clicked.connect(self.on_mButtonToSelected_clicked)
        self.mBtnUp.clicked.connect(self.on_mBtnUp_clicked)
        self.mBtnDown.clicked.connect(self.on_mBtnDown_clicked)

    @QtCore.pyqtSlot()
    def on_mBtnMoveToAvailable_clicked(self):
        self.mOuput.addItem(self.mInput.takeItem(self.mInput.currentRow()))

    @QtCore.pyqtSlot()
    def on_mBtnMoveToSelected_clicked(self):
        self.mInput.addItem(self.mOuput.takeItem(self.mOuput.currentRow()))

    @QtCore.pyqtSlot()
    def on_mButtonToAvailable_clicked(self):
        while self.mOuput.count() > 0:
            self.mInput.addItem(self.mOuput.takeItem(0))

    @QtCore.pyqtSlot()
    def on_mButtonToSelected_clicked(self):
        while self.mInput.count() > 0:
            self.mOuput.addItem(self.mInput.takeItem(0))        

    @QtCore.pyqtSlot()
    def on_mBtnUp_clicked(self):
        row = self.mOuput.currentRow()
        currentItem = self.mOuput.takeItem(row)
        self.mOuput.insertItem(row - 1, currentItem)
        self.mOuput.setCurrentRow(row - 1)

    @QtCore.pyqtSlot()
    def on_mBtnDown_clicked(self):
        row = self.mOuput.currentRow()
        currentItem = self.mOuput.takeItem(row)
        self.mOuput.insertItem(row + 1, currentItem)
        self.mOuput.setCurrentRow(row + 1)

    def addAvailableItems(self, items):
        self.mInput.addItems(items)

    def addSelectedItems(self, items):
        self.mOuput.addItems(items)
   
    def clear(self):
        self.mInput.clear()
        self.mOuput.clear()

        
    def get_left_elements(self):
        r = []
        for i in range(self.mInput.count()):
            it = self.mInput.item(i)
            r.append(it.text())
        return r

    def get_right_elements(self):
        r = []
        for i in range(self.mOuput.count()):
            it = self.mOuput.item(i)
            r.append(it.text())
        return r
    
    
class TwinlistPage(QtWidgets.QDialog):

    def __init__( self, parent=None):
        super(TwinlistPage, self).__init__(parent)
        loadUi("./data/ui/twinlist.ui",self) 

        self.list_selection = TwoListSelection()
        # self.list_selection.addAvailableItems(["item-{}".format(i) for i in range(5)])
        # def on_clicked_left():
        #     print(self.list_selection.get_left_elements())
        # def on_clicked_right():
        #     print(self.list_selection.get_right_elements())
        # l_button = QtWidgets.QPushButton(
        #     text="print left elements",
        #     clicked=on_clicked_left
        # )
        # r_button = QtWidgets.QPushButton(
        #     text="print right elements",
        #     clicked=on_clicked_right
        # )
        left = QtWidgets.QLabel()
        right = QtWidgets.QLabel()
        left.setText("未选")
        right.setText("已选(超过5个只有前5个有效)")
        lay = self.vlay
        hlay = QtWidgets.QHBoxLayout()
        hlay.addWidget(left)
        hlay.addWidget(right)
        lay.addLayout(hlay)
        lay.addWidget(self.list_selection)
        self.saved = []
        self.if_OK = False
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.OK)

    def display(self,alist,blist):
        self.list_selection.clear()
        self.list_selection.addAvailableItems(alist)
        self.list_selection.addSelectedItems(blist)
        self.if_OK = False
        self.exec_()
        
        
    def OK(self):
        self.saved = self.list_selection.get_right_elements()
        if len(self.saved) >5:
            self.saved = self.saved[:5]
        self.if_OK = True
if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    w = TwinlistPage()
    w.show()
    sys.exit(app.exec_())