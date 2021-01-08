import json
from copy import deepcopy
# from PyQt5.QtCore import QAbstractTableModel,Qt
from PyQt5 import QtWidgets,QtGui

import logging 

# def generate_relics2():

#     alist = ['head','glass','cup','flower','feather']
#     blist=[['ar','cr','cd','dr'],['ar','dr'],['ar','ed','fd'],['sh'],['sa']]

#     basic_main_rate = 31.1#满爆率

#     prop_list = ['ar','ed','cr','cd','fd','sa','sh','dr']
#     trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875]
#     ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

#     ans = dict()
#     for i in alist:
#         ans[i] = []
#         for j in blist[alist.index(i)]:
#             tmp = dict()
#             tmp[j] = round(basic_main_rate*ratio_main[j],2)
#             ans[i].append(tmp.copy())

#     with open('./tmp/run_list.json', 'w+') as fp:
#         json.dump(ans, fp,indent = 4)

#     return(ans)

# def generate_sub(N,luck):
#     assert(isinstance(N,int))
#     assert(isinstance(luck,int))

#     # alist = ['head','glass','cup','flower','feather']
#     # blist=[['cr','cd'],'ar','edr','sh','sa']

#     basic_main_rate = 31.1#满爆率

#     prop_list = ['ar','edr','cr','cd','phr','sa','sh']
#     trans_ratio = [1.5,1.5,1,2,1.875,10,153.7]
#     ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

#     ans = dict()
            

#     ans['sub'] = []
#     total_sub = basic_main_rate*luck
#     precision = N
#     dist = np.linspace(0,1,precision)
#     for i in range(precision):
#         for j in range(precision-i):
#             tmp =dict()
#             tmp['cr'] = total_sub*dist[i]
#             tmp['cd'] = total_sub*ratio_main['cd']*dist[j]
#             tmp['ar'] = total_sub*ratio_main['ar']*dist[precision-i-j-1]
#             ans['sub'].append(tmp)

#     with open('./tmp/sub_run_list.json', 'w') as fp:
#         json.dump(ans, fp,indent = 4)

#     return(ans)
# def generate_articrafts(N,luck):
#     assert(isinstance(N,int))
#     assert(isinstance(luck,int))

#     alist = ['head','glass','cup','flower','feather']
#     blist=[['cr','cd'],'ar','edr','sh','sa']

#     basic_main_rate = 31.1#满爆率

#     prop_list = ['ar','edr','cr','cd','phr','sa','sh']
#     trans_ratio = [1.5,1.5,1,2,1.875,10,153.7]
#     ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

#     ans = dict()
#     for i in alist:
#         tmp = blist[alist.index(i)]
#         if isinstance(tmp,list):
#             ans[i] = []
#             for j in tmp:
#                 tmp = dict()
#                 tmp[j] = round(basic_main_rate*ratio_main[j],2)
#                 ans[i].append(tmp.copy())
#         else:
#             ans[i] = {tmp:round(basic_main_rate*ratio_main[tmp],2)}
            

#     ans['sub'] = []
#     luck = 3
#     total_sub = 31.1*luck
#     precision = N
#     dist = np.linspace(0,1,precision)
#     for i in range(precision):
#         for j in range(precision-i):
#             tmp =dict()
#             tmp['cr'] = total_sub*dist[i]
#             tmp['cd'] = total_sub*ratio_main['cd']*dist[j]
#             tmp['ar'] = total_sub*ratio_main['ar']*dist[precision-i-j-1]
#             ans['sub'].append(tmp)

#     with open('./tmp/articraft_run_list.json', 'w') as fp:
#         json.dump(ans, fp,indent = 4)

#     return(ans)

# def get_best_articraft(c,N=50,luck=3):
#     assert(isinstance(c,Character))
#     ww = generate_articrafts(N,luck)
#     diluc = deepcopy(c)
#     rls = Articraft()

#     save = 0
#     for head in ww['head']:
#         rls.add(head,'head')
#         glass = ww['glass']
#         cup = ww['cup']
#         flower = ww['flower']
#         feather = ww['feather']
#         rls.add(glass,'glass')        
#         rls.add(cup,'cup')
#         rls.add(flower,'flower')
#         rls.add(feather,'feather')
        
