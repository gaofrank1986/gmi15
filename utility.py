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
        ans = '增益'
    if a == 'base':
        ans = '技能基数'
    return(ans)   

    



# def run_thru(path,c,rls,pbar,ksort=1):
#     logger = logging.getLogger('Main')
#     with open(path, 'r', encoding='UTF-8') as fp:
#         data = json.load(fp)
#     save = dict()
#     diluc = deepcopy(c)
#     total = 1
#     acc = 1
#     total = len( data['head'])*len( data['glass'])*len( data['cup'])
#     for head in data['head']: 
#         for glass in data['glass']:
#             for cup in data['cup']:
#                 # print(acc,total)
#                 pbar.setValue(float(acc/total)*100)
#                 flower = data['flower'][0]
#                 feather = data['feather'][0]
        
#                 rls.add(head,'head')
#                 rls.add(glass,'glass')        
#                 rls.add(cup,'cup')
#                 rls.add(flower,'flower')
#                 rls.add(feather,'feather')

#                 diluc.put_on(rls)
#                 logger.info("理之冠: {}".format(head))
#                 logger.info("时之沙: {}".format(glass))
#                 logger.info("空之杯: {}".format(cup))
#                 logger.info("副词条: {}".format(rls.buf['sub']))

#                 ans = deepcopy(diluc.damage_rsl())
#                 if ksort == 1:
#                     tmp = ans['sum']
#                 if ksort == 3:
#                     tmp = ans['maxhp']
#                 if ksort == 4:
#                     tmp = ans['heal']
#                 if ksort == 2:
#                     tmp = ans['shld']
#                 while (tmp in save.keys()):
#                     tmp = tmp-1
#                 save[tmp] = [ans,deepcopy(rls.buf)]

#                 diluc.take_off(rls)
#                 rls.rm(feather,'feather')
#                 rls.rm(flower,'flower')
#                 rls.rm(cup,'cup')
#                 rls.rm(glass,'glass')
#                 rls.rm(head,'head')
#                 acc+=1
#     return(save)

# def run_thru_folders(path,affect,c,rls,pbar,ksort=1):
#     logger = logging.getLogger('Main')

#     alist = list(affect.keys())
#     alist = list(set([_[:-1] for _ in  alist]))
#     alist[0] = '无'
    
#     save = dict()
#     diluc = deepcopy(c)
#     total = 1
#     acc = 1
#     # total = len( data['head'])*len( data['glass'])*len( data['cup'])
#     pos = ['head','glass','cup','flower','feather']
#     dirs =[]
#     gen_list=[]
#     for i in pos:
#         folder = path+i+"/"
#         dirs.append(folder)
#         logger.info(dirs[-1])
#         gen_list.append([f for f in listdir(folder) if f.endswith('.json')])
#         logger.info(gen_list[-1])
#         assert len(gen_list[-1])>=1
#         total =total*len(gen_list[-1])
        
#     for hfile in gen_list[0]:
#         e_dict = { _:0 for _ in alist}
#         # print(hfile)
#         with open(dirs[0]+hfile, 'r', encoding='UTF-8') as fp:
#             data = json.load(fp)
#         head = data['sub']
#         for i in data['main']:
#             head[i] = head.get(i,0)+data['main'][i]
#         hd_name = 'hd_'+hfile.split('.')[0]
#         rls.add(head,hd_name)
#         assert(data['set'] in e_dict)
#         e_dict[data['set']] = e_dict[data['set']]+1
#         str1 = "{} 理之冠: {} {}".format(hd_name,head,data['set'])
#         # logger.info("理之冠: {} {}".format(head,data['set']))

#         for gfile in gen_list[1]:
#             with open(dirs[1]+gfile, 'r', encoding='UTF-8') as fp:
#                 data = json.load(fp)
#             glass = data['sub']
#             for i in data['main']:
#                 glass[i] = glass.get(i,0)+data['main'][i]
#             gl_name = 'gl_'+gfile.split('.')[0]
#             rls.add(glass,gl_name) 
#             e_dict2 = deepcopy(e_dict)
#             assert(data['set'] in e_dict2)
#             e_dict2[data['set']] = e_dict2[data['set']]+1       
#             str2 = "{} 时之沙: {} {}".format(gl_name,glass,data['set'])
            
