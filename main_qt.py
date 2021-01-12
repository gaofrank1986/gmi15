# import numpy as np
import json
from copy import deepcopy
import logging
import os
from collections import OrderedDict
from basic import Articraft
from character import Character
from utility import run_thru,MyDialog,parse_formula,extract_name3,trans,run_thru_folders,extract_name4
import traceback
from PyQt5.QtWidgets import QApplication,QTableView,QMainWindow,QTableWidgetItem,QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from rec_art import Rec_Artifact
from chng_action import Change_Action
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        loadUi("./data/test.ui",self)

        self._data = {}
        self._wdata = {}
        self._aeffect = {}
        
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
            
        
        self.dlg = MyDialog(self,'Main',logging.Formatter("%(asctime)s — %(message)s",datefmt='%m-%d,%H:%M'))
        self.win_buff = MyDialog(self,'Buff',logging.Formatter("%(message)s"))
        self.win_save_act = Change_Action(self._data)
        self.win_rec_a = Rec_Artifact(self._aeffect,self._data[self.cb_name.currentText()]['name'])

        self.win_action = QDialog(self)
        loadUi("./data/win_action.ui",self.win_action)
        
        self.pb_change.clicked.connect(self.win_save_act.display) 
        self.pb_artifact.clicked.connect(self.win_rec_a.display)         
        self.btn_load_wp.clicked.connect(self.dlg.exec_) 
        self.pb_buff.clicked.connect(self.win_buff.exec_) 

       
        self.btn_run.clicked.connect(self.run) 
        self.pb_action.clicked.connect(self.list_action) 

        self.cb_name.currentIndexChanged.connect(self.reset)
        self.cb_wp.currentIndexChanged.connect(self.reset_table)
        self.cb_cnum.currentIndexChanged.connect(self.reset_table)
        self.cb_skill.currentIndexChanged.connect(self.reset_table)
        self.cb_refine.currentIndexChanged.connect(self.reset_table)
        self.cb_sort.currentIndexChanged.connect(self.change_ksort)
        self.cb_mode2.stateChanged.connect(self.show_rec)
        

        self.pb_artifact.hide()
        self.pb_buff.hide()
        self.rb_pop.hide()
        
        self.read_mainlist()
        self.read_sub()

        
        

        
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.dlg.setFont(font)
        



        font.setFamily("汉仪文黑-85w")
        font.setPointSize(9)
        self.win_buff.setFont(font)
  
        header = self.tbl_2.horizontalHeader()       
        # header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        self._ksort = 1
        self.reset()




        
    # #======================================

    
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

            env = {'spec':True,'fire':self.cb_cond_fire.isChecked(),'watr':self.cb_cond_watr.isChecked(),'elec':self.cb_cond_elec.isChecked(),'ice':self.cb_cond_ice.isChecked(),'frozen':self.cb_cond_frozen.isChecked(),'lowhp':self.cb_cond_lowhp.isChecked()}
            # print(env)
            
            c = Character(skill_level,constellation)
            c.load_from_json("./data/character/"+character+".json",env)
            c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,env,refine)

            if self.rb_pop.isChecked():
                c.skill_round['a'] = 0
            else:
                pass

            
            ae1 = self._aeffect[self.cb_aeffect1.currentText()]
            ae2 = self._aeffect[self.cb_aeffect2.currentText()]
            try:
                assert(int(ae1['n'])+int(ae2['n'])<=4)
                c._load_buff(ae1['buffs'],c._check1,env)
                c._load_buff(ae2['buffs'],c._check1,env)
            except:
                self.label2.setText("圣遗物套装信息错误，套装效果未加载")
                traceback.print_exc()

            logging.getLogger('Buff').info("总效果: {}\n".format(c.skill_effect))
            logging.getLogger('Buff').info("特殊攻击加成: {}\n".format(c.sp_buff))
            
            
            rls = Articraft()
            if self.cb_mode2.isChecked():
                rm_sub={'ed':self.digit_ed.value(),'dphys':self.digit_fd.value(),'d':self.digit_alld.value()}
                c.load_att(rm_sub)
                save = run_thru_folders(self.win_rec_a.path,self._aeffect,c,rls,self.pbar,self._ksort)
            else:
                rls.load_json("./data/artifacts/sub.json")
                save = run_thru("./data/artifacts/main_list.json",c,rls,self.pbar,self._ksort)
                
            if "rebase" in c._data.keys():
                for i in c._data['rebase']:
                    logging.getLogger('Buff').info("更换倍率基础 {}".format(i))
                    logging.getLogger('Buff').info(c._data['rebase'][i])
                    logging.getLogger('Buff').info("")


            test = OrderedDict(sorted(save.items(),reverse=True))
            N=0
            limit = 4
            for i in test:
                if 'sub' in test[i][1]:
                    test[i][1].pop('sub')
                tmp = list(test[i][1].keys())
                tmp2 = [list(test[i][1][_].keys())[0] for _ in tmp]
                if self.cb_mode2.isChecked():
                    tmp2 = tmp
                tmp2 = [extract_name4(_) for _ in tmp2]
                tmp0 = test[i][0]

                if self.rb_display.isChecked():
                    content = [i]+tmp2+[tmp0['shld'],tmp0['heal'],tmp0['maxhp'],tmp0['sum']]                
                else:
                    content = [trans(i)]+tmp2+[trans(tmp0['shld']),trans(tmp0['heal']),trans(tmp0['maxhp']),trans(tmp0['sum'])]                
                for i in range(len(content)):
                    item =  QTableWidgetItem(str(content[i]))
                    item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    self.tbl_2.setItem(i, N,item)

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
            self.digit_sd.setValue(self._sub_data['sd']) 
            self.digit_hr.setValue(self._sub_data['hr']) 
            self.digit_em.setValue(self._sub_data['em']) 
            self.digit_sh.setValue(self._sub_data['sh']) 

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
        data['sd'] = self.digit_sd.value()
        data['sh'] = self.digit_sh.value()
        data['hr'] = self.digit_hr.value()
        data['em'] = self.digit_em.value()
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
        tmp = ['cr','cd','ar','dr','em','ed','dphys','hr','ef','dheal']
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

        prop_list = ['ar','ed','cr','cd','dphys','sa','sh','dr','em','hr','dheal','ef']
        trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875,6.0128,1.5,1.1428,1.1543,1.6656]
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
            
    def list_action(self):
        try:
            desc = ['普攻','元素战技','元素爆发','护盾技能','治疗技能']
            prop_name =['a','e','q','shld','heal']
            div1 = "==========\n"
            character = self._data[self.cb_name.currentText()]['name']
            cstl = 'c'+str(int(self.cb_cnum.currentText()))

            ans =''
            with open('./data/character/'+character+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            tmp = self.win_action.info_action
            for i in range(len(prop_name)):
                if data[cstl]['action_def'][prop_name[i]]!='':
                    if i ==0 and self.rb_pop.isChecked():
                        ans+="{}(速切不计入伤害 {}轮)\n{}".format(desc[i],0,div1)                    
                    else:
                        if i <3:
                            rnd = data[cstl]['round'][prop_name[i]]
                        else:
                            rnd = 1
                        ans+="{}({}轮)\n{}".format(desc[i],rnd,div1)
                    formula = data[cstl]['action_def'][prop_name[i]]
                    for entry in parse_formula(formula):
                        if entry[0] == 'ks':
                            ans += '扩散伤害'
                            ans += '  x {}'.format(entry[1])
                        else:
                            ans += data['ratio_cmt'][entry[0]]
                            ans += '  x {}'.format(entry[1])
                        ans+='\n'
                else:
                    ans+="{}\n{}".format(desc[i],div1)
                    ans+='无定义\n'
                ans+='\n'
            tmp.setPlainText(ans)
            self.win_action.exec_()
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()



    def show_rec(self):
        if self.cb_mode2.isChecked():
            self.pb_artifact.show()
        else:
            self.pb_artifact.hide()


            
    def reset(self):
        self.cb_wp.clear()
        self.cb_cnum.clear()
        self.label.setText("")
        self.reset_table()
        self.load_info()
        self.win_rec_a.update(self._data[self.cb_name.currentText()]['name'])


    def reset_table(self):
        bbb ={'伤害':9,'护盾':6,'生命':8,'治疗':7}
        self.pb_buff.hide()
        self.label2.setText("")
        self.label.setText("")
        for i in range(self.tbl_2.rowCount()):
            for j in range(4):
                self.tbl_2.setItem(i, j,QTableWidgetItem(""))
            self.tbl_2.setRowHidden(i,False)
        text = self.cb_sort.currentText()
        self.tbl_2.setRowHidden(bbb[text],True)
        self.pbar.setValue(0)
        self.win_save_act.update(self.cb_name.currentText(),self.cb_cnum.currentText())   
        if not self.cb_mode2.isChecked():
            self.tbl_2.setRowHidden(4,True)
            self.tbl_2.setRowHidden(5,True)
                 
        
        
         
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


    
    def change_ksort(self):
        aaa ={'伤害':1,'护盾':2,'生命':3,'治疗':4}
        text = self.cb_sort.currentText()
        assert(text in aaa)
        self.tbl_2.setVerticalHeaderItem(0,QTableWidgetItem(text))
        self._ksort = aaa[text]
        self.reset_table()
        

if __name__ == "__main__":
    

    
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    win = MainWindow()

    win.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")

    