#         for sub in ww['sub']:
#             rls.add(sub,'sub')
#             diluc.put_on(rls)
#             tmp = diluc.damage_output({},"")
#             if tmp>save:
#                 save=tmp
#                 save4=rls.buf.copy()
#             diluc.take_off(rls)
#             rls.rm(sub,'sub')
#         rls.rm(feather,'feather')
#         rls.rm(flower,'flower')
#         rls.rm(cup,'cup')
#         rls.rm(glass,'glass')
#         rls.rm(head,'head')
        
#     with open('./data/articrfat.json', 'w') as fp:
#         json.dump(save4, fp,indent = 4)
    
def extract_name(a):
    assert(isinstance(a,dict))
    assert(len(a)==1)
    ans = list(a.keys())[0]
    return(ans)

def extract_name2(a):
    assert(isinstance(a,dict))
    assert(len(a)==1)
    ans = list(a.keys())[0]
    if list(a.keys())[0] == 'cr':
        ans = '暴击'
    if list(a.keys())[0] == 'cd':
        ans = '暴伤'
    if list(a.keys())[0] == 'dr':
        ans = '防御'
    if list(a.keys())[0] == 'ar':
        ans = '攻击'
    if list(a.keys())[0] == 'ed':
        ans = '属伤'
    if list(a.keys())[0] == 'dphys':
        ans = '物伤'
    if list(a.keys())[0] == 'hr':
        ans = '生命'
    if list(a.keys())[0] == 'ef':
        ans = '充能'
    return(ans)

def extract_name3(a):
    if a == 'phys':
        ans = '物理伤害'
    if a == 'elem':
        ans = '属性元素'
    if a == 'env':
        ans = '环境元素'
    if a == 'shield':
        ans = '技能护盾'
    if a == 'heal':
        ans = '技能治疗'
    if a == 'buff':
        ans = '增益'
    return(ans)   

# class pandasModel(QAbstractTableModel):
#     def __init__(self,data):
#         QAbstractTableModel.__init__(self)
#         self._data = data
#     def rowCount(self,parent=None):
#         return self._data.shape[0]
#     def columnCount(self,parent=None):
#         return self._data.shape[1]
#     def data(self,index,role=Qt.DisplayRole):
#         if index.isValid():
#             if role == Qt.DisplayRole:
#                 return (str(self._data.iloc[index.row(),index.column()]))
#     def headerData(self,col,orentation,role):
#         # if orentation == Qt.Horizontal and role == Qt.DisplayRole:
#             return self._data.columns[col]    
#         # return None        



def run_thru(path,c,rls,logger):
    with open(path, 'r', encoding='UTF-8') as fp:
        data = json.load(fp)
    save = dict()
    diluc = deepcopy(c)
    for head in data['head']:
        for glass in data['glass']:
                for cup in data['cup']:

                    flower = data['flower'][0]
                    feather = data['feather'][0]
            
                    rls.add(head,'head')
                    rls.add(glass,'glass')        
                    rls.add(cup,'cup')
                    rls.add(flower,'flower')
                    rls.add(feather,'feather')

                    diluc.put_on(rls)
                    logger.info("理之冠: {}".format(head))
                    logger.info("时之沙: {}".format(glass))
                    logger.info("空之杯: {}".format(cup))
                    logger.info("副词条: {}".format(rls.buf['sub']))

                    tmp = diluc.damage_rsl()['sum']
                    while (tmp in save.keys()):
                        tmp = tmp-1
                    save[tmp] = deepcopy(rls.buf)

                    diluc.take_off(rls)
                    rls.rm(feather,'feather')
                    rls.rm(flower,'flower')
                    rls.rm(cup,'cup')
                    rls.rm(glass,'glass')
                    rls.rm(head,'head')
    return(save)

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

# def process_string(s):
#     s = s.split("%")
#     ans = []
#     for i in s:
#         if len(i)>0:
#             ans.append(float(i))
#     return(ans)

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