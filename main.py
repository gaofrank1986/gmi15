import os,sys,traceback,pprint,json,logging
from collections import OrderedDict
from copy import deepcopy
from sqlalchemy import and_,or_

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt,QItemSelectionModel
from PyQt5.QtWidgets import QApplication,QMainWindow,QTableWidgetItem,QCheckBox,QLabel,QFrame,QTableWidget,QToolButton,QListWidget

from src.mods.ocr import cn
from src.mods.db_setup import Entry,db_session,init_db,get_info_by_id,CRatio,RWData
from src.mods.basic import Articraft
from src.mods.character import Character
from src.mods.utility import MyDialog,parse_formula,ps2,run_thru_data,ps1,gen_sublist,rename,gen_mainlist

from src.dialog.win_ratio import Win_Ratio
from src.dialog.win_select import caraWindow
from src.dialog.win_skill import Win_Skill
from src.dialog.win_rec_art import Rec_Artifact, DB_Filter
from src.widget.check_list import AppRemovalPage

class MyListWidget(QListWidget):
    def __init__(self, parent=None, max_selected = 3):
        super().__init__(parent)
        self.max_selected = max_selected

    def selectionCommand(self, index, event):
        if len(self.selectedItems()) >= self.max_selected:
            return QItemSelectionModel.Deselect
        else:
            return super().selectionCommand(index, event)


