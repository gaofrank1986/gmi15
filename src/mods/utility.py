import json
from copy import deepcopy
from PyQt5 import QtWidgets,QtGui,QtCore
from os import listdir
import logging
from datetime import datetime
from .ocr import cn
from time import sleep
import os



def extract_name3(a):
    if a == 'phys':
        ans = '物理伤害'
    if a == 'elem':
        ans = '属性元素'
    if a == 'env':
        ans = '环境元素'
    if a == 'shld':
        ans = '技能护盾'
    if a == 'heal':
        ans = '技能治疗'
    if a == 'buff':
        ans = '特殊增益'
    if a == 'base':
        ans = '技能基数'
    return(ans)

class Caculator(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progress = QtCore.pyqtSignal(float)
    # maximum = QtCore.pyqtSignal(int)
    result = QtCore.pyqtSignal(dict)
    log1 = QtCore.pyqtSignal(str)

    def __init__(self,cdata,affect,c,rls,ksort,log):
        super(QtCore.QObject,self).__init__()
        self.cdata = cdata
        self.affect = affect
        self.rls = rls
        self.c = c
        self.ksort = ksort
        self.log = log

    def test(self):
        """Long-running task."""
        try:
            for i in range(1000000):
                # sleep(1)
                # logging.getLogger('1').info("test")
                print(i)
                self.progress.emit(i /10000)

            # save = run_thru_data(cal_data,aeffect,c,rls,ksort = ksort,log=log)
            self.finished.emit()
            # self.result.emit(save)
        except:
            traceback.print_exc()


    def run(self,count_cycle=1,current_cycle=1):
        # logger = logging.getLogger('Main')
        cdata = self.cdata
        affect = deepcopy(self.affect)
        c = self.c
        rls = self.rls
        ksort = self.ksort
        log = self.log


        alist = extract_rlist(affect)

        save = dict()
        diluc = deepcopy(c)
        total = 1
        acc = 1

        for i in cdata:
            total =total*len(cdata[i])
        # total =total*len(cdata['head'])
        total = total*count_cycle
        # print(total)
        # self.maximum.emit(total)
        start = datetime.now()


        # if log:
        #     logging.getLogger('1').info(cdata)
        #     logging.getLogger('1').info("alist{}".format(alist))
        # else:
        #     logging.getLogger('Buff').setLevel(logging.CRITICAL)
        #     logging.getLogger('Main').setLevel(logging.CRITICAL)


        self.log1.emit("穷举次数{}".format(total))
        for hdata in cdata['head']:
            e_dict = { _:0 for _ in alist}

            hd_name = 'hd_'+hdata['name']
            rls.add(hdata,hd_name)

            assert(hdata['set'] in e_dict)
            e_dict[hdata['set']] = e_dict[hdata['set']]+1
            str1 = "理之冠: {} ".format(hdata)

            for gdata in cdata['glass']:
                gl_name = 'gl_'+gdata['name']
                rls.add(gdata,gl_name)
                assert(gdata['set'] in e_dict)
                e_dict2 = deepcopy(e_dict)
                e_dict2[gdata['set']] += 1
                str2 = "时之沙: {}".format(gdata)

                for cpdata in cdata['cup'] :
                    cp_name = 'cp_'+cpdata['name']
                    rls.add(cpdata,cp_name)
                    # if 'set' in cpdata:
                    # print(cpdata['set'])
                    assert(cpdata['set'] in e_dict)
                    e_dict3 = deepcopy(e_dict2)
                    e_dict3[cpdata['set']] += 1
                    str3 = "空之杯: {}".format(cpdata)
                    for fldata in cdata['flower']:
                        fl_name = 'fl_'+fldata['name']
                        rls.add(fldata,fl_name)
                        assert(fldata['set'] in e_dict)
                        e_dict4 = deepcopy(e_dict3)
                        e_dict4[fldata['set']] += 1
                        str4 = "生之花: {}".format(fldata)

                        for ftdata in cdata['feather']:
                            ft_name = 'ft_'+ftdata['name']
                            rls.add(ftdata,ft_name)
                            assert(ftdata['set'] in e_dict)
                            e_dict5 = deepcopy(e_dict4)
                            e_dict5[ftdata['set']] += 1
                            str5 = "死之羽: {}".format(ftdata)

                            for subdata in cdata['sub']:
                                sub_name = 'sub_'+subdata['name']
                                rls.add(subdata,sub_name)
                                str6 = "副词条: {}".format(subdata)

                                # if log:
                                #     logger.info("##############################################")
                                #     logger.info("#############     穷举第{}次     #################".format(acc))
                                #     logger.info("##############################################")
                                #     logger.info("##############################################")
                                #     logger.info(str1)
                                #     logger.info(str2)
                                #     logger.info(str3)
                                #     logger.info(str4)
                                #     logger.info(str5)
                                #     logger.info(str6)

                                pvalue = acc+total/count_cycle*(current_cycle-1)
                                # print(pvalue,total,count_cycle,current_cycle)
                                print(pvalue,total)
                                self.progress.emit(float(pvalue/total)*100)
                                acc+=1
                                diluc.put_on(rls)
                                tmp2 = deepcopy(diluc)
                                # logger.info(e_dict5)
                                logging.getLogger('3').info("===========录入圣遗物穷举{}===========".format(acc-1))
                                for i in e_dict5:
                                    if i!='无':
                                        if e_dict5[i] >=4 and i+'4' in affect:
                                            tmp2._load_buff(affect[i+'4']['buffs'],tmp2._check1,tmp2.env)
                                        if e_dict5[i] >=4 and not i+'4' in affect and i+'2' in affect:
                                            tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
                                        if e_dict5[i] >=2 and e_dict5[i] <4 and i+'2' in affect:
                                            tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
                                ans = deepcopy(tmp2.damage_rsl())
                                if ksort == 1:
                                    tmp = ans['sum']
                                if ksort == 3:
                                    tmp = ans['maxhp']
                                if ksort == 4:
                                    tmp = ans['heal']
                                if ksort == 2:
                                    tmp = ans['shld']
                                while (tmp in save.keys()):
                                    tmp = tmp-1
                                save[tmp] = [ans,deepcopy(rls.buf)]

                                diluc.take_off(rls)
                                rls.rm2(sub_name)
                            rls.rm2(ft_name)
                        rls.rm2(fl_name)
                    rls.rm2(cp_name)
                rls.rm2(gl_name)
            rls.rm2(hd_name)

        self.log1.emit('Time: {}'.format(datetime.now() - start))


        self.result.emit(save)
        self.finished.emit()



def run_thru_data(cdata,affect,c,rls,ksort=1):

    alist = extract_rlist(affect)

    save = dict()
    diluc = deepcopy(c)

    start = datetime.now()

    for hdata in cdata['head']:
        e_dict = { _:0 for _ in alist}

        hd_name = 'hd_'+hdata['name']
        rls.add(hdata,hd_name)

        assert(hdata['set'] in e_dict)
        e_dict[hdata['set']] = e_dict[hdata['set']]+1
        str1 = "理之冠: {} ".format(hdata)

        for gdata in cdata['glass']:
            gl_name = 'gl_'+gdata['name']
            rls.add(gdata,gl_name)
            assert(gdata['set'] in e_dict)
            e_dict2 = deepcopy(e_dict)
            e_dict2[gdata['set']] += 1
            str2 = "时之沙: {}".format(gdata)

            for cpdata in cdata['cup'] :
                cp_name = 'cp_'+cpdata['name']
                rls.add(cpdata,cp_name)
                # if 'set' in cpdata:
                # print(cpdata['set'])
                assert(cpdata['set'] in e_dict)
                e_dict3 = deepcopy(e_dict2)
                e_dict3[cpdata['set']] += 1
                str3 = "空之杯: {}".format(cpdata)
                for fldata in cdata['flower']:
                    fl_name = 'fl_'+fldata['name']
                    rls.add(fldata,fl_name)
                    assert(fldata['set'] in e_dict)
                    e_dict4 = deepcopy(e_dict3)
                    e_dict4[fldata['set']] += 1
                    str4 = "生之花: {}".format(fldata)

                    for ftdata in cdata['feather']:
                        ft_name = 'ft_'+ftdata['name']
                        rls.add(ftdata,ft_name)
                        assert(ftdata['set'] in e_dict)
                        e_dict5 = deepcopy(e_dict4)
                        e_dict5[ftdata['set']] += 1
                        str5 = "死之羽: {}".format(ftdata)

                        for subdata in cdata['sub']:
                            sub_name = 'sub_'+subdata['name']
                            rls.add(subdata,sub_name)
                            str6 = "副词条: {}".format(subdata)

                            diluc.put_on(rls)
                            tmp2 = deepcopy(diluc)

                            for i in e_dict5:
                                if i!='无':
                                    if e_dict5[i] >=4 and i+'4' in affect:
                                        tmp2._load_buff(affect[i+'4']['buffs'],tmp2._check1,tmp2.env)
                                    if e_dict5[i] >=4 and not i+'4' in affect and i+'2' in affect:
                                        tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
                                    if e_dict5[i] >=2 and e_dict5[i] <4 and i+'2' in affect:
                                        tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
                            ans = deepcopy(tmp2.damage_rsl())
                            if ksort == 1:
                                tmp = ans['sum']
                            if ksort == 3:
                                tmp = ans['maxhp']
                            if ksort == 4:
                                tmp = ans['heal']
                            if ksort == 2:
                                tmp = ans['shld']
                            while (tmp in save.keys()):
                                tmp = tmp-1
                            save[tmp] = [ans,deepcopy(rls.buf)]

                            diluc.take_off(rls)
                            rls.rm2(sub_name)
                        rls.rm2(ft_name)
                    rls.rm2(fl_name)
                rls.rm2(cp_name)
            rls.rm2(gl_name)
        rls.rm2(hd_name)

    logging.getLogger('1').info('Time: {}'.format(datetime.now() - start))

    return(save)


def gen_sublist(n,alist):
    ans=[]
    assert len(alist)<5
    if len(alist)==1:
        return([{alist[0]:n}])
    else:
        for i in range(n+1):
            tmp1 ={}
            tmp1[alist[0]] = i
            for acase in gen_sublist(n-i,alist[1:]):
                tmp2 = deepcopy(tmp1)
                for k in acase:
                    tmp2[k] = acase[k]
                ans.append(tmp2)
        return ans



class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.setStyleSheet("background-color: rgb(224, 234, 244);")

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MyDialog(QtWidgets.QDialog, QtWidgets.QPlainTextEdit):
    def __init__(self, parent, name,fmt):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        # logTextBox.setFormatter(logging.Formatter("%(asctime)s — %(message)s",datefmt='%m-%d,%H:%M'))
        # logging.getLogger('Main').addHandler(logTextBox)
        logTextBox.setFormatter(fmt)
        logging.getLogger(name).addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger(name).setLevel(logging.DEBUG)
        logging.getLogger(name).propagate = False



        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)

        self.save = logTextBox.widget
        self.resize(1300, 500)




    def clear(self):
        self.save.setPlainText("")



