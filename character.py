import json
from copy import deepcopy
import logging
from basic import Basic_Panel
from utility import parse_formula

class Character(Basic_Panel):
    def __init__(self,skill_level,c_num,c_level=90):
        # assert(isinstance(main_logger,logging.Logger))
        super().__init__()
        self.name = ''
        assert(isinstance(c_num,int))
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
        self.sp_buff = dict()
        self.formula = ''
        self._data = None
        # self.wdata = None
        self.ed_pos=-1
        logging.getLogger('Buff').info("普通增益")
        logging.getLogger('Buff').info("*************************************")
        logging.getLogger('Buff').info("*************************************")





    def load_from_json(self,path):
        
        self.loaded = True

        for i in range(0,self.constellation+1):
            self.activated_buff.append("c"+str(i))
            
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            
        self._validate_data(data)
        
        self._data = data

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


        assert('c'+str(self.constellation) in data['action_def'])
        # self.formula = data['formula']['c'+str(self.constellation)]
        # self.formula.append('w')
        # if 'action_def' in data:
        self.formula = data['action_def']['c'+str(self.constellation)]
        self.formula['w'] = 'w'

        if 'rebase' in data.keys():
            self.switch = data['rebase']
                

    def _validate_data(self,data):
        pass
    def _validate_wdata(self,data):
        pass
 

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

                cond = buffs[i][0]
                effect = buffs[i][1]
                if 'all' in cond:
                    cond=['a','e','q']
                cover_ratio =buffs[i][2]
                if True:
                    logger.info(i)
                    logger.info("============")
                    logger.info("条件:{}".format(cond))
                    logger.info("效果:{}".format(effect))
                    pre = "覆盖系数"
                    if 'level' in effect :
                        pre = '无'
                    if 'damage' in  effect:
                        pre = '附伤次数'
                    logger.info("{}:{}".format(pre,cover_ratio))
                    if i in ['w1','w2']:
                        logger.info("武器精炼:{}".format(self.equipment[0][-1]))
                    logger.info("{}".format(buffs[i][3]))
                    logger.info("")

                for j in cond:
                    assert(j in self.atk_name or j in ["shld","heal","spec"])
                    if j in self.atk_name or j in ["shld","heal","spec"]:
                        for k in effect:
                            assert(isinstance(effect[k],int) or isinstance(effect[k],float) or isinstance(effect[k],list) or isinstance(effect[k],str))
                            if isinstance(effect[k],list):
                                assert(len(effect[k]) == 2)
                                assert(len(self.equipment)>0)
                                refine = self.equipment[0][-1]
                                value = effect[k][0]+(refine-1)*effect[k][1]
                            else:
                                value = effect[k]
                                
                            if isinstance(value,str):
                                assert(value in self._data['ratios'])
                                pos = self.atk_name.index(value[0])
                                level = self.skill_level[pos]        
                                value = self._data['ratios'][value][level-1]    
                                                       
                            if k in self.d_name or k in self.de_name or k in self.att_name or k in self.h_name or k in ['d','ratio','damage']:
                                self.skill_effect[j][k] =self.skill_effect[j].get(k,0)+value*cover_ratio
                            if k == 'level':
                                self.skill_level[self.atk_name.index(j)]+=value
                            if k in ['h2a','d2a']:
                                # print(value,cover_ratio)
                                self.sp_buff[k] = self.sp_buff.get(k,0)+value*cover_ratio
                            


                            
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
    
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------

    def load_weapon_from_json(self,path,name,refine = 1):
        
        assert(self.loaded)
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            # self.wdata = data
        found = False
        
        for wp in data:
            if wp == name:
                found = True
                self._validate_wdata(data[wp])
                
                self.equipment.append((data[wp]['name'],refine))
                self.attack[0] += data[wp]['basic_attack']
                
                self.load_att(data[wp]['break_thru'])
                
                self._load_buff(data[wp]['buffs'],self._check1)
                break
        assert(found)
        
    def load_weapon_list(self,path):
        
        assert(self.loaded)
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
            # self.wdata = data
        ans = []        
        for wp in data:                
            ans.append(data[wp]['name'])

        return(ans)
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------





    def damage_rsl(self):
        if True:
            logger = logging.getLogger('Main')
            logger.info("生命面板: {}".format(self.health))
            logger.info("防御面板: {}".format(self.defense))
            logger.info("攻击面板: {}".format(self.attack[:3]))
            logger.info("暴击: {:.2f}  爆伤: {:.2f}".format(self.attack[3],self.attack[4]))
            logger.info("属性伤害: {:.2f}  物理增伤: {:.2f}".format(self.dmg_eh[self.ed_pos]+self.dmg_eh[7],self.dmg_eh[0]))
            logger.info("元素精通: {:.2f}  元素充能: {:.2f}".format(self.attack[5],self.attack[6]))
            logger.info("攻击轮数: {}".format(self.skill_round))        
            logger.info("formula = {}".format(self.formula))
            logger.info("增益:  {}".format(self.skill_effect))
            logger.info("特殊攻击提升:  {}".format(self.sp_buff))
            logger.info("技能第一乘区切换 {}".format(self.switch))
            logger.info("技能等级 {}".format(self.skill_level))
            logger.info("增伤 {}".format(self.dmg_eh))

        total = 0
        for i in self.atk_name:
            logger.debug("==============处理 {} 技能公式:[{}]===============".format(i,self.formula[i]))
            ans = [0,0,0,0]
            logger.debug("buff加载前 area1 = {:.2f},area2 = {:.2f}".format(self._total_atk(),self._crit()))

            self.load_att(self.skill_effect[i])
            area1 = self._total_atk()
            area2 = self._crit()
            if len(self.sp_buff) != 0:
                if 'd2a' in self.sp_buff.keys():
                    delta = self.sp_buff['d2a']/100*self._total_def()
                    area1+= delta
                    logger.debug("防御转攻击 增加量 = {:.2f}".format(delta))
                if 'h2a' in self.sp_buff.keys():
                    delta = self.sp_buff['h2a']/100*self._total_health()
                    area1+= delta
                    logger.debug("生命转攻击 增加量 = {:.2f}".format(delta))                                         
            logger.debug("buff加载后 area1 = {:.2f},area2 = {:.2f}".format(area1,area2))
            
            if i in ['a','e','q']:
                # if isinstance(self.formula,list):
                #     fm = parse_formula(self.formula[self.atk_name.index(i)])
                # if isinstance(self.formula,dict):
                fm = parse_formula(self.formula[i])
                for entry in fm:
                    if len(entry[0]) == 0:
                        continue
                    if not(entry[0] in ['ks']):
                        logger.debug("--------处理 {}-------".format(entry))

                        cat = self._skill_cat(entry[0])
                        level = self.skill_level[self.atk_name.index(cat)] - 1# 对index进行调整
                        multi  = float(entry[1])
                        atk_t = self._data['atk_type'][entry[0]]
                        ratio=self._data['ratios'][entry[0]][level]/100
                        if 'ratio' in self.skill_effect[i]:
                            ratio = ratio*(1+self.skill_effect[i]['ratio']/100)
                            logger.debug("祭礼剑系列 技能{} 倍率增加{}%,增加量为期望概率值".format(i,self.skill_effect[i]['ratio']))
                            
                        logger.debug("技能类别 [{}],技能等级 {},技能倍率 = {:.2f},发动次数 = {},攻击类型:{}".format(cat,level+1,ratio,multi,atk_t))                    
                        base = area1                
                        if entry[0] in self.switch.keys():
                            if self.switch[entry[0]] == 'def':
                                base = self._total_def()
                                logger.debug("切换基础乘区 攻击为防御 area1 = {:.2f}".format(base))
                            if self.switch[entry[0]] == 'life':
                                    base = self._total_health()
                                    logger.debug("切换基础乘区 攻击为生命 area1 = {:.2f}".format(base))
                                
                                
                        assert(atk_t in ['elem','phys','env'])
                        area3 = (1 + self.dmg_eh[self.ed_pos]/100+self.dmg_eh[7]/100+self.dmg_eh[8]/100)
                        dmg = base*area2*area3*ratio*multi
                        if atk_t == 'elem':                            
                            ans[0]+=dmg
                            logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{}".format(base,area2,area3,atk_t))

                        elif atk_t == 'phys':
                            ans[0]+=dmg*self.enchant_ratio
                            logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{},附魔,占比 {}".format(base,area2,area3,"属性元素",self.enchant_ratio))

                            area3 = (1 + self.dmg_eh[0]/100+self.dmg_eh[8]/100)                    
                            ans[1]+=base*area2*area3*ratio*multi*(1-self.enchant_ratio)
                            logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{},不附魔,占比 {}".format(base,area2,area3,"物理",1-self.enchant_ratio))
                        elif atk_t == 'env':
                            area3 = 1
                            ans[2]+=base*area2*area3*ratio*multi
                            logger.debug("area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},伤害类型:{}".format(base,area2,area3,"环境元素")) 
                        else:
                            pass
                    else:
                        logger.debug("--------处理 {}-------".format(entry))
                        if entry[0] == 'ks':
                            multi  = float(entry[1])
                            em_base = 721
                            ans[3] = em_base*multi*(1+self._em_formula(self.attack[5])/100)  
                            logger.debug("扩散反应  基数 {},次数 = {},精通 = {:.2f},精通增益:{:.2f}".format(em_base,multi,self.attack[5],self._em_formula(self.attack[5])/100))
        
                # '''处理技能附伤'''
                # if 'damage' in self.skill_effect[i]:
                #     area3 = (1 + self.dmg_eh[self.ed_pos]/100+self.dmg_eh[7]/100+self.dmg_eh[8]/100)                    
                #     ans[0]+=area1*self.skill_effect[i]['damage']/100*area2*area3
                #     logger.debug("技能附加伤害: area1 = {:.2f},area2 = {:.2f},area3 = {:.2f},ratio = {:.2f} 假设为元素伤害，受益2，3乘区加成".format(area1,area2,area3,self.skill_effect[i]['damage']/100)) 
            if i in ['shld','heal']:
                pass
            if i == 'w':               
                '''武器附伤'''
                if 'damage' in self.skill_effect[i]:
                    ans[1]+=area1*self.skill_effect[i]['damage']/100
                    logger.debug("武器附加伤害: area1 = {:.2f},ratio = {:.2f} 假设为物理伤害，不受益2，3乘区加成".format(area1,self.skill_effect[i]['damage']/100))    
            ##################################################

            self.load_att(self.skill_effect[i],"minus")
            logger.debug("total damage for {} is 属性元素: {}, 物理: {},其他:{}".format(i,int(ans[0]),int(ans[1]),int(ans[2]+ans[3])))
            total += (ans[0]+ans[1]+ans[2]+ans[3])*self.skill_round[i]
            
      
 


        logger.info("damage = {}".format(int(total)))
        logger.info("###############################################")        
        return(int(total))