# import numpy as np
import json
from copy import deepcopy
import logging
from basic import Basic_Panel
# import os

class Character(Basic_Panel):
    def __init__(self,skill_level,c_num,main_logger,c_level=90):
        assert(isinstance(main_logger,logging.Logger))
        super().__init__()
        self.name = ''

        assert(isinstance(skill_level,int) or isinstance(skill_level,list))
        if isinstance(skill_level,int):
            self.skill_level = [skill_level]*3
        else:
            self.skill_level = skill_level
            
        self.constellation = c_num
        self.level = c_level
        
        '''人物自带初始5暴击，50暴伤'''
        self.attack[3] = 5
        self.attack[4] = 50

        self.atk_name = ('a','e','q','w')

        self.main_logger = main_logger
        #-------------
        self.skill_round = {_:0 for _ in self.atk_name}

        self.skill_ratio = {_:[0,0] for _ in self.atk_name}
        
        self.enchant_ratio = 0 #物理附魔比例

        #------------------
        self.equipment=[]
        
        self.activated_buff = ["a","e","q","t1","t2"]

        self.skill_effect = {_:{} for _ in self.atk_name}

        self.loaded = False
        self.switch = dict()
        self.saved_buff = dict()
        self.damage = dict()
        self.formula = ''
        self.data = None
        self.wdata = None
        self.ed_pos=-1
        logging.getLogger('Buff').info("普通增益")
        logging.getLogger('Buff').info("*************************************")
        logging.getLogger('Buff').info("*************************************")

    def put_on(self,a):
        self.health = [self.health[i]+a.health[i] for i in range(len(self.health))]
        self.attack = [self.attack[i]+a.attack[i] for i in range(len(self.attack))]
        self.defense = [self.defense[i]+a.defense[i] for i in range(len(self.defense))]
        self.dmg_eh = [self.dmg_eh[i]+a.dmg_eh[i] for i in range(len(self.dmg_eh))]
        # if a.attack[5]>0:
        #     self.dmg_eh[self.ed_pos]+=a.attack[5]
        # if a.attack[6]>0:
        #     self.dmg_eh[0]+=a.attack[6]
            
    def take_off(self,a):
        self.health = [self.health[i]-a.health[i] for i in range(len(self.health))]
        self.attack = [self.attack[i]-a.attack[i] for i in range(len(self.attack))]
        self.defense = [self.defense[i]-a.defense[i] for i in range(len(self.defense))]
        self.dmg_eh = [self.dmg_eh[i]-a.dmg_eh[i] for i in range(len(self.dmg_eh))]
        # if a.attack[5]>0:
        #     self.dmg_eh[self.ed_pos]-=a.attack[5]
        # if a.attack[6]>0:
        #     self.dmg_eh[0]-=a.attack[6]


    def load_from_json(self,path):
        
        self.loaded = True

        for i in range(0,self.constellation+1):
            self.activated_buff.append("c"+str(i))
            
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            
        self._validate_data(data)
        
        self.data = data

        self.name = data['name']
        self.weapon_class = data['weapon_class']
        self.elem_class = data['elem_class']
        self.ed_pos = self.de_name.index('d'+self.elem_class)

        assert str(self.level) in data.keys()
        data1 = data[str(self.level)]
        self.health[0] = data1['basic_health']
        self.defense[0] = data1['basic_defense']
        self.attack[0] = data1['basic_attack']
        self.load_att(data1['break_thru'])
        
        self.enchant_ratio = data['enchant_ratio']

        data['round']['w'] = 1
        for i in self.atk_name:
            self.skill_round[i] = data['round'][i]        

        '''加载激活的buff'''
        self._load_buff(data['buffs'],self._check2)


        for i in data['ratios']:
            if len(data['ratios'][i]) == 1:
                data['ratios'][i] = data['ratios'][i]*15
        # print(data['ratios'])
        if "special" in data.keys():
            # logging.getLogger(data['special'])
            for i in data['special'].keys():
                if self._check2(i):
                    tmp = data['special'][i][0]
                    for j in tmp:
                        if j == 'd2a':
                            if isinstance(tmp[j],str):
                                # assert in ratio list
                                assert(tmp[j] in data['ratios'])
                                pos = self.atk_name.index(tmp[j][0])
                                level = self.skill_level[pos]
                                # print(level)
                                self.saved_buff['d2a'] = self.saved_buff.get('d2a',0)+data['ratios'][tmp[j]][level]
                                # pass
                            else:
                                self.saved_buff['d2a'] = self.saved_buff.get('d2a',0)+tmp[j]

        for i in data['formula'].keys():
            if self._check2(i):
                self.formula = data['formula'][i]
        self.formula.append('w')

        if 'rebase' in data.keys():
            self.switch = data['rebase']
                

    def _validate_data(self,data):
        pass
    def _validate_wdata(self,data):
        pass
    def _parse_formula(self,s):
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

    def _skill_cat(self,s):
        return(s[0]) 
    
    def _check1(self,i):
        return True
    def _check2(self,i):
        return i in self.activated_buff
    
    
    def _load_buff(self,buffs,check):
        assert(isinstance(buffs,dict))
        logger =  logging.getLogger('Buff')


        for i in buffs:
            if check(i):
                logger.info(i)
                logger.info("============")
                # logger.info("{}\n".format(buffs[i]))
                cond = buffs[i][0]
                effect = buffs[i][1]
                if 'all' in cond:
                    cond=['a','e','q']
                cover_ratio =buffs[i][2]
                
                logger.info("条件:{}".format(cond))
                logger.info("效果:{}".format(effect))
                pre = "覆盖系数"
                if 'level' in effect:
                    pre = '无'
                if 'damage' in  effect:
                    pre = '附伤次数'
                logger.info("{}:{}".format(pre,cover_ratio))
                if i in ['w1','w2']:
                    logger.info("武器精炼:{}".format(self.equipment[0][-1]))
                logger.info("{}".format(buffs[i][3]))

                logger.info("")

                for j in cond:
                    assert(j in self.atk_name)
                    for k in effect:
                        assert(isinstance(effect[k],int) or isinstance(effect[k],float) or isinstance(effect[k],list))
                        if isinstance(effect[k],list):
                            assert(len(effect[k]) == 2)
                            assert(len(self.equipment)>0)
                            refine = self.equipment[0][-1]
                            value = effect[k][0]+(refine-1)*effect[k][1]
                        else:
                            value = effect[k]
                            
                        if k in self.d_name or k in self.de_name or k in self.att_name or k in self.h_name or k in ['d']:
                            self.skill_effect[j][k] =self.skill_effect[j].get(k,0)+value*cover_ratio
                        if k == 'level':
                            self.skill_level[self.atk_name.index(j)]+=value
                        # if k == 'ratio':
                        #     self.skill_ratio[j][0]+=value
                        if k == 'damage':
                            self.damage[j] = self.damage.get(j,0)+value*cover_ratio
                            
    def _total_def(self):
        return(self.defense[0]*(1+self.defense[1]/100)+self.defense[2])
    def _total_atk(self):
        return(self.attack[0]*(1+self.attack[1]/100)+self.attack[2])
    def _total_health(self):
        return(self.health[0]*(1+self.health[1]/100)+self.health[2])
    def _crit(self):
        return(1+self.attack[3]/100*self.attack[4]/100)
    
    def _em_formula(self,x):
        return(1e-7*x**3-3e-4*x**2+0.472*x)
    
    def _em_formula(self,x):
        return(1e-7*x**3-3e-4*x**2+0.472*x)
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------

    def load_weapon_from_json(self,path,name,refine = 1):
        
        assert(self.loaded)
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self.wdata = data
        found = False
        
        for wp in data:
            if wp == name:
                found = True
                self._validate_wdata(data[wp])
                
                self.equipment.append((data[wp]['name'],refine))
                self.attack[0] += data[wp]['basic_attack']
                
                self.load_att(data[wp]['break_thru'])
                
                # tmp = dict()
                # for k,v in data[wp]['effect'].items():
                #     tmp[k] = v[0]+v[1]*(refine-1)
                    
                # self.load_att(tmp)
                
                '''加载激活的buff'''
                self._load_buff(data[wp]['buffs'],self._check1)
                break
        assert(found)
        
    def load_weapon_list(self,path):
        
        assert(self.loaded)
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            self.wdata = data
        ans = []        
        for wp in data:                
            ans.append(data[wp]['name'])

        return(ans)
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------





    def damage_rsl(self):
        self.main_logger.info("生命面板: {}".format(self.health))
        self.main_logger.info("防御面板: {}".format(self.defense))
        self.main_logger.info("攻击面板: {}".format(self.attack[:3]))
        self.main_logger.info("暴击: {:.2f}  爆伤: {:.2f}".format(self.attack[3],self.attack[4]))
        self.main_logger.info("属性伤害: {:.2f}  物理增伤: {:.2f}".format(self.dmg_eh[self.ed_pos]+self.dmg_eh[7],self.dmg_eh[0]))
        self.main_logger.info("元素精通: {:.2f}  元素充能: {:.2f}".format(self.attack[5],self.attack[6]))
        self.main_logger.info("攻击轮数: {}".format(self.skill_round))        
        self.main_logger.info("formula = {}".format(self.formula))
        self.main_logger.info("Buff:  {}".format(self.skill_effect))
        self.main_logger.info("特殊攻击提升:  {}".format(self.saved_buff))
        self.main_logger.info("附伤:  {}".format(self.damage))
        self.main_logger.info("技能第一乘区切换 {}".format(self.switch))
        self.main_logger.info("技能等级 {}".format(self.skill_level))
        self.main_logger.info("增伤 {}".format(self.dmg_eh))

        total = 0
        for i in self.atk_name:
            self.main_logger.debug("==============处理 {} 技能公式:[{}]===============".format(i,self.formula[self.atk_name.index(i)]))
            ans = [0,0,0,0]
            self.main_logger.debug("buff加载前 area1 = {:.2f},area2 = {:.2f}".format(self._total_atk(),self._crit()))

            self.load_att(self.skill_effect[i])
            area1 = self.attack[0]*(1+self.attack[1]/100)+self.attack[2]
            area2 = 1 + self.attack[3]/100*self.attack[4]/100
            if len(self.saved_buff) != 0:
                if 'd2a' in self.saved_buff.keys():
                    delta = self.saved_buff['d2a']/100*self._total_def()
                    area1+= delta
                    self.main_logger.debug("防御转攻击 增加量 = {:.2f}".format(delta))
                if 'h2a' in self.saved_buff.keys():
                    delta = self.saved_buff['h2a']/100*self._total_health()
                    area1+= delta
                    self.main_logger.debug("生命转攻击 增加量 = {:.2f}".format(delta))                                         
            self.main_logger.debug("buff加载后 area1 = {:.2f},area2 = {:.2f}".format(area1,area2))
            
            if i != 'w':
                fm = self._parse_formula(self.formula[self.atk_name.index(i)])
                for entry in fm:
                    if len(entry[0]) == 0:
                        continue
                    if not(entry[0] in ['ks']):
                        self.main_logger.debug("--------处理 {}-------".format(entry))

                        cat = self._skill_cat(entry[0])
                        level = self.skill_level[self.atk_name.index(cat)] - 1# 对index进行调整
                        multi  = float(entry[1])
                        atk_t = self.data['atk_type'][entry[0]]
                        ratio=self.data['ratios'][entry[0]][level]/100
                        self.main_logger.debug("技能类别 [{}],技能等级 {},技能倍率 = {:.2f},发动次数 = {},攻击类型:{}".format(cat,level+1,ratio,multi,atk_t))                    
                        base = area1                
                        if entry[0] in self.switch.keys():
                            if self.switch[entry[0]] == 'def':
                                base = self._total_def()
                                self.main_logger.debug("切换基础乘区 攻击为防御 area1 = {:.2f}".format(base))
                            if self.switch[entry[0]] == 'life':
                                    base = self._total_health()
                                    self.main_logger.debug("切换基础乘区 攻击为生命 area1 = {:.2f}".format(base))
                                
                                
                        assert(atk_t in ['elem','phys','env'])
                        if atk_t == 'elem':
                            area3 = (1 + self.dmg_eh[self.ed_pos]/100+self.dmg_eh[7]/100+self.skill_effect[i].get('d',0)/100)
                            ans[0]+=base*area2*area3*ratio*multi
                            self.main_logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{}".format(base,area2,area3,atk_t))

                        elif atk_t == 'phys':
                            area3 = (1 + self.dmg_eh[self.ed_pos]/100+self.dmg_eh[7]/100+self.skill_effect[i].get('d',0)/100)
                            ans[0]+=base*area2*area3*ratio*multi*self.enchant_ratio
                            self.main_logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{},附魔,占比 {}".format(base,area2,area3,"elem",self.enchant_ratio))

                            area3 = (1 + self.dmg_eh[0]/100+self.skill_effect[i].get('d',0)/100)                    
                            ans[1]+=base*area2*area3*ratio*multi*(1-self.enchant_ratio)
                            self.main_logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{},不附魔,占比 {}".format(base,area2,area3,"phys",1-self.enchant_ratio))
                        else:
                            area3 = 1#(1 + self.attack[5]/100+self.skill_effect[i].get('d',0)/100)
                            ans[2]+=base*area2*area3*ratio*multi
                            self.main_logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{}".format(base,area2,area3,atk_t)) 
                    else:
                        self.main_logger.debug("--------处理 {}-------".format(entry))
                        if entry[0] == 'ks':
                            multi  = float(entry[1])
                            em_base = 721
                            ans[3] = em_base*multi*(1+self._em_formula(self.attack[5])/100)  
                            self.main_logger.debug("扩散反应  基数 {},次数 = {},精通 = {:.2f},精通增益:{:.2f}".format(em_base,multi,self.attack[5],self._em_formula(self.attack[5])/100))   
                '''处理技能附伤'''
                if i in self.damage.keys():
                    area3 = (1 + self.dmg_eh[self.ed_pos]/100+self.dmg_eh[7]/100+self.skill_effect[i].get('d',0)/100)                    
                    ans[0]+=area1*self.damage[i]/100*area2*area3
                    self.main_logger.debug("技能附加伤害: area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},ratio = {:.2f} 假设为元素伤害，受益2，3乘区加成".format(area1,area2,area3,self.damage[i]/100)) 
            if i == 'w':               
                '''武器附伤'''
                if 'w' in self.damage.keys():
                    ans[1]+=area1*self.damage[i]/100
                    self.main_logger.debug("武器附加伤害: area1 = {:.2f},ratio = {:.2f} 假设为物理伤害，不受益2，3乘区加成".format(area1,self.damage[i]/100))    
            ##################################################

            self.load_att(self.skill_effect[i],"minus")
            self.main_logger.debug("total damage for {} is 元素: {}, 物理: {},其他:{}".format(i,int(ans[0]),int(ans[1]),int(ans[2]+ans[3])))
            total += (ans[0]+ans[1]+ans[2]+ans[3])*self.skill_round[i]
            
      
 


        self.main_logger.info("damage = {}".format(int(total)))
        self.main_logger.info("###############################################")        
        return(int(total))