class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        QtGui.QFontDatabase.addApplicationFont("./data/ui/zh-cn.ttf")
        loadUi("./data/ui/main.ui",self)
        font = QtGui.QFont()

        self.setFixedWidth(1070)
        
        self._data = {}
        self._wlookup= {}
        self._aeffect = {}
        
        path = "./data/info.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        namelist=[]
        for i in data:
            if "=" not in i:
                key = data[i]['name']
                namelist.append(key)
                self._data[key]={}
                self._data[key]['w']=data[i]['w']
                self._data[key]['c']=data[i]['c']
                self._data[key]['cn']=i
                

        self.current_role='diluc'
        self.win_cara = caraWindow(namelist,path="./data/character/icon/")
        
        self.pb_wpn = QToolButton(self.tab)
        self.pb_wpn.setGeometry(65,280,90,100)
        self.pb_wpn.setText("武器")
        font.setPointSize(9)
        self.pb_wpn.setFont(font)

        
        path = "./data/artifacts/artifact_effects.json"
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self._aeffect = data     
        
        self.cb_aeffect1.addItems(list(self._aeffect.keys()))
        self.cb_aeffect2.addItems(list(self._aeffect.keys()))
            
        
        self.dlg = MyDialog(self,'Main',logging.Formatter("%(asctime)s — %(message)s",datefmt='%H:%M'))
        self.win_buff = MyDialog(self,'Buff',logging.Formatter("%(message)s"))
        self.win_log = MyDialog(self,'1',logging.Formatter("%(message)s"))
        self.win_save_act = Win_Skill(self._data,self.statusBar())
        self.win_rec_a = Rec_Artifact(self._aeffect,self.statusBar())
        
        self.win_ratio = Win_Ratio(self.current_role,self.statusBar())

        
        self.pb_change.clicked.connect(self.win_save_act.display) 
        self.pb_artifact.clicked.connect(self.win_rec_a.display)         
        self.btn_load_wp.clicked.connect(self.dlg.exec_) 
        self.pb_buff.clicked.connect(self.win_buff.exec_) 
        self.pb_cara.clicked.connect(self.select_cara)
        self.pb_wpn.clicked.connect(self.select_wpn)
        self.pb_ratio.clicked.connect(self.win_ratio.display)

       
        self.btn_run.clicked.connect(self.run) 


        self.cb_cnum.currentIndexChanged.connect(self.reset_table)
        self.cb_skill.currentIndexChanged.connect(self.reset_table)
        self.cb_refine.currentIndexChanged.connect(self.reset_table)
        self.cb_sort.currentIndexChanged.connect(self.change_ksort)
        # self.rb_mode2.toggled.connect(self.show_rec)
        # self.rb_mode1.toggled.connect(self.show_rec)
        self.cb_mode2.currentIndexChanged.connect(self.show_rec)
        self.cb_mode2.setToolTip("<b>模式1:</b> 主词条穷举<br><b>模式2:</b> 副词条穷举<b>模式3:</b> 录入穷举")
        self.cb_switch_def.setToolTip("防御及抗性效果纳入计算，防御及抗性数值在<b>环境设置</b>中修改")
        self.rb_pop.setToolTip("元素反应纳入计算,增幅反应取最大系数,剧变反应需在<b>技能定义</b>中定义")
        self.rb_cond_fire.setToolTip("渡火4等")
        self.rb_cond_elec.setToolTip("平雷4,匣里龙吟等")
        self.rb_cond_ice.setToolTip("冰风4等")
        self.cb_cond_frozen.setToolTip("冰风4等")

        self.read_mainlist()
        self.read_sub()

        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.dlg.setFont(font)
        

        font.setFamily("汉仪文黑-85w")
        font.setPointSize(9)
        self.win_buff.save.setFont(font)
  
        header = self.tbl_2.horizontalHeader()       
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        # self.tbl_2.setRowHeight(6,100)
        header = self.tbl_2.verticalHeader()       
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        
        self._ksort = 1
        self.select_cara(noshow=True)


        self.statusBar().showMessage("bla-bla bla")
        # self.lbl1 = QLabel("Label: ")
        # self.lbl1.setStyleSheet('border: 0; color:  blue;')
        # self.lbl2 = QLabel("Data : ")
        # self.lbl2.setStyleSheet('border: 0; color:  red;')
        # ed = QPushButton('Log')

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
        self.statusBar().addPermanentWidget(self.pbar)
        self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(self.cb_mode2)       
        self.statusBar().addPermanentWidget(VLine())  
        # self.statusBar().addPermanentWidget(self.pb_buff)
        # self.statusBar().addPermanentWidget(VLine())    # <---
        self.statusBar().addPermanentWidget(self.cb_check)
        self.statusBar().addPermanentWidget(VLine())    # <---
        
        # ed.clicked.connect(self.win_log.exec_)
        self.pb_log.clicked.connect(self.win_log.exec_)
        self.cb_check.stateChanged.connect(self.resize_main)


        
        self.trans2 = cn().trans2
        self.trans1 = cn().trans1
        
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
    
        
        self.select_subs = MyListWidget(self.groupBox_11,3)
        self.select_subs.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.select_subs.setGeometry(30,70,220,150)
        font.setPointSize(10)
        self.select_subs.setFont(font)
        self.select_subs.addItems(['攻击','暴击','暴伤','防御','生命'])
        self.select_subs.itemClicked.connect(self.printItemText)
        self.cb_main_head.addItems(['暴击','暴伤','攻击','防御'])
        self.cb_main_glass.addItems(['攻击','防御','生命'])
        self.cb_main_cup.addItems(['属伤','物伤','攻击','生命'])
        self.show_rec()
        self.save_sub_list=[]
        
        self.tabs.setCurrentIndex(0)

    def resize_main(self):
        if self.cb_check.isChecked():
            self.setFixedWidth(1200)
        else:
            self.setFixedWidth(1070)

    def printItemText(self):
        items = self.select_subs.selectedItems()
        lang = cn()
        x = []
        y = []
        for i in range(len(items)):
            x.append(str(self.select_subs.selectedItems()[i].text()))
            y.append(lang.trans1[x[-1]])

        self.label_subs.setText('已选: {}'.format(','.join(x)))
        self.save_sub_list = y
        
    # #======================================
    def select_cara(self,noshow=False):
        if not noshow:
            self.win_cara.clicked =False
            self.win_cara.exec_()
            if self.win_cara.clicked:
                self.current_role = self.win_cara.cara
                self.win_ratio.role = self.current_role
        
        if noshow or self.win_cara.clicked:
            self.pb_cara.setIcon(QtGui.QIcon("./data/character/icon/"+self.current_role+".png"))
            self.pb_cara.setIconSize(QtCore.QSize(110, 110))
            self.pb_cara.setText("")
            self.reset()            
 
    def select_wpn(self,noshow=False):
        if not noshow:
            self.win_wpn.clicked=False
            self.win_wpn.exec_()
            if self.win_wpn.clicked:
                self.current_wpn = self.win_wpn.cara
                wkind = self._data[self.current_role]['w']
                assert self.current_wpn!=''
                self.win_ratio.wpn = wkind+'_'+self.current_wpn
                
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
                for i in db_session.query(Entry).filter(and_(Entry.pos==apos,or_(Entry.owner0==self.aaa.filter,Entry.owner1==self.aaa.filter,Entry.owner2==self.aaa.filter,Entry.owner3==self.aaa.filter,Entry.owner4==self.aaa.filter,check))).all():
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
        logging.getLogger('1').info("=================log开始================")

        fail_info=[]
        try:
            self.save_sub()
            # self.save_mainlist()
            blist=[self._read_cbox('head'),self._read_cbox('glass'),self._read_cbox('cup'),['sh'],['sa']]
            mainlist = gen_mainlist(blist)
            with open('./data/artifacts/main_list.json', 'w+', encoding='utf-8') as fp:
                    json.dump(mainlist, fp,indent = 4,ensure_ascii=False)


            env = {'spec':True,'fire':self.rb_cond_fire.isChecked(),'watr':self.rb_cond_watr.isChecked(),'elec':self.rb_cond_elec.isChecked(),'ice':self.rb_cond_ice.isChecked(),'frozen':self.cb_cond_frozen.isChecked(),'lowhp':self.cb_cond_lowhp.isChecked()}
            logger.info(env)
            
            team_cond = {"rock":self.cb_tm_rock.isChecked(),"fire":self.cb_tm_fire.isChecked(),"watr":self.cb_tm_watr.isChecked(),"ice":self.cb_tm_ice.isChecked()}
            team_buff ={"rock":[["all"],{"dshld":15,"d":15,"derss":20},1,"岩队加成"],"fire":[["all"],{"ar":25},1,"火队加成"],"watr":[["all"],{"dheal":30},1,"水队加成"],"ice":[["all"],{"cr":15},1,"冰队加成"]}
            print(team_cond)
            
            enemy = {"lvl":self.sb_enemy_lvl.value(),"erss":self.sb_enemy_erss.value(),"frss":self.sb_enemy_frss.value()}
     
            
            try:
                skill_level = int(self.cb_skill.currentText())
                constellation = int(self.cb_cnum.currentText())
                cnum ='c'+str(constellation)
                character = self.current_role
                c = Character(skill_level,constellation)
                ratio ={}
                cro = db_session.query(CRatio).filter(CRatio.name == character+'_'+cnum).first()
                if cro is not None:
                    tmp1 = cro.keys.split("/")                   
                    tmp2 = [float(_) for _ in cro.values.split("||")]
                    for i in tmp1:
                        ratio[i] = tmp2[tmp1.index(i)]
                cdata = db_session.query(RWData).filter(RWData.name == character).first()
                c.load_from_json("./data/character/"+character+".json",env,ratio,cdata = cdata )

            except:
                fail_info.append("人物信息错误")
                raise ValueError
                
            try:
                weapon = self.current_wpn
                assert weapon!=''
                ratio ={}
                refine = int(self.cb_refine.currentText())
                wro = db_session.query(CRatio).filter(CRatio.name == c.weapon_class+'_'+weapon).first()
                if wro is not None:
                    tmp1 = wro.keys.split("/")                   
                    tmp2 = [float(_) for _ in wro.values.split("||")]
                    for i in tmp1:
                        ratio[i] = tmp2[tmp1.index(i)]
                print(ratio)
                wdata = db_session.query(RWData).filter(RWData.name == c.weapon_class+'_'+weapon).first()
                c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,ratio,refine,wdata)

            except:
                fail_info.append("武器信息错误")
                raise ValueError


            if self.rb_pop.isChecked():
                c.ifer = True
            if self.cb_switch_def.isChecked():
                c.if_def_r = True       
            
            for i in team_cond:
                if team_cond[i]:
                    c.buffs['tm_'+i] = team_buff[i]

            '''人物/武器/圣遗物套装(非录入穷举) buff 加载部分'''
            c._load_buff(c.buffs,c._check1,env)
            
            if not self.cb_mode2.currentIndex()==2:
                try:
                    ae1 = self._aeffect[self.cb_aeffect1.currentText()]
                    ae2 = self._aeffect[self.cb_aeffect2.currentText()]
                    assert(int(ae1['n'])+int(ae2['n'])<=4)
                    c._load_buff(ae1['buffs'],c._check1,env)
                    c._load_buff(ae2['buffs'],c._check1,env)
                except:
                    fail_info.append("圣遗物套装信息错误")
                    logging.getLogger('1').error(traceback.format_exc())
                    raise ValueError

            logging.getLogger('Buff').info("总效果: {}\n".format(c.skill_effect))
            logging.getLogger('Buff').info("特殊攻击加成: {}\n".format(c.sp_buff))


            logging.getLogger('1').info(enemy)
            c.enemy = enemy         
            
            rls = Articraft()
            '''其他增益加载部分'''
            rm_sub={'ed':self.digit_ed.value(),'dphys':self.digit_fd.value(),'d':self.digit_alld.value(),'sa':self.digit_benett.value()}
            c.load_att(rm_sub)  
            
                      





            if self.cb_mode2.currentIndex()==2:
                try:
                    cal_data={}
                    trans_pos = ['head','glass','cup','flower','feather']
    
                    for apos in trans_pos:
                        cal_data[apos]=[]
                        tmp = getattr(self,apos)
                        assert len(tmp.record)>=1
                        for jjj in tmp.record:
                            cal_data[apos].append(get_info_by_id(int(jjj.split('_')[0])))
                    cal_data['sub']=[{'cr':0,'name':'empty'}]
                except:
                    fail_info.append("圣遗物选择错误")
                    raise ValueError
                
                save = run_thru_data(cal_data,self._aeffect,c,rls,self.pbar,self._ksort)
            if self.cb_mode2.currentIndex()==0:
                rls.load_json("./data/artifacts/sub.json")
                cal_data = mainlist
                cal_data['sub']=[{'cr':0,'name':'emtpy'}]
                save = run_thru_data(cal_data,self._aeffect,c,rls,self.pbar,self._ksort)
            if self.cb_mode2.currentIndex()==1:
                blist=[[self.trans1[self.cb_main_head.currentText()]],[self.trans1[self.cb_main_glass.currentText()]],[self.trans1[self.cb_main_cup.currentText()]],['sh'],['sa']]
                run_list = gen_sublist(self.spb_nsub.value(),self.save_sub_list)
                # print(self.save_sub_list)
                prop_list = ['ar','ed','cr','cd','dphys','sa','sh','dr','em','hr','dheal','ef']
                trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875,6.0128,1.5,1.1428,1.1543,1.6656]
                assert len(self.save_sub_list)>0
                for i in range(len(run_list)):
                    run_list[i]['name'] = rename(run_list[i])
                    for j in run_list[i]:
                        if j!='name':
                            run_list[i][j] = trans_ratio[prop_list.index(j)]*2.8*run_list[i][j]
                    
                cal_data = gen_mainlist(blist)
                cal_data["sub"] = run_list
                save = run_thru_data(cal_data,self._aeffect,c,rls,self.pbar,self._ksort)
            if self.cb_mode2.currentIndex()==3:
                save = {}
                run_list = gen_sublist(self.spb_nsub.value(),self.save_sub_list)
                # print(self.save_sub_list)
                prop_list = ['ar','ed','cr','cd','dphys','sa','sh','dr','em','hr','dheal','ef']
                trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875,6.0128,1.5,1.1428,1.1543,1.6656]
                assert len(self.save_sub_list)>0
                for i in range(len(run_list)):
                    run_list[i]['name'] = rename(run_list[i])
                    for j in run_list[i]:
                        if j!='name':
                            run_list[i][j] = trans_ratio[prop_list.index(j)]*2.8*run_list[i][j]
                cdata = {}
                N=1
                num_cycle = len(mainlist['head'])*len(mainlist['glass'])*len(mainlist['cup'])
                for h1 in mainlist['head']:
                    for g1 in mainlist['glass']:
                        for c1 in mainlist['cup']:
                            cdata['head'] = [h1]
                            cdata['glass'] = [g1]
                            cdata['cup'] = [c1]
                            cdata['feather'] = mainlist['feather']
                            cdata['flower'] = mainlist['flower']
                            cdata["sub"] = run_list
                            tmp_rsl = run_thru_data(cdata,self._aeffect,c,rls,self.pbar,self._ksort,num_cycle,N)
                            tmp_rsl = OrderedDict(sorted(tmp_rsl.items(),reverse=True))
                            for i in tmp_rsl:
                                key = i
                                while key in save:
                                    key-=1
                                save[key] = deepcopy(tmp_rsl[i])
                                break
                            N+=1

            '''结果输出部分'''

                
            test = OrderedDict(sorted(save.items(),reverse=True))
            N=0
            limit = self.spb_num_display.value()
            for i in test:
                if N>3:
                    self.tbl_2.setColumnCount(N+1)
                tmp2 = list(test[i][1].keys())
                if 'sub_test' in tmp2:
                    tmp2.remove('sub_test')
                if 'sub' in tmp2:
                    tmp2.remove('sub')
                tmp2 = [_.split('_')[1] for _ in tmp2]
                tmp0 = test[i][0]
                logging.getLogger('1').info("结果：\n {}{}{}\n{}".format(character,constellation,c.equipment[0],pprint.pformat(tmp0,indent=4)))
                logging.getLogger('1').info("圣遗物：\n{}".format(pprint.pformat(test[i][1],indent=4)))

                if self.rb_display.isChecked():
                    content = [i]+tmp2+[tmp0['shld'],tmp0['heal'],tmp0['maxhp'],tmp0['sum']]+[ps2(tmp0['perc_a']),ps2(tmp0['perc_e']),ps2(tmp0['perc_q']),ps2(tmp0['ratio2'])]              
                else:
                    content = [ps1(i)]+tmp2+[ps1(tmp0['shld']),ps1(tmp0['heal']),ps1(tmp0['maxhp']),ps1(tmp0['sum'])]+[ps2(tmp0['perc_a']),ps2(tmp0['perc_e']),ps2(tmp0['perc_q']),ps2(tmp0['ratio2'])]                 
                for i in range(len(content)):
                    item =  QTableWidgetItem(str(content[i]))

                    item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    self.tbl_2.setItem(i, N,item)

                N+=1

                if N==limit:
                    break

            self.statusBar().showMessage("计算成功",2000)
            self.tabs.setCurrentIndex(0)

        except Exception as e:
            fail_info.append("计算失败")
            self.statusBar().showMessage("/".join(fail_info),3000)
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
            self.digit_sa.setValue(self._sub_data['sa']) 
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
        data['sa'] = self.digit_sa.value()
        data['sd'] = self.digit_sd.value()
        data['sh'] = self.digit_sh.value()
        data['hr'] = self.digit_hr.value()
        data['em'] = self.digit_em.value()
        save = {}
        save['sub'] = data
        with open(path, 'w', encoding='UTF-8') as fp:
            json.dump(save, fp,indent = 4)


    def _set_cbox(self,pos,data):
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
                        

            




    def show_rec(self):
        if self.cb_mode2.currentIndex()==2:
            self.tabs.setTabEnabled(2,False)
            self.tabs.setTabEnabled(3,True)
            self.tabs.setCurrentIndex(3)
        else:
            self.tabs.setTabEnabled(2,True)
            self.tabs.setTabEnabled(3,False)
            self.tabs.setCurrentIndex(2)
            if self.cb_mode2.currentIndex()==0:
                self.grp_head.show()
                self.grp_glass.show()
                self.grp_cup.show()
                self.grp_sub.show()
                self.groupBox_11.hide()
                self.groupBox.hide()
            if self.cb_mode2.currentIndex()==1:
                self.grp_head.hide()
                self.grp_glass.hide()
                self.grp_cup.hide()
                self.grp_sub.hide()
                self.groupBox_11.show()
                self.groupBox.show()
            if self.cb_mode2.currentIndex()==3:
                self.grp_head.show()
                self.grp_glass.show()
                self.grp_cup.show()
                self.grp_sub.hide()
                self.groupBox_11.show()
                self.groupBox.hide()
            
    def reset(self):
        self.cb_cnum.clear()
        self.win_ratio.wpn = ''
        self.reset_table()
        self.load_info()
        # self.win_rec_a.update(self.current_role)


    def reset_table(self):
        bbb ={'伤害':10,'护盾':7,'生命':9,'治疗':8}
        self.win_ratio.cnum = 'c'+str(self.cb_cnum.currentText())

        for i in range(self.tbl_2.rowCount()):
            for j in range(4):
                self.tbl_2.setItem(i, j,QTableWidgetItem(""))
            self.tbl_2.setRowHidden(i,False)
        text = self.cb_sort.currentText()
        self.tbl_2.setRowHidden(bbb[text],True)
        self.pbar.setValue(0)
        self.win_save_act.update(self.current_role,self.cb_cnum.currentText())   
        if not self.cb_mode2.currentIndex()==2:
            self.tbl_2.setRowHidden(4,True)
            self.tbl_2.setRowHidden(5,True)
        if self.cb_mode2.currentIndex()==0 or self.cb_mode2.currentIndex()==2:
            self.tbl_2.setRowHidden(6,True)

        self.statusBar().showMessage("重置结果",1000)
         
        
        
         
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
        # self.cb_cnum.addItems(self._data[self.current_role]['c'])
        self.cb_cnum.addItems(["0","1","2","3","4","5","6"])
        self.statusBar().showMessage("信息重新加载",1000)


    
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

    
