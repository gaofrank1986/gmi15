from PyQt5 import QtCore, QtGui, QtWidgets
from db_setup import get_info_by_id

class Delegate(QtWidgets.QStyledItemDelegate):
    def editorEvent(self, event, model, option, index):
        checked = index.data(QtCore.Qt.CheckStateRole)
        ret = QtWidgets.QStyledItemDelegate.editorEvent(self, event, model, option, index)
        if checked != index.data(QtCore.Qt.CheckStateRole):
            self.parent().checked.emit(index)
        return ret


class ListView(QtWidgets.QListView):
    checked = QtCore.pyqtSignal(QtCore.QModelIndex)
    def __init__(self, *args, **kwargs):
        super(ListView, self).__init__(*args, **kwargs)
        self.setItemDelegate(Delegate(self))


class AppRemovalPage(QtWidgets.QWizardPage):
    def __init__( self, parent=None):
        super(AppRemovalPage, self).__init__(parent)
        # self.setTitle('Apps to Remove')
        # self.setSubTitle('Listview')
        self.list_view = ListView(self)
        scroll_bar = QtWidgets.QScrollBar(self)
        self.list_view.setVerticalScrollBar(scroll_bar)

        # scroll_bar.setStyleSheet("background : lightgreen;")
        # self.list_view.setMinimumSize(465, 200)

        self.model = QtGui.QStandardItemModel(self)


        self.list_view.setModel(self.model)
        self.list_view.checked.connect(self.onChecked)
        self.record=set()

        
        
    def add(self,alist):
        self.model.clear()
        self.record=set()
        for line in alist:
            self.item = QtGui.QStandardItem(line)
            self.item.setCheckable(True)
            self.item.setCheckState(QtCore.Qt.Checked)
            self.record.add(self.item.text())
            
            self.model.appendRow(self.item)
            font = QtGui.QFont()
            font.setFamily("汉仪文黑-85w")
            font.setPointSize(10)
            self.item.setFont(font)



            
    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def onChecked(self, index):
        item = self.model.itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            print(item.text(), "was checked")
            self.record.add(item.text())
        else:
            print(item.text(), "was unchecked")
            self.record.remove(item.text())
        # print(self.record)