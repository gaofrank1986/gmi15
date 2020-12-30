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
from utility import extract_name,run_thru

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
    weapon ="lm"
    refine = 5
    character = "diluc"
    

    
    c = Character(skill_level,constellation,logger)
    c.load_from_json("./data/character/"+character+".json")
    c.load_weapon_from_json("./data/weapon/"+c.weapon_class+".json",weapon,refine)


    rls = Articraft()
    rls.load_json("./data/sub.json")

    save = run_thru("./data/main_run_list.json",c,rls,logger)
                    
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
    
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)