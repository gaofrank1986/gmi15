# import numpy as np
import json
from copy import deepcopy
import logging
import os
from collections import OrderedDict
from basic import Articraft
from character import Character
from utility import MyDialog,parse_formula,trans,run_thru_data
import traceback
from PyQt5.QtWidgets import QApplication,QTableView,QMainWindow,QTableWidgetItem,QCheckBox,QDialog,QLineEdit,QLabel,QSpinBox,QFrame,QPushButton,QMenu,QMenuBar,QTableWidget,QToolButton 
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt
from rec_art import Rec_Artifact, DB_Filter
from chng_action import Change_Action
from ocr import cn
from db_setup import Entry,db_session,init_db,get_info_by_id
from check_list import AppRemovalPage
from sqlalchemy import and_,or_
from wincara import caraWindow
class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        QtGui.QFontDatabase.addApplicationFont("./data/ui/zh-cn.ttf")
        loadUi("./data/ui/test.ui",self)
        font = QtGui.QFont()


        self._data = {}
        self._wlookup= {}
        self._aeffect = {}
        
        path = "./data/info.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            # self._data = data      
        namelist=[]
        # namelookup={}
        for i in data:
            if "=" not in i:
                key = data[i]['name']
                namelist.append(key)
                self._data[key]={}
                self._data[key]['w']=data[i]['w']
                self._data[key]['c']=data[i]['c']
                self._data[key]['cn']=i
                # namelookup[key] = i
                

        self.current_role='diluc'
        self.win_cara = caraWindow(namelist,path="./data/character/icon/")
        
        self.pb_wpn = QToolButton(self.tab)
        self.pb_wpn.setGeometry(50,240,90,100)
        self.pb_wpn.setText("武器")
        font.setPointSize(9)
        self.pb_wpn.setFont(font)

        
        path = "./data/artifacts/artifact_effects.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._aeffect = data     
        
        self.cb_aeffect1.addItems(list(self._aeffect.keys()))
        self.cb_aeffect2.addItems(list(self._aeffect.keys()))
            
        
        self.dlg = MyDialog(self,'Main',logging.Formatter("%(asctime)s — %(message)s",datefmt='%m-%d,%H:%M'))
        self.win_buff = MyDialog(self,'Buff',logging.Formatter("%(message)s"))
        self.win_log = MyDialog(self,'1',logging.Formatter("%(message)s"))
        self.win_save_act = Change_Action(self._data,self.statusBar())
        self.win_rec_a = Rec_Artifact(self._aeffect,self.current_role,self.statusBar())


        
        self.pb_change.clicked.connect(self.win_save_act.display) 
        self.pb_artifact.clicked.connect(self.win_rec_a.display)         
        self.btn_load_wp.clicked.connect(self.dlg.exec_) 
        self.pb_buff.clicked.connect(self.win_buff.exec_) 
        self.pb_cara.clicked.connect(self.select_cara)
        self.pb_wpn.clicked.connect(self.select_wpn)

       
        self.btn_run.clicked.connect(self.run) 


        self.cb_cnum.currentIndexChanged.connect(self.reset_table)
        self.cb_skill.currentIndexChanged.connect(self.reset_table)
        self.cb_refine.currentIndexChanged.connect(self.reset_table)
        self.cb_sort.currentIndexChanged.connect(self.change_ksort)
        # self.rb_mode2.toggled.connect(self.show_rec)
        # self.rb_mode1.toggled.connect(self.show_rec)
        self.cb_mode2.stateChanged.connect(self.show_rec)
        self.cb_mode2.setToolTip("<b>模式1:</b> 选择圣遗物主词条穷举<br><b>模式2:</b> 圣遗物录入穷举")
        self.cb_switch_def.setToolTip("防御及抗性效果纳入计算，防御及抗性数值在<b>环境设置</b>中修改")
        self.rb_pop.setToolTip("元素反应纳入计算,增幅反应取最大系数,剧变反应需在<b>技能定义</b>中定义")


        self.read_mainlist()


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
        self.select_cara(noshow=True)


        self.statusBar().showMessage("bla-bla bla")
        # self.lbl1 = QLabel("Label: ")
        # self.lbl1.setStyleSheet('border: 0; color:  blue;')
        # self.lbl2 = QLabel("Data : ")
        # self.lbl2.setStyleSheet('border: 0; color:  red;')
        ed = QPushButton('Log')

        self.statusBar().reformat()
        self.statusBar().setStyleSheet('border: 0; background-color: #FFF8DC;')
        self.statusBar().setStyleSheet("QStatusBar::item {border: none;}") 
        self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(self.rb_pop)
        self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(self.cb_switch_def)
        self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(self.btn_run)       
        self.statusBar().addPermanentWidget(VLine())    # <---
  # <---
        self.statusBar().addPermanentWidget(self.pbar)
        self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(self.cb_mode2)       
        self.statusBar().addPermanentWidget(VLine())  
        self.statusBar().addPermanentWidget(self.pb_buff)
        self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(ed)
        self.statusBar().addPermanentWidget(VLine())    # <---
        
        # self.lbl1.setText("Label: Hello")
        # self.lbl2.setText("Data : 15-09-2019")

        # ed.clicked.connect(lambda: self.statusBar().showMessage("Hello "))
        ed.clicked.connect(self.win_log.exec_)

        # menuBar = QMenuBar(self)
        # fileMenu = QMenu("&File", self)
        # menuBar.addMenu(fileMenu)
        
        self.trans2 = cn().trans2
        
        init_db()
        
        self.tabs.setTabEnabled(3,False)

        # ===============================
        hlay = self.verticalLayout
        lay = QtWidgets.QHBoxLayout()
        lay2 = QtWidgets.QHBoxLayout()
        hlay.addLayout(lay2)
        hlay.addLayout(lay)
        self.head = AppRemovalPage()
        self.glass = AppRemovalPage()
        self.cup = AppRemovalPage()
        self.feather = AppRemovalPage()
        self.flower = AppRemovalPage()
        for i in ["理之冠","时之沙","空之杯","生之花","死之羽"]:
            tmp = QLabel(i, alignment=QtCore.Qt.AlignCenter)
            tmp.setFixedHeight(30)
            lay2.addWidget(tmp)
            
        lay.addWidget(self.head)
        lay.addWidget(self.glass)
        lay.addWidget(self.cup)
        lay.addWidget(self.flower)
        lay.addWidget(self.feather)
        self.pb_load_db.clicked.connect(self.load_db_info)

        
    # #======================================
    def select_cara(self,noshow=False):
        if not noshow:
            self.win_cara.clicked =False
            self.win_cara.exec_()
            self.current_role = self.win_cara.cara
        
        if noshow or self.win_cara.clicked:
            self.pb_cara.setIcon(QtGui.QIcon("./data/character/icon/"+self.current_role+".png"))
            self.pb_cara.setIconSize(QtCore.QSize(80, 80))
            self.pb_cara.setText("")
            self.reset()            
 
    def select_wpn(self,noshow=False):
        if not noshow:
            self.win_wpn.clicked=False
            self.win_wpn.exec_()
            self.current_wpn = self.win_wpn.cara
                
        if noshow or self.win_wpn.clicked:
            self.pb_wpn.setIcon(QtGui.QIcon(self.win_wpn.path+self.current_wpn+".png"))
            self.pb_wpn.setIconSize(QtCore.QSize(80, 80))
            self.pb_wpn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            if not self.win_wpn.cara =='':
                self.pb_wpn.setText(self._wlookup[self.win_wpn.cara])
            self.reset_table()


    def load_db_info(self):
        pos = ["理之冠","时之沙","空之杯","生之花","死之羽"]
        trans = ['head','glass','cup','flower','feather']
        self.aaa = DB_Filter(self.win_rec_a.owners)
        self.aaa.exec_()
        if self.aaa.if_OK:
            if self.aaa.filter == '全部':
                check = True
            else:
                check = False
            for apos in pos:
                ans = []
                for i in db_session.query(Entry).filter(and_(Entry.pos==apos,or_(check,Entry.owner==self.aaa.filter))).all():
                    ans.append(str(i.id)+'_'+i.name)
                tmp = getattr(self,trans[pos.index(apos)])
                tmp.add(ans)
   
    
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
            character = self.current_role
            weapon = self.current_wpn
            assert weapon!=''
            
            refine = int(self.cb_refine.currentText())

            

            env = {'spec':True,'fire':self.rb_cond_fire.isChecked(),'watr':self.rb_cond_watr.isChecked(),'elec':self.rb_cond_elec.isChecked(),'ice':self.rb_cond_ice.isChecked(),'frozen':self.cb_cond_frozen.isChecked(),'lowhp':self.cb_cond_lowhp.isChecked()}
            logger.info(env)
            
            c = Character(skill_level,constellation)
            c.load_from_json("./data/character/"+character+".json",env)
            c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,refine)

            if self.rb_pop.isChecked():
                c.ifer = True
            if self.cb_switch_def.isChecked():
                c.if_def_r = True            # else:

            c._load_buff(c.buffs,c._check1,env)
            
            ae1 = self._aeffect[self.cb_aeffect1.currentText()]
            ae2 = self._aeffect[self.cb_aeffect2.currentText()]
            try:
                assert(int(ae1['n'])+int(ae2['n'])<=4)
                c._load_buff(ae1['buffs'],c._check1,env)
                c._load_buff(ae2['buffs'],c._check1,env)
            except:

                self.statusBar().showMessage("圣遗物套装信息错误，套装效果未加载")
                logging.getLogger('1').error(traceback.format_exc())

            logging.getLogger('Buff').info("总效果: {}\n".format(c.skill_effect))
            logging.getLogger('Buff').info("特殊攻击加成: {}\n".format(c.sp_buff))

            enemy = {"lvl":self.sb_enemy_lvl.value(),"erss":self.sb_enemy_erss.value(),"frss":self.sb_enemy_frss.value()}
            logging.getLogger('1').info(enemy)
            c.enemy = enemy         
            
            rls = Articraft()
            rm_sub={'ed':self.digit_ed.value(),'dphys':self.digit_fd.value(),'d':self.digit_alld.value(),'sa':self.digit_benett.value()}
            c.load_att(rm_sub)            
            if self.cb_mode2.isChecked():

                cal_data={}
                trans_pos = ['head','glass','cup','flower','feather']
 
                for apos in trans_pos:
                    cal_data[apos]=[]
                    tmp = getattr(self,apos)
                    assert len(tmp.record)>=1
                    for jjj in tmp.record:
                        cal_data[apos].append(get_info_by_id(int(jjj.split('_')[0])))
                
                save = run_thru_data(cal_data,self._aeffect,c,rls,self.pbar,self._ksort)
                # save = run_thru_folders(self.win_rec_a.path,self._aeffect,c,rls,self.pbar,self._ksort)
            else:
                rls.load_json("./data/artifacts/sub.json")
                with open('./data/artifacts/main_list.json', 'r', encoding='UTF-8') as fp:
                    cal_data = json.load(fp)
                # save = run_thru("./data/artifacts/main_list.json",c,rls,self.pbar,self._ksort)
                save = run_thru_data(cal_data,self._aeffect,c,rls,self.pbar,self._ksort)
                
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
                tmp2 = list(test[i][1].keys())

                # tmp2 = [list(test[i][1][_].keys())[0] for _ in tmp]
                # if self.rb_mode2.isChecked():
                # tmp2 = tmp
                tmp2 = [_.split('_')[1] for _ in tmp2]
                tmp0 = test[i][0]
                logging.getLogger('1').info("{}{}{}{}".format(character,constellation,c.equipment[0],tmp0))

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

            self.statusBar().showMessage("计算成功")
            self.tabs.setCurrentIndex(0)
            # self.pb_buff.show()

        except Exception as e:
            self.statusBar().showMessage("计算失败")
            logging.getLogger('1').error("Error:{} ".format(e))
            logging.getLogger('1').error(traceback.format_exc())



    def read_sub(self):
        path = "./data/artifacts/sub.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._sub_data = data["sub"]
            self.digit_cr.setValue(self._sub_data['cr']) 
            self.digit_cd.setValue(self._sub_data['cd']) 
            self.digit_dr.setValue(self._sub_data['dr']) 
            self.digit_ar.setValue(self._sub_data['ar']) 
            # self.digit_ed.setValue(self._sub_data['ed']) 
            # self.digit_fd.setValue(self._sub_data['dphys']) 
            self.digit_sa.setValue(self._sub_data['sa']) 
            # self.digit_alld.setValue(self._sub_data['d']) 
            self.digit_sd.setValue(self._sub_data['sd']) 
            self.digit_hr.setValue(self._sub_data['hr']) 
            self.digit_em.setValue(self._sub_data['em']) 
            self.digit_sh.setValue(self._sub_data['sh']) 

    def save_sub(self):
        path = "./data/artifacts/sub.json"

        data ={}
        data['cr'] = self.digit_cr.value() 
        data['cd'] = self.digit_cd.value()
        data['dr'] = self.digit_dr.value()
        data['ar'] = self.digit_ar.value()
        data['cd'] = self.digit_cd.value()
        # data['ed'] = self.digit_ed.value()
        # data['dphys'] = self.digit_fd.value()
        data['sa'] = self.digit_sa.value()
        # data['d'] = self.digit_alld.value()
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
                tmp['set'] = '无'
                tmp['name'] = self.trans2[j]
                tmp[j] = round(basic_main_rate*ratio_main[j],2)
                ans[i].append(tmp.copy())

        # with open('./data/artifacts/main_list.json', 'w+') as fp:
        #     json.dump(ans, fp,indent = 4)
        with open('./data/artifacts/main_list.json', 'w+', encoding='utf-8') as fp:
                json.dump(ans, fp,indent = 4,ensure_ascii=False)
            




    def show_rec(self):
        if self.cb_mode2.isChecked():
            self.tabs.setTabEnabled(2,False)
            self.tabs.setTabEnabled(3,True)
        else:
            self.tabs.setTabEnabled(2,True)
            self.tabs.setTabEnabled(3,False)

            
    def reset(self):
        self.cb_cnum.clear()
        self.reset_table()
        self.load_info()
        self.win_rec_a.update(self.current_role)


    def reset_table(self):
        bbb ={'伤害':9,'护盾':6,'生命':8,'治疗':7}

        for i in range(self.tbl_2.rowCount()):
            for j in range(4):
                self.tbl_2.setItem(i, j,QTableWidgetItem(""))
            self.tbl_2.setRowHidden(i,False)
        text = self.cb_sort.currentText()
        self.tbl_2.setRowHidden(bbb[text],True)
        self.pbar.setValue(0)
        # self.win_save_act.update(self.cb_name.currentText(),self.cb_cnum.currentText())   
        self.win_save_act.update(self.current_role,self.cb_cnum.currentText())   
        if not self.cb_mode2.isChecked():
            self.tbl_2.setRowHidden(4,True)
            self.tbl_2.setRowHidden(5,True)
                 
        
        
         
    def load_info(self):
        wkind = self._data[self.current_role]['w']
        path = "./data/weapon/"+wkind+".json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        wpnlist=[]
        self._wlookup={}
        for wp in data: 
            wpnlist.append(wp)
            self._wlookup[wp] = data[wp]['name']
            
        self.win_wpn = caraWindow(wpnlist,"./data/weapon/icon/"+self._data[self.current_role]['w']+'/',lookup = self._wlookup)
        self.pb_wpn.setText("武器")
        self.current_wpn=""
        self.pb_wpn.setIconSize(QtCore.QSize(0, 0))
        
        self.cb_cnum.addItems(self._data[self.current_role]['c'])
        self.statusBar().showMessage("信息重新加载")


    
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

    
