from PyQt5.QtWidgets import QDialog,QLineEdit,QLabel,QSpinBox,QTableWidgetItem
from PyQt5.uic import loadUi
import traceback
import json
from utility import extract_name3
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

class Change_Action(QDialog):
    def __init__(self,data,sbar):
        super(Change_Action,self).__init__()
        loadUi("./data/ui/change_action.ui",self)       
        # self.le_a.editingFinished.connect(lambda: self.checkline('a'))
        # self.le_e.editingFinished.connect(lambda: self.checkline('e'))
        # self.le_q.editingFinished.connect(lambda: self.checkline('q'))
        # self.le_shld.editingFinished.connect(lambda: self.checkline('shld'))
        # self.le_heal.editingFinished.connect(lambda: self.checkline('heal'))
        self.le_a.textEdited.connect(lambda: self.checkline('a'))
        self.le_e.textEdited.connect(lambda: self.checkline('e'))
        self.le_q.textEdited.connect(lambda: self.checkline('q'))
        self.le_shld.textEdited.connect(lambda: self.checkline('shld'))
        self.le_heal.textEdited.connect(lambda: self.checkline('heal'))
        self.pb_save.clicked.connect(self.save)
        
        self._data = data
        self.sbar=sbar
        
        N=0
        jb_ds={'ks':'扩散伤害','cd':'超导伤害','gd':'感电伤害','gz':'过载伤害'}
        for i in ['ks','gd','cd','gz']:
            item =  QTableWidgetItem(i)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tb_jb.insertRow(N)
            self.tb_jb.setItem(N,0,item)
            item = QTableWidgetItem("剧变反应")
            self.tb_jb.setItem(N,2,item)
            item = QTableWidgetItem(jb_ds[i])
            self.tb_jb.setItem(N,1,item)
            
            s = "攻击"         
            item = QTableWidgetItem(s)
            self.tb_jb.setItem(N,3,item)        
            N+=1
          
            
        header = self.tb_jb.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        # self._cname = cname
        # self._clevel = 'c'+str(int(self.cb_cnum.currentText()))  

            
    def checkline(self,s):
        assert(s in['a','e','q','heal','shld'])
        fm = self.findChild(QLineEdit,"le_"+s).text()
        status = self.findChild(QLabel,"lb_status_"+s)
        if fm!='':
            try:
                tmp = fm.split('+')
                for i in tmp:
                    assert(i.count('*')<2)
                    tmp2 = i.split('*')
                    assert(tmp2[-1] in self._cdata['ratios'] or tmp2[-1] in ['ks','cd','gz','gd'])
                    if not(tmp2[-1] in ['ks','cd','gz','gd']):
                        atk_t = self._cdata['atk_type'][tmp2[-1]]
                        # print(atk_t,s)
                        if s in  ['a','e','q']:
                            assert atk_t in ['elem','phys','env']
                        if s in  ['shld','heal']:
                            assert atk_t in ['shld','base','heal']

                status.setText('正确')
            except:
                status.setText('错误')
        else:
            status.setText('正确')
            
    def save(self):
        try:
            character = self.cname
            cstl = 'c'+str(int(self.clevel))        
            rnd = dict()
            self._cdata[cstl] = {}
            self._cdata[cstl]['action_def'] = {}
            for i in ['a','e','q','shld','heal']:
                assert self.findChild(QLabel,"lb_status_"+i).text() == '正确'
                self._cdata[cstl]['action_def'][i] = self.findChild(QLineEdit,"le_"+i).text()
                
            for i in ['a','e','q']:
                    rnd[i]= self.findChild(QSpinBox,"sb_rnd_"+i).value()
            self._cdata[cstl]['enchant_ratio'] = self.dsb_enchant.value()
            self._cdata[cstl]['round'] = rnd
            self._cdata[cstl]['cmts']= self.pte_cmts.toPlainText()

            tmp =['c0','c1','c2','c3','c4','c5','c6']
            tmp2 = {_:'' for _ in ('a','e','q','shld','heal')}
            for i in tmp:
                if not i in self._cdata:
                    self._cdata[i] = {}
                self._cdata[i]['enchant_ratio'] = self._cdata[i].get('enchant_ratio',0)
                self._cdata[i]['action_def']= self._cdata[i].get('action_def',tmp2)
                self._cdata[i]['round']= self._cdata[i].get('round',{'a':0,'e':0,'q':0})

            for i in ['round','enchant_ratio','action_def']:
                if i in self._cdata:
                    self._cdata.pop(i)

            with open('./data/character/'+character+'.json', 'w', encoding='utf-8') as fp:
                json.dump(self._cdata, fp,indent = 4,ensure_ascii=False)
            self.sbar.showMessage("技能保存成功",1000)
        except Exception as e:
            self.sbar.showMessage("技能保存失败",1000)
            logging.getLogger('1').info("Error: {}".format(e))
            logging.getLogger('1').info(traceback.format_exc())
            traceback.print_exc()
            
    def update(self,cname,clevel):
        self.cname = cname
        self.clevel = clevel

    def display(self):
        try:
            # print(self._data)
            character = self.cname
            cstl = 'c'+str(int(self.clevel))  

            with open('./data/character/'+character+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            self._cdata = data
            self.lb_name.setText(data['name'])
            c_trans={"c0":"0命","c1":"1命","c2":"2命","c3":"3命","c4":"4命","c5":"5命","c6":"6命"}
            self.lb_c.setText(c_trans[cstl])
            while (self.tb_skill.rowCount() > 0):
                self.tb_skill.removeRow(0)
            N = 0
            for i in data['ratios']:
                item =  QTableWidgetItem(i)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.tb_skill.insertRow(N)
                self.tb_skill.setItem(N,0,item)
                text = extract_name3(data['atk_type'][i])
                item = QTableWidgetItem(text)
                self.tb_skill.setItem(N,2,item)
                item = QTableWidgetItem(data['ratio_cmt'][i])
                self.tb_skill.setItem(N,1,item)
                
                s = "atk"
                if "rebase" in data and i in data["rebase"]:
                    s=data["rebase"][i]
                if data['atk_type'][i] in ['buff','base']:
                    s='none'
                name_trans={'atk':'攻击','def':'防御','life':'生命','none':'无'}
                s = name_trans[s]
                    
                item = QTableWidgetItem(s)
                self.tb_skill.setItem(N,3,item)                

                if "skill_num" in data and i in data["skill_num"]:
                    s=data["skill_num"][i]
                else:
                    s = "1"
                item = QTableWidgetItem(s)
                self.tb_skill.setItem(N,4,item)                


                N+=1

            header = self.tb_skill.horizontalHeader()       
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

            


            for i in ['a','e','q','shld','heal']:           

                self.findChild(QLineEdit,"le_"+i).setText((data[cstl]['action_def'][i]))
                self.checkline(i)                                                                     
            for i in ['a','e','q']:           
                self.findChild(QSpinBox,"sb_rnd_"+i).setValue(data[cstl]['round'][i])                                                            
            self.dsb_enchant.setValue(data[cstl]['enchant_ratio'])
            if 'cmts' in data[cstl]:
                self.pte_cmts.setPlainText(data[cstl]['cmts'])
            
            
            while (self.tb_ratio.rowCount() > 0):
                self.tb_ratio.removeRow(0)
            N = 0
            for i in data['ratios']:
                item =  QTableWidgetItem(i)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.tb_ratio.insertRow(N)
                self.tb_ratio.setItem(N,0,item)

                K=1
                for j in data['ratios'][i]:
                    text = "{:6.1f}%".format(float(j))
                    item = QTableWidgetItem(text)
                    self.tb_ratio.setItem(N,K,item)  
                    K+=1           

                N+=1

            header = self.tb_ratio.horizontalHeader()       
            for i in range(16):
                header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
                
                
                
                
                
                
        
            
            self.tabs.setCurrentIndex(0)
            
            
            
            
            
            

            self.exec_()
        except Exception as e:
            self.sbar.showMessage("技能显示失败",1000)
            print("Error: ", e)
            traceback.print_exc()