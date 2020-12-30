import numpy as np
import json
import pickle
from copy import deepcopy
import logging
import os
from collections import OrderedDict
from basic import Articraft
from character import Character
import pandas as pd
from utility import extract_name

if __name__ == "__main__":


    
    os.remove("./tmp/main.log")
    logger = logging.getLogger('Main')
    logger.setLevel(level=logging.DEBUG)
    fh = logging.FileHandler('./tmp/main.log','w+')
    fmt = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s",datefmt='%m-%d,%H:%M')
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.propagate = False
    
    


    skill_level = 9
    constellation = 6
    weapon ="tkza"
    character = "noel"
    

    
    c = Character(skill_level,constellation,logger)
    c.load_from_json("./data/character/"+character+".json")
    c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,5)


    diluc = c
    rls = Articraft()
    rls.load_json("./data/sub.json")

    with open("./data/main_run_list.json", 'r', encoding='UTF-8') as fp:
        data = json.load(fp)


    save = dict()
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
                    
test = OrderedDict(sorted(save.items(),reverse=True))
N=0
limit = 4
tmp2 = dict()
for i in test:
    N+=1
    tmp = test[i]
    tmp2[N] = [i,extract_name(tmp['head']),extract_name(tmp['glass']),extract_name(tmp['cup'])]
    if N==4:
        break
table = pd.DataFrame(tmp2)
table.index =  ['damage','head','glass','cup']

print(c.name,c.equipment)
print(table)