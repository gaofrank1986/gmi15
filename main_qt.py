import numpy as np
import json
from copy import deepcopy
import logging
import os
from collections import OrderedDict
from basic import Articraft
from character import Character
from utility import extract_name2,run_thru,MyDialog,parse_formula
import traceback
from PyQt5.QtWidgets import QApplication,QTableView,QMainWindow,QTableWidgetItem,QCheckBox,QDialog
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("./data/test.ui",self)

        self._data = {}
        self._wdata = {}
        self._aeffect = {}
        
        self.btn_run.clicked.connect(self.run) 
        self.btn_load_wp.clicked.connect(self.new_win) 
        self.pb_action.clicked.connect(self.show_action) 

        self.cb_name.currentIndexChanged.connect(self.reset)
        self.cb_wp.currentIndexChanged.connect(self.reset_table)
        self.cb_cnum.currentIndexChanged.connect(self.reset_table)
        self.cb_skill.currentIndexChanged.connect(self.reset_table)
        self.cb_refine.currentIndexChanged.connect(self.reset_table)
        # self.b_read.clicked.connect(self.read_sub)
        # self.b_save.clicked.connect(self.save_sub)
        # self.b_save_main.clicked.connect(self.generate_mainlist)
        # self.b_read_main.clicked.connect(self.read_mainlist)
        self.b_read.hide()
        self.b_save.hide()
        self.b_read_main.hide()
        self.b_save_main.hide()
        
        self.read_mainlist()
        self.read_sub()

        
        path = "./data/info.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._data = data      
        
        path = "./data/artifact_effects.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._aeffect = data     
        
        
        
        self.cb_name.addItems(list(self._data.keys()))
        self.cb_aeffect1.addItems(list(self._aeffect.keys()))
        self.cb_aeffect2.addItems(list(self._aeffect.keys()))
        
        self.load_info()
        self.dlg = MyDialog(self)
        self.win_action = QDialog(self)
        # self.btn_load_wp.hide()
  
    def show_action(self):
        try:
            desc = ['普攻','元素战技','元素爆发','重击']
            prop_name =['a','e','q','h']
            div1 = "==========\n"
            loadUi("./data/win_action.ui",self.win_action)
            character = self._data[self.cb_name.currentText()]['name']
            cstl = 'c'+str(int(self.cb_cnum.currentText()))

            ans =''
            with open('./data/character/'+character+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            tmp = self.win_action.info_action
            for i in range(4):
                if data['formula'][cstl][i]!='':
                    rnd = data['round'][prop_name[i]]
                    ans+="{}({}轮)\n{}".format(desc[i],rnd,div1)
                    formula = data['formula'][cstl][i]
                    for entry in parse_formula(formula):
                        if entry[0] == 'ks':
                            ans += '扩散伤害'
                            ans += '  x {}'.format(entry[1])
                        else:
                            ans += data['ratio_cmt'][entry[0]]
                            ans += '  x {}'.format(entry[1])
                        ans+='\n'
                else:
                    rnd = data['round'][prop_name[i]]
                    ans+="{}({}轮)\n{}".format(desc[i],rnd,div1)
                    ans+='无定义\n'
                ans+='\n'
            tmp.setPlainText(ans)
            self.win_action.exec_()
        except Exception as e:
            print("Error: ", e)
        
        
        
    #======================================
    def new_win(self):

        self.dlg.setWindowTitle("计算日志")
        self.dlg.exec_()

    def reset(self):
        self.cb_wp.clear()
        self.cb_cnum.clear()
        self.label.setText("")
        self.reset_table()
        self.load_info()

    def reset_table(self):
        self.label.setText("")
        for i in range(4):
            for j in range(4):
                self.tbl_2.setItem(i, j,QTableWidgetItem(""))



    
    def load_info(self):
        self.cb_wp.clear()
        self.cb_cnum.clear()
        self.label.setText("")

        wkind = self._data[self.cb_name.currentText()]['w']
        path = "./data/weapon/"+wkind+".json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        ans = []        
        for wp in data: 
            self._wdata[data[wp]['name']] = wp         
            ans.append(data[wp]['name'])
        self.cb_wp.addItems(ans)
        self.cb_cnum.addItems(self._data[self.cb_name.currentText()]['c'])
    
    def run(self):
        logger = logging.getLogger()
        self.dlg.clear()
        self.reset_table()
        logging.info("=================日志开始================")
        logging.info("精确显示伤害后可复制到其他文本编辑器进行查询")
        logging.info("========================================")

        try:
            self.save_sub()
            self.save_mainlist()
            
            skill_level = int(self.cb_skill.currentText())
            constellation = int(self.cb_cnum.currentText())
            character = self._data[self.cb_name.currentText()]['name']
            weapon = self._wdata[self.cb_wp.currentText()]
            refine = int(self.cb_refine.currentText())


            self.label.setText("{} {} {} {} {}".format(character,constellation,skill_level,weapon,refine))
            
            c = Character(skill_level,constellation,logger)
            c.load_from_json("./data/character/"+character+".json")
            c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,refine)

            if self.rb_pop.isChecked():
                c.skill_round['a'] = 0
            else:
                pass
            rls = Articraft()
            rls.load_json("./data/sub.json")

            save = run_thru("./data/main_list.json",c,rls,logger)
                            
            test = OrderedDict(sorted(save.items(),reverse=True))
            N=0
            limit = 4
            for i in test:
                tmp = test[i]
                if self.rb_display.isChecked():
                    item =  QTableWidgetItem(str(i))
                else:
                    item =  QTableWidgetItem(str(round(i/10000,1))+'万')
                item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.tbl_2.setItem(0, N,item)
                item =  QTableWidgetItem(extract_name2(tmp['head']))
                item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.tbl_2.setItem(1, N,item)
                item =  QTableWidgetItem(extract_name2(tmp['glass']))
                item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.tbl_2.setItem(2, N,item)
                item =  QTableWidgetItem(extract_name2(tmp['cup']))
                item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                self.tbl_2.setItem(3, N,item)
                N+=1

                if N==limit:
                    break

            self.label.setText("计算成功")
            # self.btn_load_wp.show()
        except Exception as e:
            print("Error: ", e)
            self.label.setText("计算失败")
            traceback.print_exc()


    def read_sub(self):
        path = "./data/sub.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._sub_data = data["sub"]
            self.digit_cr.setValue(self._sub_data['cr']) 
            self.digit_cd.setValue(self._sub_data['cd']) 
            self.digit_dr.setValue(self._sub_data['dr']) 
            self.digit_ar.setValue(self._sub_data['ar']) 
            self.digit_ed.setValue(self._sub_data['ed']) 
            self.digit_fd.setValue(self._sub_data['fd']) 
            self.digit_sa.setValue(self._sub_data['sa']) 

    def save_sub(self):
        path = "./data/sub.json"

        # self._sub_data = data["sub"]
        data ={}
        data['cr'] = self.digit_cr.value() 
        data['cd'] = self.digit_cd.value()
        data['dr'] = self.digit_dr.value()
        data['ar'] = self.digit_ar.value()
        data['cd'] = self.digit_cd.value()
        data['ed'] = self.digit_ed.value()
        data['fd'] = self.digit_fd.value()
        data['sa'] = self.digit_sa.value()
        data['em'] = 0
        save = {}
        save['sub'] = data
        with open(path, 'w', encoding='UTF-8') as fp:
            json.dump(save, fp,indent = 4)


    def _set_cbox(self,pos,data):
        #setObjectName()/findChild()
        assert(pos in ['head','glass','cup'])
        # tmp = data[pos]
        ans = []
        for i in data:
            ans+=list(i.keys())        
        for i in set(ans):
            checkbox = self.findChild(QCheckBox, "cbox_"+pos[0]+"_"+i)
            if checkbox != None:
                checkbox.setChecked(True)

    def _read_cbox(self,pos):
        tmp = ['cr','cd','ar','dr','em','ed','fd']
        ans = []
      
        for i in tmp:
            checkbox = self.findChild(QCheckBox, "cbox_"+pos[0]+"_"+i)
            if checkbox != None:
                if checkbox.isChecked():
                    ans.append(i)
        return(ans)
                            
    def read_mainlist(self):
        with open('./data/main_list.json', 'r', encoding='UTF-8') as fp:
            data = json.load(fp)

        self._set_cbox('head',data['head'])
        self._set_cbox('glass',data['glass'])
        self._set_cbox('cup',data['cup'])          
            
            
            
    def save_mainlist(self):

        alist = ['head','glass','cup','flower','feather']
        blist=[[],[],[],['sh'],['sa']]
        blist[0]  = self._read_cbox('head')
        blist[1]  = self._read_cbox('glass')
        blist[2]  = self._read_cbox('cup')
                                               
        basic_main_rate = 31.1#满爆率

        prop_list = ['ar','ed','cr','cd','fd','sa','sh','dr','em']
        trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875,6.0128]
        ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

        ans = dict()
        for i in alist:
            ans[i] = []
            for j in blist[alist.index(i)]:
                tmp = dict()
                tmp[j] = round(basic_main_rate*ratio_main[j],2)
                ans[i].append(tmp.copy())

        with open('./data/main_list.json', 'w+') as fp:
            json.dump(ans, fp,indent = 4)
            




if __name__ == "__main__":
    

    
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()

    win.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
        logger = logging.getLogger()
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
    
