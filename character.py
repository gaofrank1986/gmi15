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
        
        '''人物自带初始5暴击，50暴伤,100充能'''
        self.attack[3] = 5
        self.attack[4] = 50
        self.attack[6] = 100

        self.atk_name = ('a','e','q','shld','heal','w')

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
        self.formula = {_:'' for _ in self.atk_name}
        self.formula['w'] ='w'
        self._data = None
        self.ed_pos=-1
        self.env = {}

        self.ifer = False
        self.if_def_r = False
        self.rct_tbl ={'fire':2,'watr':2,'ice':1.5}
        self.enemy = {"lvl":0,"erss":0,"frss":0}
        self.t1 = {'fire':'火','watr':'水','ice':'冰','elec':'雷','rock':'岩','wind':'风','grss':'草'}
        self.t2 = {'cr':'暴击','cd':'暴伤','hr':'生命%','ar':'攻击%','dr':'防御%','em':'精通','ef':'充能','dheal':'治疗','ed':'属伤','dphys':'物伤'}
        self.buffs={}
        self.jb_tb={'ks':"wind","cd":"ice","gz":"fire","gd":"watr"}
        
        
    def load_from_json(self,path,env,ratio):
        assert isinstance(ratio,dict)
        self.loaded = True
        self.env = env
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
        if True:
            logging.getLogger('Buff').info('{}(90级)'.format(data['name']))
            logging.getLogger('Buff').info('============')
            logging.getLogger('Buff').info('人物属性: {}'.format(self.t1[data['elem_class']]))
            logging.getLogger('Buff').info('基础生命: {}'.format(data1['basic_health']))
            logging.getLogger('Buff').info('基础防御: {}'.format(data1['basic_defense']))
            logging.getLogger('Buff').info('基础攻击: {}'.format(data1['basic_attack']))
            for i in data1['break_thru']:
                logging.getLogger('Buff').info('突破:\n   {} {}%'.format(self.t2[i],data1['break_thru'][i]))
            logging.getLogger('Buff').info('\n')

            self.enchant_ratio = data['c'+str(self.constellation)]['enchant_ratio']


        data['c'+str(self.constellation)]['round']['w'] = 1
        data['c'+str(self.constellation)]['round']['heal'] = 0
        data['c'+str(self.constellation)]['round']['shld'] = 0
        for i in self.atk_name:
            self.skill_round[i] = data['c'+str(self.constellation)]['round'][i]        

        for i in data['buffs']:
            if self._check2(i):
                assert not (i in self.buffs)
                self.buffs[i] = data['buffs'][i]
                if i in ratio:
                    self.buffs[i][2] = ratio[i]

        data['ratios']['w'] = [100]
        for i in data['ratios']:
            if len(data['ratios'][i]) == 1:
                data['ratios'][i] = data['ratios'][i]*15

        for i in data['c'+str(self.constellation)]['action_def']:
            self.formula[i] = data['c'+str(self.constellation)]['action_def'][i]
            
        if 'rebase' in data.keys():
            self.switch = data['rebase']
                
    def load_weapon_from_json(self,path,name,ratio,refine = 1):
        
        assert(self.loaded)
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        found = False
        
        for wp in data:
            if wp == name:
                found = True
                self._validate_wdata(data[wp])
                
                self.equipment.append((data[wp]['name'],refine))
                self.attack[0] += data[wp]['basic_attack']                                
                self.load_att(data[wp]['break_thru'])
                if True:
                    logging.getLogger('Buff').info('{}(90级) 精炼:{}'.format(data[wp]['name'],refine))
                    logging.getLogger('Buff').info('============')
                    logging.getLogger('Buff').info('基础攻击: {}'.format(data[wp]['basic_attack']))
                    for i in data[wp]['break_thru']:
                        logging.getLogger('Buff').info('突破:\n     {} {}%'.format(self.t2[i],data[wp]['break_thru'][i]))
                    logging.getLogger('Buff').info('\n')                

                for i in data[wp]['buffs']:
                    assert not (i in self.buffs)
                    self.buffs[i] = data[wp]['buffs'][i]
                    if i in ratio:
                        self.buffs[i][2] = ratio[i]
                    
                break
        assert(found)
        
    def load_weapon_list(self,path):
        
        assert(self.loaded)
        with open(path, 'r', encoding='UTF-8') as fp:
            data = json.load(fp)
        ans = []        
        for wp in data:                
            ans.append(data[wp]['name'])

        return(ans)













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
    
    
    def _load_buff(self,buffs,check,env):
        assert(isinstance(buffs,dict))
        logger =  logging.getLogger('Buff')
        for i in buffs:
            if check(i):

                cond = buffs[i][0]
                effect = buffs[i][1]
                if 'all' in cond:
                    cond=self.atk_name
                if 'atk' in cond:
                    cond=['a','e','q','w']
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
                    # print(j)
                    assert(j in self.atk_name or j in env)
                    if j in self.atk_name or env.get(j,False):
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
                                   
                            if j in env:
                                self.sp_buff[k] = self.sp_buff.get(k,0)+value*cover_ratio
                            else:         
                                if k in self.d_name or k in self.de_name or k in self.att_name or k in self.h_name or k in ['d','ratio','damage']:
                                    self.skill_effect[j][k] =self.skill_effect[j].get(k,0)+value*cover_ratio
                                if k == 'level':
                                    self.skill_level[self.atk_name.index(j)]+=value

                                    
                            


                            
    def _total_def(self):
        return(self.defense[0]*(1+self.defense[1]/100)+self.defense[2])
    def _total_atk(self):
        return(self.attack[0]*(1+self.attack[1]/100)+self.attack[2])
    def _total_health(self):
        return(self.health[0]*(1+self.health[1]/100)+self.health[2])
    def _crit(self):
        if self.attack[3]<100:
            return(1+self.attack[3]/100*self.attack[4]/100)
        else:
            return(1+self.attack[4]/100)
    
    # def _em_formula(self,x):
    #     return(1e-7*x**3-3e-4*x**2+0.472*x)
    # def _em2(self,x):
    #     return 20*x/(3*(x+1400))
    def _em3(self,x):
        return (6.665-9340/(x+1401))/2.4
    
    def _rr(self,r0,r,cnst=0.75):

        if (r0-r)<0:
            return 1-(r0-r)/2
        if (r0-r)>=0 and r0-r<0.75:
            return 1-(r0-r)
        if r0-r>=0.75:
            return 1/(1+4*((r0-r)))

    def _em_base(self,i):
        tmp = {'ks':721,'gd':2886,'gz':2406,'cd':601,'sb':1083}
        assert i in tmp
        return tmp[i]

    def _area3(self):
        return (1 + self.dmg_eh[self.ed_pos]/100+self.dmg_eh[7]/100+self.dmg_eh[8]/100,1 + self.dmg_eh[0]/100+self.dmg_eh[8]/100)
        
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------
    #----------------------------------------------------------------------------------




    def damage_rsl(self):
        if True:
            logger = logging.getLogger('Main')

            logger.info("攻击轮数: {}".format(self.skill_round))        
            logger.info("formula = {}".format(self.formula))

            logger.info("技能第一乘区切换 {}".format(self.switch))
            logger.info("技能等级 {}".format(self.skill_level))

        result = dict()
        atk_dmg = dict()
        for i in self.atk_name:
            logger.debug("==============处理 {} 技能公式:[{}]===============".format(i,self.formula[i]))
            ans = [0,0,0,0,0,0]
            ans2 = [0,0,0,0]
            atk_dmg[i] =0

            save_value= [_*self._total_atk()*self._crit() for _ in self._area3()]
            save_value.append(1000*(1+0.05*0.5))
            save = {}

            logger.debug("buff加载前 area1 = {:.2f},area2 = {:.2f}".format(self._total_atk(),self._crit()))
            logger.info("生命面板: {}".format(self.health))
            logger.info("防御面板: {}".format(self.defense))
            logger.info("攻击面板: {}".format(self.attack[:3]))
            logger.info("暴击: {:.2f}  爆伤: {:.2f}".format(self.attack[3],self.attack[4]))
            logger.info("属性伤害: {:.2f}  物理增伤: {:.2f}".format(self.dmg_eh[self.ed_pos]+self.dmg_eh[7],self.dmg_eh[0]))
            logger.info("元素精通: {:.2f}  元素充能: {:.2f}".format(self.attack[5],self.attack[6]))
            logger.info("增伤 {}".format(self.dmg_eh))

            logger.info("增益:  {}".format(self.skill_effect[i]))
            logger.info("特殊攻击提升:  {}".format(self.sp_buff))
                        
            self.load_att(self.skill_effect[i])
            self.load_att(self.sp_buff)
                        
            area1 = self._total_atk()
            area2 = self._crit()
            (area30,area31) = self._area3()

            if 'd2a' in self.sp_buff.keys():
                delta = self.sp_buff['d2a']/100*self._total_def()
                area1+= delta
                logger.debug("防御转攻击 增加量 = {:.2f}".format(delta))
            if 'h2a' in self.sp_buff.keys():
                delta = self.sp_buff['h2a']/100*self._total_health()
                area1+= delta
                logger.debug("生命转攻击 增加量 = {:.2f}".format(delta))
            if 'a2a' in self.sp_buff.keys():
                delta = self.sp_buff['a2a']/100*self._total_atk()
                area1+= delta
                logger.debug("攻击转攻击 增加量 = {:.2f}".format(delta))
            if 'ef2ed' in self.sp_buff.keys():
                delta = self.sp_buff['ef2ed']/100*self.attack[6]
                area30+=delta/100
                logger.debug("充能转增伤 增加量 = {:.2f}".format(delta)) 
                
            if True:
                                                     
                logger.debug("buff加载后 area1 = {:.2f},area2 = {:.2f}".format(area1,area2))
                logger.info("生命面板: {}".format(self.health))
                logger.info("防御面板: {}".format(self.defense))
                logger.info("攻击面板: {}".format(self.attack[:3]))
                logger.info("暴击: {:.2f}  爆伤: {:.2f}".format(self.attack[3],self.attack[4]))
                logger.info("属性伤害: {:.2f}  物理增伤: {:.2f}".format(self.dmg_eh[self.ed_pos]+self.dmg_eh[7],self.dmg_eh[0]))
                logger.info("元素精通: {:.2f}  元素充能: {:.2f}".format(self.attack[5],self.attack[6]))
                logger.info("增伤 {}".format(self.dmg_eh))

            
            if self.ifer:
                elemrct = self.rct_tbl.get(self.elem_class,1)*(1+self._em3(self.attack[5])+self.dmg_eh[13])
                elemrct2 = 1+2.4*self._em3(self.attack[5])+self.dmg_eh[13]
            else:
                elemrct = 1
                elemrct2 = 1
            logger.info('增幅反应系数{} 剧变反应系数{}'.format(elemrct,elemrct2))

            if self.if_def_r:
                ratio_dr = 190/((1-self.dmg_eh[14])*(self.enemy['lvl']+100)+190)
                ratio_rr0 = self._rr(self.enemy['erss']/100.0,self.dmg_eh[15]/100.0)  
                ratio_rr1 = self._rr(self.enemy['frss']/100.0,self.dmg_eh[16]/100.0)  
                ratio_rr2 = self._rr(self.enemy['frss']/100.0,0)
            else:
                ratio_dr = 1
                ratio_rr0 = 1  
                ratio_rr1 = 1  
                ratio_rr2 = 1               
            logger.info('防御系数{} 本属性抗性系数{} 物理抗性系数{} 其他属性抗性系数{}'.format(ratio_dr,ratio_rr0,ratio_rr1,ratio_rr2))          

            fm = parse_formula(self.formula[i])
            for entry in fm:
                if len(entry[0]) == 0:
                    continue                
                logger.debug("--------处理 {}-------".format(entry))
                if not(entry[0] in ['ks','w','cd','gz','gd']):

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
                    delta = 0
                    if i =='a' and ('ah' in entry[0]) and 'dah' in self.skill_effect[i]:
                        delta = self.skill_effect[i]['dah']/100
                        logger.debug('dah:{}'.format(delta))
                    if i =='a' and 'ah' not in entry[0] and 'ap' not in entry[0] and 'daa' in self.skill_effect[i]:
                        delta = self.skill_effect[i]['daa']/100
                        logger.debug('daa:{}'.format(delta))
                        
                    if i in ['a','e','q']:        
                        assert(atk_t in ['elem','phys','env'])
                        ans2[0]+=ratio*multi*base/self._total_atk()
                        ans2[1]+=ratio*multi
                        if atk_t == 'elem':                            
                            ans[0]+=base*area2*(area30+delta)*ratio*multi*elemrct*ratio_dr*ratio_rr0
                            # ans2[2]+=base*area2*(area30+delta)*ratio*multi/save_value[0]
                            # ans2[3]+=base*area2*(area30+delta)*ratio*multi/save_value[2]

                            logger.debug("基础攻击{:.2f},修正后总攻击 = {:.2f},暴击区 = {:.2f},加伤区 = {:.2f},伤害类型:{}".format(self.attack[0],base,area2,area30,atk_t))

                        elif atk_t == 'phys':
                            ans[0]+=base*area2*(area30+delta)*ratio*multi*self.enchant_ratio*elemrct*ratio_dr*ratio_rr0
                            # ans2[2]+=base*area2*(area30+delta)*ratio*multi*self.enchant_ratio/save_value[0]
                            # ans2[3]+=base*area2*(area30+delta)*ratio*multi*self.enchant_ratio/save_value[2]

                            logger.debug("基础攻击{:.2f},修正后总攻击 = {:.2f},暴击区 = {:.2f},加伤区 = {:.2f},伤害类型:{},附魔,占比 {}".format(self.attack[0],base,area2,area30,"属性元素",self.enchant_ratio))

    
                            ans[1]+=base*area2*(area31+delta)*ratio*multi*(1-self.enchant_ratio)*ratio_dr*ratio_rr1
                            # ans2[2]+=base*area2*(area30+delta)*ratio*multi*(1-self.enchant_ratio)/save_value[1]
                            # ans2[3]+=base*area2*(area30+delta)*ratio*multi*(1-self.enchant_ratio)/save_value[2]

                            logger.debug("基础攻击{:.2f},修正后总攻击 = {:.2f},暴击区 = {:.2f},加伤区 = {:.2f},伤害类型:{},不附魔,占比 {}".format(self.attack[0],base,area2,area31,"物理",1-self.enchant_ratio))
                        elif atk_t == 'env':
                            ans[2]+=base*area2*ratio*multi*ratio_dr*ratio_rr2
                            # ans2[2]+=base*area2*ratio*multi/save_value[0]
                            # ans2[3]+=base*area2*ratio*multi/save_value[2]

                            logger.debug("基础攻击{:.2f},修正后总攻击 = {:.2f},暴击区 = {:.2f},加伤区 = {:.2f},伤害类型:{}".format(self.attack[0],base,area2,1,"环境元素")) 
                        else:
                            pass
                    elif i in ['shld']:
                        assert(atk_t in ['shld','base'])
                        logger.debug("护盾强效{}%".format(self.dmg_eh[10]))
                        if atk_t == 'shld':
                            ans[4] += base*ratio*multi*(1+self.dmg_eh[10]/100)
                        if atk_t == 'base':
                            ans[4] += ratio*multi*(1+self.dmg_eh[10]/100)
                    elif i in ['heal']:
                        assert(atk_t in ['heal','base'])
                        logger.debug("治疗效果增加{}%".format(self.dmg_eh[9]))
                        if atk_t == 'heal':
                            ans[5] += base*ratio*multi*(1+self.dmg_eh[9]/100)
                        if atk_t == 'base':
                            ans[5] += ratio*100*multi*(1+self.dmg_eh[9]/100)
                    else:
                        raise ValueError       

                else:
                    if entry[0] in ['ks','cd','gz','gd'] and self.ifer:
                        multi  = float(entry[1])
                        em_base = self._em_base(entry[0])
                        if self.elem_class == self.jb_tb[entry[0]]:
                            ans[0] += em_base*multi*elemrct2*ratio_dr*ratio_rr0
                        else:
                            ans[2] += em_base*multi*elemrct2*ratio_dr*ratio_rr2
                            
                        logger.debug("剧变反应：{}  基数 {},次数 = {},精通 = {:.2f},精通增益:{:.2f}".format(entry[0],em_base,multi,self.attack[5],self._em3(self.attack[5])))
                    if entry[0] == 'w':
                        '''武器附伤'''
                        if 'damage' in self.skill_effect[i]:
                            ans[1]+=area1*self.skill_effect[i]['damage']/100*ratio_dr*ratio_rr1
                            logger.debug("武器附加伤害: 总攻击 = {:.2f},ratio = {:.2f} 假设为物理伤害，不受益2，3乘区加成".format(area1,self.skill_effect[i]['damage']/100)) 
        


            ##################################################
            result['maxhp'] = int(self._total_health())

            self.load_att(self.skill_effect[i],"minus")
            self.load_att(self.sp_buff,"minus")
            self.load_att(save,"minus")

            logger.debug("total damage for {} is 属性元素: {}, 物理: {},其他:{}".format(i,int(ans[0]),int(ans[1]),int(ans[2])))
            logger.debug("total shield for {} is {},total heal {}".format(i,int(ans[4]),int(ans[5])))
            ans = [int(_) for _ in ans]
            result['elem'] = result.get('elem',0)+ans[0]*self.skill_round[i]
            result['phys'] = result.get('phys',0)+ans[1]*self.skill_round[i]
            result['othr'] = result.get('othr',0)+(ans[2])*self.skill_round[i]
            result['shld'] = result.get('shld',0)+ans[4]
            result['heal'] = result.get('heal',0)+ans[5]
            atk_dmg[i] = (ans[0]+ans[1]+ans[2])*self.skill_round[i]
            # print(i,ans2[1],self.skill_round[i])
            # result['ratio1'] = result.get('ratio1',0)+ans2[1]*self.skill_round[i]
            result['ratio2'] = result.get('ratio2',0)+ans2[0]*self.skill_round[i]
            # result['ratio3'] = result.get('ratio3',0)+ans2[2]*self.skill_round[i]
            # result['ratio4'] = result.get('ratio4',0)+ans2[3]*self.skill_round[i]
            

        result['sum'] = int(result.get('elem',0)+result.get('phys',0)+ result.get('othr',0))
        result['perc_a'] = atk_dmg['a']/result['sum']
        result['perc_e'] = atk_dmg['e']/result['sum']
        result['perc_q'] = atk_dmg['q']/result['sum']
        logger.info("damage = {}".format(int(result['sum'])))
        logger.info("###############################################")        
        return(result)