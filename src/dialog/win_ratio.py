from PyQt5.QtWidgets import QDialog,QLineEdit,QLabel,QSpinBox,QTableWidgetItem,QDialogButtonBox
from PyQt5.uic import loadUi
import traceback
import json
from PyQt5 import QtCore, QtGui, QtWidgets
import logging

from ..mods.utility import extract_name3
from ..mods.db_setup import CRatio,db_session,RWData,Buff_Def
import re
class Win_Ratio(QDialog):
    def __init__(self,role,sbar):
        super(Win_Ratio,self).__init__()
        loadUi("./data/ui/win_ratio.ui",self)
        # self.pb_save.clicked.connect(self.save)

        # self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)
        self.pb_reset.clicked.connect(self.reset)
        self.pb_save.clicked.connect(self.save)
        self.pb_close.clicked.connect(self.close)
        # self.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.Cancel)
        # self.table_ratio.cellChanged.connect(self.update)
        # self._data = data
        self.sbar=sbar
        self.role = role
        self.cnum = 'c0'
        self.wpn = ''
        self.t2 = {'cr':'暴击','cd':'暴伤','hr':'生命%','ar':'攻击%','dr':'防御%','em':'精通','ef':'充能','dheal':'治疗','ed':'属伤','dphys':'物伤','basic_health':'基础生命','basic_attack':'基础攻击','basic_defense':'基础防御'}


        header = self.table_ratio.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header = self.table_ratio.verticalHeader()
        header.setVisible(False)


        header = self.table_value.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header = self.table_value.verticalHeader()
        header.setVisible(False)

        header = self.tb_buff_def.horizontalHeader()
        for i in range(0,10):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
            # header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header = self.tb_buff_def.verticalHeader()
        header.setVisible(False)

    def close(self):
        self.hide()

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
                print(key,value)
                try:
                    if (re.match(r'^-?\d+(?:\.\d+)$', value) is None) and not(value.isdigit()):
                        raise ValueError
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

            rw1 = db_session.query(RWData).filter(RWData.name==self.role).first()
            rw2 = db_session.query(RWData).filter(RWData.name==self.wpn).first()
            for i in range(self.table_value.rowCount()):
                k = self.table_value.item(i,0).text()
                key = self.table_value.item(i,1).text()
                value = self.table_value.item(i,2).text()

                try:
                    if (re.match(r'^-?\d+(?:\.\d+)$', value) is None) and not(value.isdigit()):
                        raise ValueError
                except:
                    # print("error",key,i)
                    self.sbar.showMessage('输入值错误')
                    raise ValueError
                if k == '人物':
                    if key in ['basic_attack','basic_health','basic_defense']:
                        setattr(rw1,key,value)
                    else:
                        rw1.break_thru = key
                        rw1.break_thru_v = value
                if k == '武器':
                    if key in ['basic_attack','basic_health','basic_defense']:
                        setattr(rw2,key,value)
                    else:
                        rw2.break_thru = key
                        rw2.break_thru_v = value

            for i in range(self.tb_buff_def.rowCount()):
                key= self.tb_buff_def.item(i,0).text()
                ans=[]
                if not key in ['w1','w2']:
                    filtr = self.role+'_'+key
                else:
                    filtr = self.wpn+'_'+key
                save = db_session.query(Buff_Def).filter(Buff_Def.key==filtr).first()
                exist = True
                if save is None:
                    exist = False
                    save = Buff_Def()
                    save.key = filtr

                for k in range(1,10):
                    ans.append(self.tb_buff_def.item(i,k).text())
                save.value = '||'.join(ans)
                if not exist:
                    db_session.add(save)
                else:
                    db_session.commit()

            db_session.commit()
            self.sbar.showMessage('基础值存储成功')

        except:
            db_session.rollback()
            traceback.print_exc()
            logging.getLogger('1').info(traceback.format_exc())
            self.sbar.showMessage('存储错误')


    def update(self,row,column):
        # self.cname = role
        print(row,column)

    def display(self):
        self.tabs.setCurrentIndex(0)
        try:
            logging.getLogger('1').info('{}{}'.format(self.role,self.cnum,self.wpn))
            while (self.table_ratio.rowCount() > 0):
                self.table_ratio.removeRow(0)

            while (self.table_value.rowCount() > 0):
                self.table_value.removeRow(0)
            while (self.tb_buff_def.rowCount() > 0):
                self.tb_buff_def.removeRow(0)

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

            with open('./data/character/'+self.role+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            data = data['90']
            self.show_value2(data,self.role)

            if not self.wpn == '':
                loc = self.wpn.split('_')[0]
                key = self.wpn.split('_')[1]
                with open('./data/weapon/'+loc+'.json', 'r', encoding='UTF-8') as fp:
                    data = json.load(fp)
                data = data[key]
                self.show_value2(data,self.wpn,kind='武器')

            #=======================


            self.exec_()
        except Exception as e:
            self.sbar.showMessage("技能显示失败",1000)
            print("Error: ", e)
            traceback.print_exc()

    def reset(self):
        while (self.table_value.rowCount() > 0):
            self.table_value.removeRow(0)
        with open('./data/character/'+self.role+'.json', 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        data = data['90']
        self.show_value2(data,self.role,enforce=True)

        if not self.wpn == '':
            loc = self.wpn.split('_')[0]
            key = self.wpn.split('_')[1]
            with open('./data/weapon/'+loc+'.json', 'r', encoding='UTF-8') as fp:
                data = json.load(fp)
            data = data[key]
            self.show_value2(data,self.wpn,kind='武器',enforce=True)

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
                        print(i,re.match(r'^-?\d+(?:\.\d+)$', i),i.isdigit())
                        if (re.match(r'^-?\d+(?:\.\d+)$', i) is None) and not(i.isdigit()):
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

                self.tb_buff_def.insertRow(base+i)
                item =  QTableWidgetItem(keys2[i])
                self.tb_buff_def.setItem(base+i,0,item)
                # print("test",keys2[i],base+i)
                if not keys2[i] in ["w1","w2"]:
                    save = db_session.query(Buff_Def).filter(Buff_Def.key==self.role+'_'+keys2[i]).first()
                else:
                    save = db_session.query(Buff_Def).filter(Buff_Def.key==self.wpn+'_'+keys2[i]).first()

                if save is None:
                    ans = ['0']*9
                else:
                    ans = save.value.split('||')
                for k in range(0,9):
                    item = QTableWidgetItem(ans[k])
                    self.tb_buff_def.setItem(base+i,k+1,item)


    def show_value2(self,rawdata,fltr,kind='人物',enforce=False):
        saved = db_session.query(RWData).filter(RWData.name==fltr).first()

        if not enforce:
            if saved is None:
                data = rawdata
                rw1 = RWData()
                rw1.name = fltr

                for key in data:
                    value = data[key]
                    if key in ['basic_attack','basic_health','basic_defense']:
                        setattr(rw1,key,str(value))
                        print(key,value)
                    if key == 'break_thru':
                        rw1.break_thru = list(value.keys())[0]
                        rw1.break_thru_v = value[rw1.break_thru]
                db_session.add(rw1)
                db_session.commit()

            else:
                data = {}
                if kind == '人物':
                    data['basic_health'] = saved.basic_health
                data['basic_attack'] = saved.basic_attack
                if kind == '人物':
                    data['basic_defense'] = saved.basic_defense
                data['break_thru'] = {}
                data['break_thru'][saved.break_thru] = saved.break_thru_v
        else:
            data = rawdata



        base = self.table_value.rowCount()
        N=0
        for i in data:
            # print(i,data[i])
            if i in ['name','level','buffs']:
                continue
            if i != 'break_thru':
                key = i
                value  = data[i]
            else:
                key = list(data['break_thru'].keys())[0]
                value = data['break_thru'][key]

            self.table_value.insertRow(base+N)
            item =  QTableWidgetItem(kind)
            self.table_value.setItem(base+N,0,item)
            item =  QTableWidgetItem(key)
            self.table_value.setItem(base+N,1,item)
            item =  QTableWidgetItem(str(value))
            self.table_value.setItem(base+N,2,item)
            item =  QTableWidgetItem(self.t2.get(key,key))
            self.table_value.setItem(base+N,3,item)

            N+=1
