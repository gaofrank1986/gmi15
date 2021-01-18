from PyQt5.QtWidgets import QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox,QFileDialog,QComboBox,QDoubleSpinBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

import traceback
import json
import os
import shutil
from ocr import ocr,parse
import logging

def ps(s):
    s = s.replace('(测试无效果)','')
    s = s[:-1]
    return(s)

class Rec_Artifact(QDialog):
    def __init__(self,data,name,sbar):
        super(Rec_Artifact,self).__init__()
        loadUi("./data/ui/artifacts2.ui",self)        
        self.pb_savefile.clicked.connect(self.savefile)
        self.pb_openfile.clicked.connect(self.openfile)
        self.pb_openimg.clicked.connect(self.openimgfile)
        
        self.pos = {'理之冠':'head','时之沙':'glass','空之杯':'cup','生之花':'flower','死之羽':'feather'}
        self.plist = ['暴击','暴伤','攻击%','攻击(固定)','属伤','物伤','防御','生命%','生命(固定)','治疗','精通','充能']
        self.dlist = ['cr','cd','ar','sa','ed','dphys','dr','hr','sh','dheal','em','ef']

        self.slist = ['暴击','暴伤','攻击%','攻击(固定)','防御%','防御(固定)','生命%','生命(固定)','精通','充能']
        self.tlist = ['cr','cd','ar','sa','dr','sd','hr','sh','em','ef']
        
        self.name = name
        self.path = "./data/compare/"+name+"/"
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
        
        # self.label = QLabel(self)

     
        
    def savefile(self):
        try:

            pos2={self.plist[i]:self.dlist[i] for i in range(len(self.plist))}
            pos1={self.slist[i]:self.tlist[i] for i in range(len(self.slist))}
            
            folder = self.pos[self.cb_pos.currentText()]
            path = QFileDialog.getSaveFileName(self, 'Open a file', self.path+folder,'圣遗物数据文件 (*.json)')
            data = {"pos":"","main":{},"sub":{},"set":"","cmt":""}
            

            for i in range(1,5):
                pos = pos1[self.findChild(QComboBox,"cb_sub_"+str(i)).currentText()]
                assert(pos not in data["sub"])
                data["sub"][pos] = self.findChild(QDoubleSpinBox,"digit_sub_"+str(i)).value()
                
            
            data['main'] = {pos2[self.cb_main.currentText()]:self.digit_main.value()}
            data["pos"] = self.cb_pos.currentText()
            data["set"] = self.cb_aeffect.currentText()
            data['cmt'] = self.le_cmt.text()
            if path != ('', ''):
                # print(path)
                with open(path[0], 'w', encoding='utf-8') as fp:
                    json.dump(data, fp,indent = 4,ensure_ascii=False)
        except:
            self.sbar.showMessage("圣遗物文件存储错误")
            logging.getLogger('1').error(traceback.format_exc())

    def openimgfile(self):
        try:
            trans = {'攻击力%':'ar','防御力%':'dr','生命值%':'hr','生命值':'sh','元素充能效率%':'ef','暴击率%':'cr','暴击伤害%':'cd','攻击力':'sa','元素精通':'em','防御力':'sd'}
            path = QFileDialog.getOpenFileName(self, 'Open a file', "./data/",'圣遗物数据文件 (*.*)')
            if path != ('', ''):
                pixmap = QPixmap(path[0]).scaled(370,591, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.label_pic.setPixmap(pixmap)
                self.label_pic.resize(pixmap.width(),pixmap.height())
                
                
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
        except:
            self.sbar.showMessage("圣遗物图像读取错误")
            logging.getLogger('1').error(traceback.format_exc())                  



            
    def openfile(self):
        try:
            
            folder = self.pos[self.cb_pos.currentText()]
            path = QFileDialog.getOpenFileName(self, 'Open a file', self.path+folder,'圣遗物数据文件 (*.json)')
            if path != ('', ''):
                with open(path[0], 'r', encoding='UTF-8') as fp:
                    data = json.load(fp)     
                    
                filtered = {}
                for i in data['sub']:
                    if data['sub'][i]>0:
                        filtered[i] = data['sub'][i]
                assert (len(filtered) <= 4)

                N=1
                for i in filtered:
                    pass
                    self.findChild(QComboBox,"cb_sub_"+str(N)).setCurrentIndex(self.tlist.index(i))
                    self.findChild(QDoubleSpinBox,"digit_sub_"+str(N)).setValue(filtered[i])
                    N+=1

                
                for i in data['main']:
                    self.cb_main.setCurrentIndex(self.dlist.index(i))
                    self.digit_main.setValue(data['main'][i])
                self.le_cmt.setText(data['cmt'])
                tmp = list(self.pos.keys())
                self.cb_pos.setCurrentIndex(tmp.index(data["pos"]))        
                self.cb_aeffect.setCurrentIndex(self.elist.index(data["set"]))  
        except:
            self.sbar.showMessage("圣遗物文件读取错误")
            logging.getLogger('1').error(traceback.format_exc())
            
    def display(self):
        if not os.path.exists("./data/compare/"+self.name):
            shutil.copytree(src="./data/compare/dummy",dst="./data/compare/"+self.name)
        self.exec_()
     
    def update(self,name):
        self.name = name
        self.path = "./data/compare/"+name+"/"          



