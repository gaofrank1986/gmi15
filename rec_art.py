from PyQt5.QtWidgets import QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox,QFileDialog
from PyQt5.uic import loadUi
import traceback
import json
import os
import shutil
from ocr import ocr
class Rec_Artifact(QDialog):
    def __init__(self,data,name):
        super(Rec_Artifact,self).__init__()
        loadUi("./data/ui/artifacts.ui",self)        
        self.pb_savefile.clicked.connect(self.savefile)
        self.pb_openfile.clicked.connect(self.openfile)
        
        self.pos = {'理之冠':'head','时之沙':'glass','空之杯':'cup','生之花':'flower','死之羽':'feather'}
        self.plist = ['暴击','暴伤','攻击','属伤','物伤','防御','生命','治疗','精通','充能']
        self.dlist = ['cr','cd','ar','ed','dphys','dr','hr','dheal','em','ef']
        
        self.name = name
        self.path = "./data/compare/"+name+"/"
        alist = list(data.keys())
        alist = list(set([_[:-1] for _ in  alist]))
        alist[0] = '无'
        self.elist = alist
        # for i in self.plist:
        self.cb_aeffect.addItems(alist)
        self.cb_main.addItems(self.plist)

     
        
    def savefile(self):

        pos2={self.plist[i]:self.dlist[i] for i in range(len(self.plist))}
        
        folder = self.pos[self.cb_pos.currentText()]
        path = QFileDialog.getSaveFileName(self, 'Open a file', self.path+folder,'圣遗物数据文件 (*.json)')
        data = {"pos":"","main":{},"sub":{},"set":"","cmt":""}
        
        tmp ={}
        tmp['cr'] = self.digit_cr.value() 
        tmp['cd'] = self.digit_cd.value()
        tmp['dr'] = self.digit_dr.value()
        tmp['ar'] = self.digit_ar.value()
        tmp['cd'] = self.digit_cd.value()
        tmp['sa'] = self.digit_sa.value()
        tmp['sd'] = self.digit_sd.value()
        tmp['sh'] = self.digit_sh.value()
        tmp['hr'] = self.digit_hr.value()
        tmp['em'] = self.digit_em.value()
        tmp['ef'] = self.digit_ef.value()
        
        data['sub'] = tmp
        data['main'] = {pos2[self.cb_main.currentText()]:self.digit_main.value()}
        data["pos"] = self.cb_pos.currentText()
        data["set"] = self.cb_aeffect.currentText()
        data['cmt'] = self.le_cmt.text()
        if path != ('', ''):
            # print(path)
            with open(path[0], 'w', encoding='utf-8') as fp:
                json.dump(data, fp,indent = 4,ensure_ascii=False)

    def openfile(self):
        pos={'理之冠':'head','时之沙':'glass','空之杯':'cup','生之花':'flower','死之羽':'feather'}
        
        folder = pos[self.cb_pos.currentText()]
        path = QFileDialog.getOpenFileName(self, 'Open a file', self.path+folder,'圣遗物数据文件 (*.*)')
        if path != ('', ''):
            ans = ocr(path[0])['words_result']
            ans = [i['words'] for i in ans][:8]
            print(ans)
                   
            # self.digit_cr.setValue(data['sub']['cr']) 
            # self.digit_cd.setValue(data['sub']['cd']) 
            # self.digit_dr.setValue(data['sub']['dr']) 
            # self.digit_ar.setValue(data['sub']['ar']) 
            # self.digit_sa.setValue(data['sub']['sa']) 
            # self.digit_sd.setValue(data['sub']['sd']) 
            # self.digit_hr.setValue(data['sub']['hr']) 
            # self.digit_em.setValue(data['sub']['em']) 
            # self.digit_sh.setValue(data['sub']['sh']) 
            # self.digit_ef.setValue(data['sub']['ef']) 
            
            # for i in data['main']:
            self.cb_main.setCurrentIndex(self.dlist.index(i))
            self.digit_main.setValue(data['main'][i])
            # self.le_cmt.setText(data['cmt'])
            tmp = list(self.pos.keys())
            self.cb_pos.setCurrentIndex(tmp.index(ans[1]))        
            # self.cb_aeffect.setCurrentIndex(self.elist.index(data["set"]))        

    def openfile2(self):
        pos={'理之冠':'head','时之沙':'glass','空之杯':'cup','生之花':'flower','死之羽':'feather'}
        
        folder = pos[self.cb_pos.currentText()]
        path = QFileDialog.getOpenFileName(self, 'Open a file', self.path+folder,'圣遗物数据文件 (*.json)')
        if path != ('', ''):
            with open(path[0], 'r', encoding='UTF-8') as fp:
                data = json.load(fp)     
                
            self.digit_cr.setValue(data['sub']['cr']) 
            self.digit_cd.setValue(data['sub']['cd']) 
            self.digit_dr.setValue(data['sub']['dr']) 
            self.digit_ar.setValue(data['sub']['ar']) 
            self.digit_sa.setValue(data['sub']['sa']) 
            self.digit_sd.setValue(data['sub']['sd']) 
            self.digit_hr.setValue(data['sub']['hr']) 
            self.digit_em.setValue(data['sub']['em']) 
            self.digit_sh.setValue(data['sub']['sh']) 
            self.digit_ef.setValue(data['sub']['ef']) 
            
            for i in data['main']:
                self.cb_main.setCurrentIndex(self.dlist.index(i))
                self.digit_main.setValue(data['main'][i])
            self.le_cmt.setText(data['cmt'])
            tmp = list(self.pos.keys())
            self.cb_pos.setCurrentIndex(tmp.index(data["pos"]))        
            self.cb_aeffect.setCurrentIndex(self.elist.index(data["set"]))  
            
    def display(self):
        if not os.path.exists("./data/compare/"+self.name):
            shutil.copytree(src="./data/compare/dummy",dst="./data/compare/"+self.name)
        self.exec_()
     
    def update(self,name):
        self.name = name
        self.path = "./data/compare/"+name+"/"          



