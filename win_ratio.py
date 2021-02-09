from PyQt5.QtWidgets import QDialog,QLineEdit,QLabel,QSpinBox,QTableWidgetItem,QDialogButtonBox
from PyQt5.uic import loadUi
import traceback
import json
from utility import extract_name3
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from db_setup import CRatio,db_session
import re
class Win_Ratio(QDialog):
    def __init__(self,role,sbar):
        super(Win_Ratio,self).__init__()
        loadUi("./data/ui/win_ratio.ui",self)       
        # self.pb_save.clicked.connect(self.save)

        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.save)
        # self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.Cancel)
        # self.table_ratio.cellChanged.connect(self.update)
        # self._data = data
        self.sbar=sbar
        self.role = role
        self.cnum = 'c0'
        self.wpn = ''
        

        header = self.table_ratio.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header = self.table_ratio.verticalHeader()       
        header.setVisible(False)

            
    def save(self):
        try:
            ckeys =[]
            cvalues = []
            wkeys =[]
            wvalues = []
            for i in range(self.table_ratio.rowCount()):
                key = self.table_ratio.item(i,0).text()
                value = self.table_ratio.item(i,3).text()
                # for i in value:
                # print(key,value)
                try:
                    assert key.count('.')<=1
                    key = key.replace('.','')
                    assert key.isalnum()
                except:
                    # print("error",key,i)
                    self.sbar.showMessage('输入值错误')
                    raise ValueError
                if key not in ['w1','w2','w3']:
                    ckeys.append(key)
                    cvalues.append(value)
                else:
                    wkeys.append(key)
                    wvalues.append(value)
                
            cratio = db_session.query(CRatio).filter(CRatio.name==self.role+'_'+self.cnum).first()
            cratio.values = '||'.join(cvalues)        
            db_session.commit()
            if len(wkeys)!=0 and self.wpn!='':
                cratio = db_session.query(CRatio).filter(CRatio.name==self.wpn).first()
                cratio.values = '||'.join(wvalues)        
                db_session.commit() 
            self.sbar.showMessage('覆盖率存储成功')
        except:
            db_session.rollback()
            traceback.print_exc()
            logging.getLogger('1').info(traceback.format_exc())
            self.sbar.showMessage('覆盖率存储错误')        
            
    def update(self,row,column):
        # self.cname = role
        print(row,column)

    def display(self):
        try:
            logging.getLogger('1').info('{}{}'.format(self.role,self.cnum,self.wpn))
            while (self.table_ratio.rowCount() > 0):
                self.table_ratio.removeRow(0)
            
            
            with open('./data/character/'+self.role+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            data = data['buffs']
            
            self.show_value(data,self.role+'_'+self.cnum)
            
            if not self.wpn == '':
                loc = self.wpn.split('_')[0]        
                key = self.wpn.split('_')[1]        
                with open('./data/weapon/'+loc+'.json', 'r', encoding='UTF-8') as fp:
                    data = json.load(fp)
                data = data[key]['buffs']
                self.show_value(data,self.wpn)        

            self.exec_()
        except Exception as e:
            self.sbar.showMessage("技能显示失败",1000)
            print("Error: ", e)
            traceback.print_exc()
            
            
            
    def show_value(self,data,fltr):
            saved = db_session.query(CRatio).filter(CRatio.name==fltr).first()
            keys = [_ for _ in data]
            desc = [data[_][3] for _ in data]
            cond = ['{}'.format(data[_][0]) for _ in data]
            print(cond)
            print(keys)
            effct = ['{}'.format(data[_][1]) for _ in data]
            values = [str(data[_][2]) for _ in data]
            valid = False
            if saved is not None:
                cratio = saved
                try:
                    keys2 = cratio.keys.split('/')
                    values2 = cratio.values.split('||')
                    print(keys2)
                    print(values2)
                    print(len(keys2),len(values2))
                    print(len(keys2),len(keys))
                    assert(len(keys2)==len(values2))
                    assert(len(keys2)==len(keys))
                    for i in values2:
                        print(i,re.match(r'^-?\d+(?:\.\d+)$', i),i.isalnum())
                        if (re.match(r'^-?\d+(?:\.\d+)$', i) is None) and not(i.isalnum()):
                            raise ValueError 
                    valid = True
                except:
                    pass
            
            if not valid:
                if saved is None:
                    cratio = CRatio()
                else:
                    cratio = saved
                cratio.name = fltr
                cratio.keys = '/'.join(keys)
                cratio.values = '||'.join(values)
                if saved is None:
                    db_session.add(cratio)
                db_session.commit()

                
                
            keys2 = cratio.keys.split('/')
            values2 = cratio.values.split('||')


            base = self.table_ratio.rowCount()
            # print("base",base)

            for i in range(len(keys2)):
                if keys2[i]=='':
                    continue
                item =  QTableWidgetItem(keys2[i])
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.table_ratio.insertRow(base+i)
                self.table_ratio.setItem(base+i,0,item)
                item = QTableWidgetItem(values2[i])
                self.table_ratio.setItem(base+i,3,item)
                item = QTableWidgetItem(cond[i])
                self.table_ratio.setItem(base+i,1,item)
                item = QTableWidgetItem(desc[i])
                self.table_ratio.setItem(base+i,4,item) 
                item = QTableWidgetItem(effct[i])
                self.table_ratio.setItem(base+i,2,item) 