class MyDialog2(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QtWidgets.QVBoxLayout()
        # Add the new logging box widget to the layout
        self.save = QtWidgets.QPlainTextEdit()
        layout.addWidget(self.save)
        self.setLayout(layout)

        self.resize(1300, 500)

    def clear(self):
        self.save.setPlainText("")

    def display(self):
        if os.path.exists("./data/logs/2.log"):
            with open("./data/logs/2.log","r") as fp:
                cache = fp.readlines()
            self.save.setPlainText('\n'.join(cache))
        self.exec_()


def parse_formula(s):
    a = s.split("+")
    ans = []
    for j in a:
        if len(j.split('*')) == 1:
            ans.append((j,'1'))
        elif len(j.split('*')) == 2:
            tmp = j.split('*')
            assert('e' in tmp[1] or 'a' in tmp[1] or 'q' in tmp[1] or tmp[1]=='ks')
            ans.append((tmp[1],tmp[0]))
        else:
          raise ValueError("invalid formula: {}".format(s))
    return(ans)

def ps1(i):
    assert(isinstance(i,int) or isinstance(i,float))
    if i<10000:
        return i
    return str(round(i/10000,1))+'万'

def ps2(i):
    s = "{:.1f}%".format(i*100)
    return s

def ps(s):
    s = s.replace('(测试无效果)','')
    s = s[:-1]
    return(s)

def extract_rlist(data):
    assert isinstance(data,dict)
    alist = list(data.keys())
    alist = list(ps(_) for _ in  alist)
    blist=[]
    for i in alist:
        if i not in blist:
            blist.append(i)
    return(blist)

def rename(a):
    assert isinstance(a,dict)
    s = cn()
    ans=''
    for i in a:
        ans+='{}{}\n'.format(s.trans2[i],a[i])
    return(ans[:-1])

def gen_mainlist(blist):

    alist = ['head','glass','cup','flower','feather']
    basic_main_rate = 31.1#满爆率
    lang = cn()

    prop_list = ['ar','ed','cr','cd','dphys','sa','sh','dr','em','hr','dheal','ef']
    trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875,6.0128,1.5,1.1428,1.1543,1.6656]
    ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

    ans = dict()
    for i in alist:
        ans[i] = []
        for j in blist[alist.index(i)]:
            tmp = dict()
            tmp[j] = round(basic_main_rate*ratio_main[j],2)
            tmp['name'] = lang.trans2[j]
            tmp['set'] = '无'
            ans[i].append(tmp.copy())

    return(ans)