import json
from copy import deepcopy
from PyQt5 import QtWidgets,QtGui
from os import listdir
from PyQt5 import QtCore
import logging 





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




def run_thru_data(cdata,affect,c,rls,pbar,ksort=1):
    logging.getLogger('1').info(cdata)
    logger = logging.getLogger('Main')

    alist = extract_rlist(affect)
    
    save = dict()
    diluc = deepcopy(c)
    total = 1
    acc = 1

    for i in cdata:
        total =total*len(cdata[i])


    logging.getLogger('1').info("alist{}".format(alist))
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
                        
                        logger.info("##############################################")
                        logger.info("#############     穷举第{}次     #################".format(acc))
                        logger.info("##############################################")
                        logger.info("##############################################")
                        logger.info(str1)
                        logger.info(str2)
                        logger.info(str3)
                        logger.info(str4)
                        logger.info("死之羽: {}".format(ftdata))
                        
                        pbar.setValue(float(acc/total)*100)
                        acc+=1
                        diluc.put_on(rls)                                                
                        tmp2 = deepcopy(diluc)
                        logger.info(e_dict5)
                        logging.getLogger('Buff').info("===========录入圣遗物穷举{}===========".format(acc-1))
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
                        rls.rm2(ft_name)        
                    rls.rm2(fl_name)                                 
                rls.rm2(cp_name)        
            rls.rm2(gl_name)        
        rls.rm2(hd_name)
        
    return(save)



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

def trans(i):
    assert(isinstance(i,int) or isinstance(i,float))
    if i<10000:
        return i
    return str(round(i/10000,1))+'万'

def trans2(i):
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