#             for cfile in gen_list[2] :
#                 with open(dirs[2]+cfile, 'r', encoding='UTF-8') as fp:
#                     data = json.load(fp)
#                 cup = data['sub']
#                 for i in data['main']:
#                     cup[i] = cup.get(i,0)+data['main'][i]
#                 cp_name = 'cp_'+cfile.split('.')[0]
#                 rls.add(cup,cp_name) 
#                 e_dict3 = deepcopy(e_dict2)
#                 assert(data['set'] in e_dict3)
#                 e_dict3[data['set']] = e_dict3[data['set']]+1
#                 str3 = "{} 空之杯: {} {}".format(cp_name ,cup,data['set'])                      
#                 for flfile in gen_list[3]:
#                     with open(dirs[3]+flfile, 'r', encoding='UTF-8') as fp:
#                         data = json.load(fp)
#                     flower = data['sub']
#                     for i in data['main']:
#                         flower[i] = flower.get(i,0)+data['main'][i]
#                     fl_name = 'fl_'+flfile.split('.')[0]
#                     rls.add(flower,fl_name)
#                     e_dict4 = deepcopy(e_dict3)
#                     assert(data['set'] in e_dict4)
#                     e_dict4[data['set']] = e_dict4[data['set']]+1
#                     str4 = "{} 生之花: {} {}".format(fl_name,flower,data['set'])
                    
#                     for ftfile in gen_list[4]:
#                         with open(dirs[4]+ftfile, 'r', encoding='UTF-8') as fp:
#                             data = json.load(fp)
#                         feather = data['sub']
#                         for i in data['main']:
#                             feather[i] = feather.get(i,0)+data['main'][i]
#                         ft_name = 'ft_'+ftfile.split('.')[0]
#                         rls.add(feather,ft_name) 
#                         e_dict5 = deepcopy(e_dict4)

#                         assert(data['set'] in e_dict5)
#                         e_dict5[data['set']] = e_dict5[data['set']]+1
#                         logger.info(str1)
#                         logger.info(str2)
#                         logger.info(str3)
#                         logger.info(str4)
#                         logger.info("{} 死之羽: {} {}".format(ft_name,feather,data['set']))
#                         pbar.setValue(float(acc/total)*100)
              
#                         acc+=1


#                         diluc.put_on(rls)
                                                
#                         tmp2 = deepcopy(diluc)
#                         # print(e_dict)
#                         logger.info(e_dict5)
#                         logging.getLogger('Buff').info("===========录入圣遗物穷举{}===========".format(acc-1))
#                         for i in e_dict5:
#                             if i!='无':
#                                 if e_dict5[i] >=4 and i+'4' in affect:
#                                     tmp2._load_buff(affect[i+'4']['buffs'],tmp2._check1,tmp2.env)
#                                 if e_dict5[i] >=4 and not i+'4' in affect:
#                                     tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
#                                 if e_dict5[i] >=2 and e_dict5[i] <4:
#                                     tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)                                    
#                         ans = deepcopy(tmp2.damage_rsl())
#                         if ksort == 1:
#                             tmp = ans['sum']
#                         if ksort == 3:
#                             tmp = ans['maxhp']
#                         if ksort == 4:
#                             tmp = ans['heal']
#                         if ksort == 2:
#                             tmp = ans['shld']
#                         while (tmp in save.keys()):
#                             tmp = tmp-1
#                         save[tmp] = [ans,deepcopy(rls.buf)]

#                         diluc.take_off(rls)
#                         rls.rm(feather,ft_name)        
#                     rls.rm(flower,fl_name) 
                                
#                 rls.rm(cup,cp_name)        

#             rls.rm(glass,gl_name)        

#         rls.rm(head,hd_name)

        
#     return(save)


