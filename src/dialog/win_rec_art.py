from PyQt5.QtWidgets import QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox,QFileDialog,QComboBox,QDoubleSpinBox,QDialogButtonBox,QStyledItemDelegate
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap,QStandardItem, QStandardItemModel
# from PyQt5.QtGui import QStandardItem, QStandardItemModel
# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

import traceback
import json
import os
import shutil
import logging
from sqlalchemy import or_

from ..mods.ocr import ocr,parse
from ..mods.db_setup import Entry,db_session
from ..mods.utility import extract_rlist
from ..widget.twinlist import TwinlistPage

def createModel(options):
    model = QStandardItemModel(len(options), 1)
    firstItem = QStandardItem("最多5个")
    # firstItem.setBackground(QtGui.QBrush(QtGui.QColor(200, 200, 200)))
    firstItem.setSelectable(False)
    model.setItem(0, 0, firstItem)
    for i, area in enumerate(options):
        item = QStandardItem(area)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        model.setItem(i+1, 0, item)
    return model


class RName(QDialog):
    def __init__(self):
        super(RName,self).__init__()
        loadUi("./data/ui/name_ar.ui",self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.OK)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.Cancel)
        self.if_OK = False
        self.name = ''
    def OK(self):
        self.if_OK = True
        self.name = self.lineEdit.text()
        self.close()
    def set_name(self,s):
        self.lineEdit.setText(s)
    def Cancel(self):
        # self.if_OK = True
        self.close()         
      
class DB_Filter(QDialog):
    def __init__(self,alist):
        super(DB_Filter,self).__init__()
        loadUi("./data/ui/filter_db.ui",self)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.OK)
        self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.Cancel)
        self.cb_filter.addItems(['全部']+alist)
        self.if_OK = False
        self.filter = None
    def OK(self):
        self.if_OK = True
        self.filter = self.cb_filter.currentText()
        self.close()
    def Cancel(self):
        self.close()  
        
