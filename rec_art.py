from PyQt5.QtWidgets import QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox,QFileDialog,QComboBox,QDoubleSpinBox,QDialogButtonBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

import traceback
import json
import os
import shutil
from ocr import ocr,parse
import logging
from db_setup import Entry,db_session

def ps(s):
    s = s.replace('(测试无效果)','')
    s = s[:-1]
    return(s)

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
    def Cancel(self):
        # self.if_OK = True
        self.close()         
      

class Rec_Artifact(QDialog):
    def __init__(self,data,name,sbar):
        super(Rec_Artifact,self).__init__()
        loadUi("./data/ui/artifacts2.ui",self)        
        # self.pb_savefile.clicked.connect(self.savefile)
        self.pb_link_pic.clicked.connect(self.new_pic_link)
        self.pb_clear.clicked.connect(self.clear)
        self.pb_savedb.clicked.connect(self.savedb)
        self.pb_lookupdb.clicked.connect(self.lookupdb)
        # self.pb_openfile.clicked.connect(self.openfile)
        self.pb_openimg.clicked.connect(self.openimgfile)
        self.pb_db_del.clicked.connect(self.delete_entry)
        self.pb_db_update.clicked.connect(self.renew_entry)
        
        self.pos = {'理之冠':'head','时之沙':'glass','空之杯':'cup','生之花':'flower','死之羽':'feather'}
        self.plist = ['暴击','暴伤','攻击%','攻击(固定)','属伤','物伤','防御','生命%','生命(固定)','治疗','精通','充能']
        self.dlist = ['cr','cd','ar','sa','ed','dphys','dr','hr','sh','dheal','em','ef']

        self.slist = ['暴击','暴伤','攻击%','攻击(固定)','防御%','防御(固定)','生命%','生命(固定)','精通','充能']
        self.tlist = ['cr','cd','ar','sa','dr','sd','hr','sh','em','ef']
        
        self.name = name
        # self.path = "./data/compare/"+name+"/"
        self.sbar = sbar
        alist = list(data.keys())
        alist = list(ps(_) for _ in  alist)
        alist[0] = '无'
        self.elist = alist
        print(self.elist)
        # for i in self.plist:
        self.cb_aeffect.addItems(alist)
        self.cb_main.addItems(self.plist)
        self.cb_sub_1.addItems(self.slist)
        self.cb_sub_2.addItems(self.slist)
        self.cb_sub_3.addItems(self.slist)
        self.cb_sub_4.addItems(self.slist)
        
        # init_db()
        
        self.cached = None
        self.look_up = {}
    
        

    def load_entry(self):
        aaa = self.cb_db.currentIndex()
        assert aaa in self.look_up
        print (self.look_up)
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
        for i in range(1,5):
            self.findChild(QComboBox,"cb_sub_"+str(i)).setCurrentIndex(self.tlist.index(getattr(r1,'sub'+str(i)+'0')))
            self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).setValue(getattr(r1,'sub'+str(i)+'1'))
            self.cb_aeffect.setCurrentIndex(self.elist.index(r1.aset))
            self.le_cmt.setText(r1.cmts)
        self.label_id.setText("ID: {}".format(self.look_up[aaa]))
   
    def delete_entry(self):
        aaa = self.cb_db.currentIndex()
        assert aaa in self.look_up
        print (self.look_up)
        r1 = db_session.query(Entry).filter(Entry.id == self.look_up[aaa]).delete()
        db_session.commit()
        self.lookupdb()
        
    
    def renew_entry(self):
        try:
            aaa = self.cb_db.currentIndex()
            assert aaa in self.look_up
            r1 = db_session.query(Entry).filter(Entry.id == self.look_up[aaa]).first()
            
            pos2={self.plist[i]:self.dlist[i] for i in range(len(self.plist))}
            pos1={self.slist[i]:self.tlist[i] for i in range(len(self.slist))}
            
            saved_pos=[]

            r1.pos = self.cb_pos.currentText()
            r1.aset = self.cb_aeffect.currentText()
            r1.cmts = self.le_cmt.text()
            r1.main0 = pos2[self.cb_main.currentText()]
            saved_pos.append(pos2[self.cb_main.currentText()])
            r1.main1 = self.digit_main.value()
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
            
            self.sbar.showMessage("圣遗物数据存储成功")

        except:
            db_session.roll_back()
            self.sbar.showMessage("圣遗物文件存储错误")
            logging.getLogger('1').error(traceback.format_exc())

    def lookupdb(self):
        try:
            try:
                self.cb_db.currentIndexChanged.disconnect(self.load_entry)
            except:
                pass

            self.cb_db.clear()
            N=0
            for i in db_session.query(Entry).all():
                self.cb_db.addItem(i.name)
                self.look_up[N] = i.id
                N+=1
            # self.sbar.showMessage("圣遗物数据存储成功")
            # print(1)
            self.cb_db.currentIndexChanged.connect(self.load_entry)
            self.load_entry()
            self.sbar.showMessage("圣遗物数据库加载成功")

        except:
            self.sbar.showMessage("圣遗物数据库加载失败")
            logging.getLogger('1').error(traceback.format_exc())    
        
    def savedb(self):
        try:
            self.aaa = RName()
            self.aaa.exec_()
            # self.aaa.show()
            print(self.aaa.if_OK,self.aaa.name)
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
                
                self.sbar.showMessage("圣遗物数据存储成功")

        except:
            db_session.roll_back()
            self.sbar.showMessage("圣遗物文件存储错误")
            logging.getLogger('1').error(traceback.format_exc())


    def new_pic_link(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', "./",'圣遗物图像文件 (*.*)')
        if path != ('', ''):
            pixmap = QPixmap(path[0]).scaled(370,591, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label_pic.setPixmap(pixmap)
            self.label_pic.resize(pixmap.width(),pixmap.height())
            with open(file=path[0],mode='rb',) as fp:
                self.cached = fp.read()      
                      
    def openimgfile(self):
        try:
            self.clear()
            trans = {'攻击力%':'ar','防御力%':'dr','生命值%':'hr','生命值':'sh','元素充能效率%':'ef','暴击率%':'cr','暴击伤害%':'cd','攻击力':'sa','元素精通':'em','防御力':'sd'}
            path = QFileDialog.getOpenFileName(self, 'Open a file', "./",'圣遗物图像文件 (*.*)')
            if path != ('', ''):
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
                print(ans)
                ans2 = parse(ans)
                # print(ans2)
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
            self.sbar.showMessage("圣遗物图像读取成功")

        except:
            self.sbar.showMessage("圣遗物图像读取错误")
            logging.getLogger('1').error(traceback.format_exc())                  



            
    # def openfile(self):
    #     try:
    #         self.clear()

    #         folder = self.pos[self.cb_pos.currentText()]
    #         path = QFileDialog.getOpenFileName(self, 'Open a file', self.path+folder,'圣遗物数据文件 (*.json)')
    #         if path != ('', ''):
    #             with open(path[0], 'r', encoding='UTF-8') as fp:
    #                 data = json.load(fp)     
                    
    #             filtered = {}
    #             for i in data['sub']:
    #                 if data['sub'][i]>0:
    #                     filtered[i] = data['sub'][i]
    #             assert (len(filtered) <= 4)

    #             N=1
    #             for i in filtered:
    #                 pass
    #                 self.findChild(QComboBox,"cb_sub_"+str(N)).setCurrentIndex(self.tlist.index(i))
    #                 self.findChild(QDoubleSpinBox,"digit_sub_"+str(N)).setValue(filtered[i])
    #                 N+=1

                
    #             for i in data['main']:
    #                 self.cb_main.setCurrentIndex(self.dlist.index(i))
    #                 self.digit_main.setValue(data['main'][i])
    #             self.le_cmt.setText(data['cmt'])
    #             tmp = list(self.pos.keys())
    #             self.cb_pos.setCurrentIndex(tmp.index(data["pos"]))        
    #             self.cb_aeffect.setCurrentIndex(self.elist.index(data["set"]))  
    #         self.sbar.showMessage("圣遗物数据读取成功")

    #     except:
    #         self.sbar.showMessage("圣遗物文件读取错误")
    #         logging.getLogger('1').error(traceback.format_exc())
            
    def display(self):
        self.exec_()
     
    def update(self,name):
        self.name = name
        # self.path = "./data/compare/"+name+"/"          



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
        except:
            self.sbar.showMessage("圣遗物界面clear错误")
            logging.getLogger('1').error(traceback.format_exc())