def run_thru_data(cdata,affect,c,rls,pbar,ksort=1):
    print(cdata)
    logger = logging.getLogger('Main')

    alist = list(affect.keys())
    alist = list(set([_[:-1] for _ in  alist]))
    alist[0] = '无'
    
    save = dict()
    diluc = deepcopy(c)
    total = 1
    acc = 1

    for i in cdata:
        total =total*len(cdata[i])
        
    for hdata in cdata['head']:
        e_dict = { _:0 for _ in alist}
        
        hd_name = 'hd_'+hdata['name']
        rls.add(hdata,hd_name)
        assert(hdata['set'] in e_dict)
        e_dict[hdata['set']] = e_dict[hdata['set']]+1
        str1 = "{} 理之冠: {} {}".format(hd_name,hdata,hdata['set'])

        for gdata in cdata['glass']:
            gl_name = 'gl_'+gdata['name']
            rls.add(gdata,gl_name)
            assert(gdata['set'] in e_dict)
            e_dict2 = deepcopy(e_dict)
            e_dict2[gdata['set']] += 1 
            str2 = "{} 时之沙: {} {}".format(gl_name,gdata,gdata['set'])
            
            for cpdata in cdata['cup'] :
                cp_name = 'cp_'+cpdata['name']
                rls.add(cpdata,cp_name)
                # if 'set' in cpdata:
                assert(cpdata['set'] in e_dict)
                e_dict3 = deepcopy(e_dict2)
                e_dict3[cpdata['set']] += 1 
                str3 = "{} 空之杯: {} {}".format(cp_name,cpdata,cpdata['set'])                      
                for fldata in cdata['flower']:
                    fl_name = 'fl_'+fldata['name']
                    rls.add(fldata,fl_name)
                    assert(fldata['set'] in e_dict)
                    e_dict4 = deepcopy(e_dict3)
                    e_dict4[fldata['set']] += 1
                    str4 = "{} 生之花: {} {}".format(fl_name,fldata,fldata['set'])
                    
                    for ftdata in cdata['feather']:
                        ft_name = 'ft_'+ftdata['name']
                        rls.add(ftdata,ft_name)
                        assert(ftdata['set'] in e_dict)
                        e_dict5 = deepcopy(e_dict4)
                        e_dict5[ftdata['set']] += 1
                        
                        logger.info(str1)
                        logger.info(str2)
                        logger.info(str3)
                        logger.info(str4)
                        logger.info("{} 死之羽: {} {}".format(ft_name,ftdata,ftdata['set']))
                        
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
                                if e_dict5[i] >=4 and not i+'4' in affect:
                                    tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
                                if e_dict5[i] >=2 and e_dict5[i] <4:
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

# def generate_cdata(path):
#     with open(path, 'r', encoding='UTF-8') as fp:
#         data = json.load(fp)
#     for apos in data:
#         for aitem in data[apos]:
            
    
# def get_name(s):
    
# def run_recursive(cdata,depth,edict,info,alist,c,rls,pbar,ksort=1):

#     logger = logging.getLogger('Main')

#     # alist = list(affect.keys())
#     # alist = list(set([_[:-1] for _ in  alist]))
#     # alist[0] = '无'
#     pre={}
#     save = dict()
#     diluc = deepcopy(c)
#     total = 1
#     acc = 1
#     e_dict5={}

#     # for i in cdata:
#     #     total =total*len(cdata[i])
                            
#     for data in cdata[depth]:
#         name = pre[depth]+data['name']
#         rls.add(data,name)
#         assert(data['set'] in e_dict)
#         e_dict = deepcopy(e_dict)
#         e_dict[data['set']] += 1
        
#         # logger.info(str1)
#         # logger.info(str2)
#         # logger.info(str3)
#         # logger.info(str4)
#         info.append("{} 死之羽: {} {}".format(name,data,data['set']))
#         if depth >0:
#             depth-=1
#             run_recursive(cdata,depth,edict,info,alist,c,rls,pbar,ksort)
#             rls.rm2(name)        

#         if depth==0:
        
#             pbar.setValue(float(acc/total)*100)
#             acc+=1
#             diluc.put_on(rls)                                                
#             tmp2 = deepcopy(diluc)
#             logger.info(e_dict5)
#             logging.getLogger('Buff').info("===========录入圣遗物穷举{}===========".format(acc-1))
#             for i in e_dict5:
#                 if i!='无':
#                     if e_dict5[i] >=4 and i+'4' in affect:
#                         tmp2._load_buff(affect[i+'4']['buffs'],tmp2._check1,tmp2.env)
#                     if e_dict5[i] >=4 and not i+'4' in affect:
#                         tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)
#                     if e_dict5[i] >=2 and e_dict5[i] <4:
#                         tmp2._load_buff(affect[i+'2']['buffs'],tmp2._check1,tmp2.env)                                    
#             ans = deepcopy(tmp2.damage_rsl())
#             if ksort == 1:
#                 tmp = ans['sum']
#             if ksort == 3:
#                 tmp = ans['maxhp']
#             if ksort == 4:
#                 tmp = ans['heal']
#             if ksort == 2:
#                 tmp = ans['shld']
#             while (tmp in save.keys()):
#                 tmp = tmp-1
#             save[tmp] = [ans,deepcopy(rls.buf)]

#             diluc.take_off(rls)
#             rls.rm2(name)
        
#     return(save)

class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

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