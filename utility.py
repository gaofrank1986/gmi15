import numpy as np
import json
import pickle
from copy import deepcopy
from basic import Articraft
from character import Character


def generate_relics2():

    alist = ['head','glass','cup','flower','feather']
    blist=[['ar','cr','cd','dr'],['ar','dr'],['ar','ed','fd'],['sh'],['sa']]

    basic_main_rate = 31.1#满爆率

    prop_list = ['ar','ed','cr','cd','fd','sa','sh','dr']
    trans_ratio = [1.5,1.5,1,2,1.875,10,153.7,1.875]
    ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

    ans = dict()
    for i in alist:
        ans[i] = []
        for j in blist[alist.index(i)]:
            tmp = dict()
            tmp[j] = round(basic_main_rate*ratio_main[j],2)
            ans[i].append(tmp.copy())

    with open('./tmp/run_list.json', 'w+') as fp:
        json.dump(ans, fp,indent = 4)

    return(ans)

def generate_sub(N,luck):
    assert(isinstance(N,int))
    assert(isinstance(luck,int))

    # alist = ['head','glass','cup','flower','feather']
    # blist=[['cr','cd'],'ar','edr','sh','sa']

    basic_main_rate = 31.1#满爆率

    prop_list = ['ar','edr','cr','cd','phr','sa','sh']
    trans_ratio = [1.5,1.5,1,2,1.875,10,153.7]
    ratio_main = {prop_list[i]:trans_ratio[i] for i in range(len(prop_list))}

    ans = dict()
            

    ans['sub'] = []
    total_sub = basic_main_rate*luck
    precision = N
    dist = np.linspace(0,1,precision)
    for i in range(precision):
        for j in range(precision-i):
            tmp =dict()
            tmp['cr'] = total_sub*dist[i]
            tmp['cd'] = total_sub*ratio_main['cd']*dist[j]
            tmp['ar'] = total_sub*ratio_main['ar']*dist[precision-i-j-1]
            ans['sub'].append(tmp)

    with open('./tmp/sub_run_list.json', 'w') as fp:
        json.dump(ans, fp,indent = 4)

    return(ans)
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
    # if list(a.keys())[0] == 'cr':
    #     ans = '暴击'
    # if list(a.keys())[0] == 'cd':
    #     ans = '暴伤'
    # if list(a.keys())[0] == 'dr':
    #     ans = '防御'
    # if list(a.keys())[0] == 'ar':
    #     ans = '攻击'
    # if list(a.keys())[0] == 'ed':
    #     ans = '属伤'
    return(ans)
    




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

                    tmp = diluc.damage_rsl()
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