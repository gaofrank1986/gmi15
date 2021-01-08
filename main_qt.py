# import numpy as np
import json
from copy import deepcopy
import logging
import os
from collections import OrderedDict
from basic import Articraft
from character import Character
from utility import extract_name2,run_thru,MyDialog,parse_formula,extract_name3
import traceback
from PyQt5.QtWidgets import QApplication,QTableView,QMainWindow,QTableWidgetItem,QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox
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
        self.pb_buff.clicked.connect(self.new_win_buff) 
        self.pb_change.clicked.connect(self.change_action) 

        self.cb_name.currentIndexChanged.connect(self.reset)
        self.cb_wp.currentIndexChanged.connect(self.reset_table)
        self.cb_cnum.currentIndexChanged.connect(self.reset_table)
        self.cb_skill.currentIndexChanged.connect(self.reset_table)
        self.cb_refine.currentIndexChanged.connect(self.reset_table)


        self.b_read.hide()
        self.b_save.hide()
        self.b_read_main.hide()
        self.b_save_main.hide()
        
        self.pb_buff.hide()
        
        self.read_mainlist()
        self.read_sub()

        
        path = "./data/info.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._data = data      
        
        path = "./data/artifacts/artifact_effects.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._aeffect = data     
        
        
        
        self.cb_name.addItems(list(self._data.keys()))
        self.cb_aeffect1.addItems(list(self._aeffect.keys()))
        self.cb_aeffect2.addItems(list(self._aeffect.keys()))
        
        self.load_info()
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        fmt = logging.Formatter("%(asctime)s — %(message)s",datefmt='%m-%d,%H:%M')
        self.dlg = MyDialog(self,'Main',fmt)
        self.dlg.setFont(font)
        
        self.win_action = QDialog(self)
        loadUi("./data/win_action.ui",self.win_action)

        self.win_change = QDialog(self)
        loadUi("./data/change_action.ui",self.win_change)
        self.win_change.le_a.editingFinished.connect(lambda: self.checkline('a'))
        self.win_change.le_e.editingFinished.connect(lambda: self.checkline('e'))
        self.win_change.le_q.editingFinished.connect(lambda: self.checkline('q'))
        self.win_change.pb_save.clicked.connect(self.save_action)

        font.setFamily("汉仪文黑-85w")
        font.setPointSize(9)
        fmt = logging.Formatter("%(message)s")
        self.win_buff = MyDialog(self,'Buff',fmt)
        self.win_buff.setFont(font)
  

        
        
        
    #======================================
    def new_win(self):

        self.dlg.setWindowTitle("计算日志")
        self.dlg.exec_()

    def new_win_buff(self):
        self.win_buff.setWindowTitle("增益效果")
        self.win_buff.exec_()    

    
    def run(self):
        logger = logging.getLogger('Main')
        self.dlg.clear()
        self.win_buff.clear()
        self.reset_table()
        logger.info("=================日志开始================")
        logger.info("精确显示伤害后可复制到其他文本编辑器进行查询")
        logger.info("========================================")

        try:
            self.save_sub()
            self.save_mainlist()
            
            skill_level = int(self.cb_skill.currentText())
            constellation = int(self.cb_cnum.currentText())
            character = self._data[self.cb_name.currentText()]['name']
            weapon = self._wdata[self.cb_wp.currentText()]
            refine = int(self.cb_refine.currentText())

            self.label2.setText("")

            # self.label.setText("{} {} {} {} {}".format(character,constellation,skill_level,weapon,refine))
            
            c = Character(skill_level,constellation)
            c.load_from_json("./data/character/"+character+".json")
            c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,refine)

            if self.rb_pop.isChecked():
                c.skill_round['a'] = 0
            else:
                pass
            rls = Articraft()
            rls.load_json("./data/artifacts/sub.json")
            
            ae1 = self._aeffect[self.cb_aeffect1.currentText()]
            ae2 = self._aeffect[self.cb_aeffect2.currentText()]
            try:
                assert(int(ae1['n'])+int(ae2['n'])<=4)
                c._load_buff(ae1['buffs'],c._check1)
                c._load_buff(ae2['buffs'],c._check1)
            except:
                self.label2.setText("圣遗物套装信息错误，套装效果未加载")


            logging.getLogger('Buff').info("总效果: {}\n".format(c.skill_effect))
            logging.getLogger('Buff').info("特殊: {}\n".format(c.sp_buff))
            

            save = run_thru("./data/artifacts/main_list.json",c,rls,logger)

            if "rebase" in c._data.keys():
                for i in c._data['rebase']:
                    logging.getLogger('Buff').info("更换倍率基础 {}".format(i))
                    logging.getLogger('Buff').info(c._data['rebase'][i])
                    logging.getLogger('Buff').info("")


                 
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
            self.pb_buff.show()

        except Exception as e:
            print("Error: ", e)
            self.label.setText("计算失败")
            traceback.print_exc()


    def read_sub(self):
        path = "./data/artifacts/sub.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._sub_data = data["sub"]
            self.digit_cr.setValue(self._sub_data['cr']) 
            self.digit_cd.setValue(self._sub_data['cd']) 
            self.digit_dr.setValue(self._sub_data['dr']) 
            self.digit_ar.setValue(self._sub_data['ar']) 
            self.digit_ed.setValue(self._sub_data['ed']) 
            self.digit_fd.setValue(self._sub_data['dphys']) 
            self.digit_sa.setValue(self._sub_data['sa']) 
            self.digit_alld.setValue(self._sub_data['d']) 

    def save_sub(self):
        path = "./data/artifacts/sub.json"

        # self._sub_data = data["sub"]
        data ={}
        data['cr'] = self.digit_cr.value() 
        data['cd'] = self.digit_cd.value()
        data['dr'] = self.digit_dr.value()
        data['ar'] = self.digit_ar.value()
        data['cd'] = self.digit_cd.value()
        data['ed'] = self.digit_ed.value()
        data['dphys'] = self.digit_fd.value()
        data['sa'] = self.digit_sa.value()
        data['d'] = self.digit_alld.value()
        data['em'] = 0
        save = {}
        save['sub'] = data
        with open(path, 'w', encoding='UTF-8') as fp:
            json.dump(save, fp,indent = 4)


    def _set_cbox(self,pos,data):
        #setObjectName()/findChild()
        assert(pos in ['head','glass','cup'])
        ans = []
        for i in data:
            ans+=list(i.keys())        
        for i in set(ans):
            checkbox = self.findChild(QCheckBox, "cbox_"+pos[0]+"_"+i)
            if checkbox != None:
                checkbox.setChecked(True)

    def _read_cbox(self,pos):
        tmp = ['cr','cd','ar','dr','em','ed','dphys','hr','ef']
        ans = []
      
        for i in tmp:
            checkbox = self.findChild(QCheckBox, "cbox_"+pos[0]+"_"+i)
            if checkbox != None:
                if checkbox.isChecked():
                    ans.append(i)
        return(ans)
                            
    def read_mainlist(self):
        with open('./data/artifacts/main_list.json', 'r', encoding='UTF-8') as fp:
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

        prop_list = ['ar','ed','cr','cd','dphys','sa','sh','dr','em','hr','cure','ef']
        trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875,6.0128,1.5,1.1428,1,1]
        ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

        ans = dict()
        for i in alist:
            ans[i] = []
            for j in blist[alist.index(i)]:
                tmp = dict()
                tmp[j] = round(basic_main_rate*ratio_main[j],2)
                ans[i].append(tmp.copy())

        with open('./data/artifacts/main_list.json', 'w+') as fp:
            json.dump(ans, fp,indent = 4)
            
    def show_action(self):
        try:
            desc = ['普攻','元素战技','元素爆发']
            prop_name =['a','e','q']
            div1 = "==========\n"
            character = self._data[self.cb_name.currentText()]['name']
            cstl = 'c'+str(int(self.cb_cnum.currentText()))

            ans =''
            with open('./data/character/'+character+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            tmp = self.win_action.info_action
            for i in range(len(prop_name)):
                if data['action_def'][cstl][i]!='':
                    if i ==0 and self.rb_pop.isChecked():
                        ans+="{}(速切不计入伤害 {}轮)\n{}".format(desc[i],0,div1)                    
                    else:
                        rnd = data['round'][prop_name[i]]
                        ans+="{}({}轮)\n{}".format(desc[i],rnd,div1)
                    formula = data['action_def'][cstl][i]
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
            traceback.print_exc()

    def change_action(self):
        try:
            
            character = self._data[self.cb_name.currentText()]['name']
            cstl = 'c'+str(int(self.cb_cnum.currentText()))

            with open('./data/character/'+character+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            self._cdata = data
            self.win_change.lb_name.setText(data['name'])
            self.win_change.lb_c.setText(cstl)
            while (self.win_change.tb_skill.rowCount() > 0):
                self.win_change.tb_skill.removeRow(0)
            N = 0
            for i in data['ratios']:
                item =  QTableWidgetItem(i)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.win_change.tb_skill.insertRow(N)
                self.win_change.tb_skill.setItem(N,0,item)
                text = extract_name3(data['atk_type'][i])
                item = QTableWidgetItem(text)
                self.win_change.tb_skill.setItem(N,2,item)
                item = QTableWidgetItem(data['ratio_cmt'][i])
                self.win_change.tb_skill.setItem(N,1,item)

                N+=1
            header = self.win_change.tb_skill.horizontalHeader()       
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            
            self.win_change.le_a.setText(data['action_def'][cstl]['a'])
            self.win_change.le_e.setText(data['action_def'][cstl]['e'])
            self.win_change.le_q.setText(data['action_def'][cstl]['q'])
            
            self.win_change.sb_rnd_a.setValue(data['round']['a'])
            self.win_change.sb_rnd_e.setValue(data['round']['e'])
            self.win_change.sb_rnd_q.setValue(data['round']['q'])
            self.win_change.dsb_enchant.setValue(data['enchant_ratio'][cstl])

            self.win_change.exec_()
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def save_action(self):
        try:
            character = self._data[self.cb_name.currentText()]['name']
            cstl = 'c'+str(int(self.cb_cnum.currentText()))        
            rnd = dict()
            # fm = []
            for i in ['a','e','q']:
                rnd[i]= self.win_change.findChild(QSpinBox,"sb_rnd_"+i).value()
                assert self.win_change.findChild(QLabel,"lb_status_"+i).text() == '正确'
                # fm.append(self.win_change.findChild(QLineEdit,"le_"+i).text())
                self._cdata['action_def'][cstl][i] = self.win_change.findChild(QLineEdit,"le_"+i).text()

            self._cdata['enchant_ratio'][cstl] = self.win_change.dsb_enchant.value()
            self._cdata['round'] = rnd

            # self._cdata['action_def'][cstl]= dict()
            # self._cdata['action_def'][cstl]['a'] = fm[0]
            # self._cdata['action_def'][cstl]['e'] = fm[1]
            # self._cdata['action_def'][cstl]['q'] = fm[2]
            # self._cdata['action_def'][cstl]['shld'] = ''
            # self._cdata['action_def'][cstl]['heal'] = ''
            with open('./data/character/'+character+'.json', 'w', encoding='utf-8') as fp:
                json.dump(self._cdata, fp,indent = 4,ensure_ascii=False)

        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            
    def reset(self):
        self.cb_wp.clear()
        self.cb_cnum.clear()
        self.label.setText("")
        self.reset_table()
        self.load_info()

    def reset_table(self):
        self.pb_buff.hide()
        self.label2.setText("")
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

    def checkline(self,s):
        assert(s in['a','e','q'])
        fm = self.win_change.findChild(QLineEdit,"le_"+s).text()
        status = self.win_change.findChild(QLabel,"lb_status_"+s)
        if fm!='':
            try:
                tmp = fm.split('+')
                for i in tmp:
                    assert(i.count('*')<2)
                    tmp2 = i.split('*')
                    assert(tmp2[-1] in self._cdata['ratios'] or tmp2[-1] in ['ks'])
                status.setText('正确')
            except:
                status.setText('错误')
        else:
            status.setText('正确')

        
if __name__ == "__main__":
    

    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    win = MainWindow()

    win.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")

    