class Rec_Artifact(QDialog):
    def __init__(self,data,sbar):
        super(Rec_Artifact,self).__init__()
        loadUi("./data/ui/artifacts2.ui",self)        
        # self.pb_savefile.clicked.connect(self.savefile)
        self.pb_link_pic.clicked.connect(self.new_pic_link)
        self.pb_clear.clicked.connect(self.clear)
        self.pb_savedb.clicked.connect(self.save_entry)
        self.pb_lookupdb.clicked.connect(self.lookupdb)
        # self.pb_openfile.clicked.connect(self.openfile)
        self.pb_openimg.clicked.connect(self.openimgfile)
        self.pb_db_del.clicked.connect(self.delete_entry)
        self.pb_db_update.clicked.connect(self.renew_entry)
        
        self.pos = {'理之冠':'head','时之沙':'glass','空之杯':'cup','生之花':'flower','死之羽':'feather'}
        self.plist = ['暴击','暴伤','攻击%','攻击(固定)','属伤','物伤','防御','生命%','生命(固定)','治疗','精通','充能','火伤','水伤','冰伤','雷伤','风伤','岩伤']
        self.dlist = ['cr','cd','ar','sa','ed','dphys','dr','hr','sh','dheal','em','ef','dfire','dwatr','dice','delec','dwind','drock']

        self.slist = ['暴击','暴伤','攻击%','攻击(固定)','防御%','防御(固定)','生命%','生命(固定)','精通','充能']
        self.tlist = ['cr','cd','ar','sa','dr','sd','hr','sh','em','ef']
        

        self.sbar = sbar
        self.elist = extract_rlist(data)
        logging.getLogger('1').info("db套装{}".format(self.elist))
        self.cb_aeffect.addItems(self.elist)
        self.cb_main.addItems(self.plist)
        self.cb_sub_1.addItems(self.slist)
        self.cb_sub_2.addItems(self.slist)
        self.cb_sub_3.addItems(self.slist)
        self.cb_sub_4.addItems(self.slist)
        
        # init_db()
        
        self.cached = None
        self.look_up = {}
        
        self.owners=['无']
    
        path = "./data/info.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        for i in data:
            if "=" not in i:
                self.owners.append(i)
                
        self.twinlist = TwinlistPage(self)
        # self.twinlist.setMinimumSize(750,300)
        self.pb_select_owners.clicked.connect(self.show_twinlist)
                
        # self.model = createModel(self.owners)
        # self.cb_owner.setModel(self.model)
        # self.model.itemChanged.connect(self.on_itemChanged)

        self.twinlist.list_selection.addAvailableItems(self.owners)
        # self.cb_owner.addItems(self.owners)

        self.pathm='./data/'
        self.save_pos = 0
            
    
    # def on_itemChanged(self):
    #     model = self.model
    #     items = []
    #     for row in range(model.rowCount()):
    #         comboItem = model.index(row, 0)
    #         if comboItem.data(Qt.CheckStateRole):
    #             items.append(comboItem.data())
    #     print(items)
    def show_twinlist(self):
        owners = self.label_owners.text()
        owners = owners.split(',')
        unselected = self.owners.copy()
        selected = []

        for i in owners:
            if i in unselected:
                unselected.remove(i)
                selected.append(i)
            else:
                if i not in selected and i!='':
                    selected.append(i)
        print(unselected)
        print(selected)
        self.twinlist.display(unselected,selected)
        if self.twinlist.if_OK:
            self.label_owners.setText(','.join(self.twinlist.saved))

    def load_entry(self):
        aaa = self.cb_db.currentIndex()
        assert aaa in self.look_up
        r1 = db_session.query(Entry).filter(Entry.id == self.look_up[aaa]).first()
        pix = QPixmap()
        pix.loadFromData(r1.img)
        self.cached = r1.img
        pixmap = pix.scaled(370,591, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.label_pic.setPixmap(pixmap)
        self.label_pic.resize(pixmap.width(),pixmap.height())

        tmp = list(self.pos.keys())
        self.cb_pos.setCurrentIndex(tmp.index(r1.pos))    
        self.cb_main.setCurrentIndex(self.dlist.index(r1.main0))
        self.digit_main.setValue(r1.main1)
        # self.cb_owner.setCurrentIndex(self.owners.index(r1.owner))
        for i in range(1,5):
            self.findChild(QComboBox,"cb_sub_"+str(i)).setCurrentIndex(self.tlist.index(getattr(r1,'sub'+str(i)+'0')))
            self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).setValue(getattr(r1,'sub'+str(i)+'1'))
            self.cb_aeffect.setCurrentIndex(self.elist.index(r1.aset))
            self.le_cmt.setText(r1.cmts)
        self.label_id.setText("ID: {}".format(self.look_up[aaa]))
        owners = [r1.owner0,r1.owner1,r1.owner2,r1.owner3,r1.owner4]
        for i in range(len(owners)):
            if owners[i] is None:
                owners[i]=''
        self.label_owners.setText(','.join(owners))
        # print(owners)
   
    def delete_entry(self):
        aaa = self.cb_db.currentIndex()
        try:
            assert aaa in self.look_up
            r1 = db_session.query(Entry).filter(Entry.id == self.look_up[aaa]).delete()
            db_session.commit()
            self.lookupdb(quick=True)
            if aaa==1:
                aaa=1
            self.cb_db.setCurrentIndex(aaa-1)
        except:
            pass
        
    
    def renew_entry(self):

        try:
            aaa = self.cb_db.currentIndex()
            assert aaa in self.look_up
            self.bbb = RName()
            self.bbb.set_name(self.cb_db.currentText().split('.')[1])
            self.bbb.exec_()
            
            r1 = db_session.query(Entry).filter(Entry.id == self.look_up[aaa]).first()
            
            pos2={self.plist[i]:self.dlist[i] for i in range(len(self.plist))}
            pos1={self.slist[i]:self.tlist[i] for i in range(len(self.slist))}
            
            saved_pos=[]
            if self.bbb.if_OK:
                r1.name = self.bbb.name

            r1.pos = self.cb_pos.currentText()
            r1.aset = self.cb_aeffect.currentText()
            r1.cmts = self.le_cmt.text()
            r1.main0 = pos2[self.cb_main.currentText()]
            saved_pos.append(pos2[self.cb_main.currentText()])
            r1.main1 = self.digit_main.value()
            # r1.owner = self.cb_owner.currentText()
            owners = self.label_owners.text()
            owners = owners.split(',')
            if len(owners)<5:
                owners = owners+['无']*(5-len(owners))
            
            r1.owner0 = owners[0]
            r1.owner1 = owners[1]
            r1.owner2 = owners[2]
            r1.owner3 = owners[3]
            r1.owner4 = owners[4]

            
            
            for i in range(1,5):
                pos = pos1[self.findChild(QComboBox,"cb_sub_"+str(i)).currentText()]
                assert(pos not in saved_pos)
                saved_pos.append(pos)
                
                tag = 'sub'+str(i)
                setattr(r1,tag+str(0),pos)
                setattr(r1,tag+str(1),self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).value())

            if not (self.cached is None):
                r1.img = self.cached
            db_session.commit()
            self.lookupdb(quick=True)
            self.cb_db.setCurrentIndex(aaa)
            
            self.sbar.showMessage("圣遗物数据存储成功",1000)

        except:
            db_session.rollback()
            self.sbar.showMessage("圣遗物文件存储错误",2000)
            logging.getLogger('1').error(traceback.format_exc())

    def lookupdb(self,quick=False):
        try:
            try:
                self.cb_db.currentIndexChanged.disconnect(self.load_entry)
            except:
                pass
            
            if not quick:
                self.aaa = DB_Filter(self.owners)
                self.aaa.exec_()
                if self.aaa.if_OK:
                    self.cb_db.clear()
                    N=0
                    self.last_filter = self.aaa.filter
                    if self.aaa.filter == '全部':
                        tmp = True
                    else:
                        tmp = False
                    for i in db_session.query(Entry).filter(or_(Entry.owner0==self.aaa.filter,Entry.owner1==self.aaa.filter,Entry.owner2==self.aaa.filter,Entry.owner3==self.aaa.filter,Entry.owner4==self.aaa.filter,tmp)).all():
                        self.cb_db.addItem(str(i.id)+'.'+i.name)
                        self.look_up[N] = i.id
                        N+=1
                    
                    
            else:
                self.cb_db.clear()
                N=0
                if self.last_filter == '全部':
                    tmp = True
                else:
                    tmp = False
                for i in db_session.query(Entry).filter(or_(Entry.owner0==self.aaa.filter,Entry.owner1==self.aaa.filter,Entry.owner2==self.aaa.filter,Entry.owner3==self.aaa.filter,Entry.owner4==self.aaa.filter,tmp)).all():
                    self.cb_db.addItem(str(i.id)+'.'+i.name)
                    self.look_up[N] = i.id
                    N+=1
            self.cb_db.currentIndexChanged.connect(self.load_entry)               
            self.sbar.showMessage("圣遗物数据库加载成功",1000)
            self.load_entry()
        except:
            self.sbar.showMessage("圣遗物数据库加载失败",2000)
            logging.getLogger('1').error(traceback.format_exc())    
        
    def save_entry(self):
        try:
            self.aaa = RName()
            self.aaa.exec_()

            if self.aaa.if_OK:
                pos2={self.plist[i]:self.dlist[i] for i in range(len(self.plist))}
                pos1={self.slist[i]:self.tlist[i] for i in range(len(self.slist))}
                
                r1 = Entry()
                saved_pos=[]

                r1.name = self.aaa.name                
                r1.pos = self.cb_pos.currentText()
                r1.aset = self.cb_aeffect.currentText()
                r1.cmts = self.le_cmt.text()
                r1.main0 = pos2[self.cb_main.currentText()]
                saved_pos.append(pos2[self.cb_main.currentText()])
                r1.main1 = self.digit_main.value()
                # r1.owner = self.cb_owner.currentText()
                owners = self.label_owners.text()
                owners = owners.split(',')
                if len(owners)<5:
                    owners = owners+['无']*(5-len(owners))
                
                r1.owner0 = owners[0]
                r1.owner1 = owners[1]
                r1.owner2 = owners[2]
                r1.owner3 = owners[3]
                r1.owner4 = owners[4]
                # N=1
                for i in range(1,5):
                    pos = pos1[self.findChild(QComboBox,"cb_sub_"+str(i)).currentText()]
                    assert(pos not in saved_pos)
                    saved_pos.append(pos)
                    
                    tag = 'sub'+str(i)
                    setattr(r1,tag+str(0),pos)
                    setattr(r1,tag+str(1),self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).value())
                    # N+=1

                if not (self.cached is None):
                    r1.img = self.cached
                    
                    
                    
            
                db_session.add(r1)
                db_session.commit()
                self.lookupdb(quick=True)
                self.cb_db.setCurrentIndex(self.cb_db.count()-1)
                
                self.sbar.showMessage("圣遗物数据存储成功",1000)

        except:
            db_session.rollback()
            self.sbar.showMessage("圣遗物文件存储错误",2000)
            logging.getLogger('1').error(traceback.format_exc())


    def new_pic_link(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', self.pathm,'圣遗物图像文件 (*.*)')
        if path != ('', ''):
            pixmap = QPixmap(path[0]).scaled(370,591, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label_pic.setPixmap(pixmap)
            self.label_pic.resize(pixmap.width(),pixmap.height())
            with open(file=path[0],mode='rb',) as fp:
                self.cached = fp.read()      
                      
    def openimgfile(self):
        try:
            self.clear()
            trans = {'攻击力%':'ar','防御力%':'dr','生命值%':'hr','生命值':'sh','元素充能效率%':'ef','暴击率%':'cr','暴击伤害%':'cd','攻击力':'sa','元素精通':'em','防御力':'sd','火元素伤害加成%':'dfire','水元素伤害加成%':'dwatr','冰元素伤害加成%':'dice','雷元素伤害加成%':'delec','风元素伤害加成%':'dwind','岩元素伤害加成%':'drock','物理伤害加成%':'dphys'}
            path = QFileDialog.getOpenFileName(self, 'Open a file', self.pathm,'圣遗物图像文件 (*.*)')
            if path != ('', ''):
                self.pathm = path[0]
                pixmap = QPixmap(path[0]).scaled(370,591, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_pic.setPixmap(pixmap)
                self.label_pic.resize(pixmap.width(),pixmap.height())
                with open(file=path[0],mode='rb',) as fp:
                    self.cached = fp.read()
                ans = ocr(path[0])
                data = ans.split('\n')

                pos = ans.split('\n')[1]  
                assert pos in self.pos.keys()      
                tmp = list(self.pos.keys())
                self.cb_pos.setCurrentIndex(tmp.index(pos))    
                ans2 = parse(ans)
                assert(len(ans2[1])==5)
                self.cb_main.setCurrentIndex(self.dlist.index(trans[ans2[1][0][0]]))
                self.digit_main.setValue(ans2[1][0][1])
                for i in range(1,5):
                    self.findChild(QComboBox,"cb_sub_"+str(i)).setCurrentIndex(self.tlist.index(trans[ans2[1][i][0]]))
                    self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).setValue((ans2[1][i][1]))
            
                found = False
                for i in self.elist:
                    for j in [0,7,8,9,10,11]:
                        if i in data[j]:
                            found = True
                            self.cb_aeffect.setCurrentIndex(self.elist.index(i))
                            self.le_cmt.setText(data[0]+'  等级:'+str(ans2[0]))
                            break   
                    if found:
                        break
                if not found:
                    self.cb_aeffect.setCurrentIndex(0)
            self.sbar.showMessage("圣遗物图像读取成功",1000)

        except:
            self.sbar.showMessage("圣遗物图像读取错误",2000)
            logging.getLogger('1').error(traceback.format_exc())                  

            
    def display(self):
        self.exec_()     

    def clear(self):
        try:

            for i in range(1,5):
                self.findChild(QComboBox,"cb_sub_"+str(i)).setCurrentIndex(0)
                self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).setValue(0)

            
            self.cb_main.setCurrentIndex(0)
            self.digit_main.setValue(0)
            self.le_cmt.setText("")
            # self.cb_pos.setCurrentIndex(0)        
            self.cb_aeffect.setCurrentIndex(0)
            self.label_pic.setText("图形")
            self.cached = None
            self.label_id.setText("")
            self.label_owners.setText("无,无,无,无,无")
        except:
            self.sbar.showMessage("圣遗物界面clear错误")
            logging.getLogger('1').error(traceback.format_exc())
            
            
# ===============================
# class CheckableComboBox(QComboBox):

#     # Subclass Delegate to increase item height
#     class Delegate(QStyledItemDelegate):
#         def sizeHint(self, option, index):
#             size = super().sizeHint(option, index)
#             size.setHeight(20)
#             return size

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Make the combo editable to set a custom text, but readonly
#         self.setEditable(True)
#         self.lineEdit().setReadOnly(True)
#         # Make the lineedit the same color as QPushButton
#         palette = qApp.palette()
#         palette.setBrush(QPalette.Base, palette.button())
#         self.lineEdit().setPalette(palette)

#         # Use custom delegate
#         self.setItemDelegate(CheckableComboBox.Delegate())

#         # Update the text when an item is toggled
#         self.model().dataChanged.connect(self.updateText)

#         # Hide and show popup when clicking the line edit
#         self.lineEdit().installEventFilter(self)
#         self.closeOnLineEditClick = False

#         # Prevent popup from closing when clicking on an item
#         self.view().viewport().installEventFilter(self)

#     def resizeEvent(self, event):
#         # Recompute text to elide as needed
#         self.updateText()
#         super().resizeEvent(event)

#     def eventFilter(self, object, event):

#         if object == self.lineEdit():
#             if event.type() == QEvent.MouseButtonRelease:
#                 if self.closeOnLineEditClick:
#                     self.hidePopup()
#                 else:
#                     self.showPopup()
#                 return True
#             return False

#         if object == self.view().viewport():
#             if event.type() == QEvent.MouseButtonRelease:
#                 index = self.view().indexAt(event.pos())
#                 item = self.model().item(index.row())

#                 if item.checkState() == Qt.Checked:
#                     item.setCheckState(Qt.Unchecked)
#                 else:
#                     item.setCheckState(Qt.Checked)
#                 return True
#         return False

#     def showPopup(self):
#         super().showPopup()
#         # When the popup is displayed, a click on the lineedit should close it
#         self.closeOnLineEditClick = True

#     def hidePopup(self):
#         super().hidePopup()
#         # Used to prevent immediate reopening when clicking on the lineEdit
#         self.startTimer(100)
#         # Refresh the display text when closing
#         self.updateText()

#     def timerEvent(self, event):
#         # After timeout, kill timer, and reenable click on line edit
#         self.killTimer(event.timerId())
#         self.closeOnLineEditClick = False

#     def updateText(self):
#         texts = []
#         for i in range(self.model().rowCount()):
#             if self.model().item(i).checkState() == Qt.Checked:
#                 texts.append(self.model().item(i).text())
#         text = ", ".join(texts)

#         # Compute elided text (with "...")
#         metrics = QFontMetrics(self.lineEdit().font())
#         elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
#         self.lineEdit().setText(elidedText)

#     def addItem(self, text, data=None):
#         item = QStandardItem()
#         item.setText(text)
#         if data is None:
#             item.setData(text)
#         else:
#             item.setData(data)
#         item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
#         item.setData(Qt.Unchecked, Qt.CheckStateRole)
#         self.model().appendRow(item)

#     def addItems(self, texts, datalist=None):
#         for i, text in enumerate(texts):
#             try:
#                 data = datalist[i]
#             except (TypeError, IndexError):
#                 data = None
#             self.addItem(text, data)

#     def currentData(self):
#         # Return the list of selected items data
#         res = []
#         for i in range(self.model().rowCount()):
#             if self.model().item(i).checkState() == Qt.Checked:
#                 res.append(self.model().item(i).data())
#         return res