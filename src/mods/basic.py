# from numpy import zeros
import json




class Basic_Panel():
    def __init__(self):
        self.health = [0]*3
        self.attack = [0]*7
        self.defense = [0]*3
        self.dmg_eh = [0]*19
        self.att_name = ['ba','ar','sa','cr','cd','em','ef']
        self.h_name = ['bh','hr','sh']
        self.d_name = ['bd','dr','sd']
        self.de_name = ['dphys','dfire','dwatr','dwind','delec','dice','drock','ed','d','dheal','dshld','daa','dah','delemrct','defreduce','derss','dfrss','addon_a','addon_a2']

    def load_att(self,info,t = "plus"):
        assert(isinstance(info,dict))
        assert(t in ["plus","minus"])
        if t == "plus":
            for i in info:
                if i in self.att_name:
                    self.attack[self.att_name.index(i)]+=info[i]
                elif i in self.h_name:
                    self.health[self.h_name.index(i)]+=info[i]
                elif i in self.d_name:
                    self.defense[self.d_name.index(i)]+=info[i]
                elif i in self.de_name:
                    self.dmg_eh[self.de_name.index(i)]+=info[i]
                else:
                    # print(i,"is not loaded to the character")
                    pass
        if t == "minus":
            for i in info:
                if i in self.att_name:
                    self.attack[self.att_name.index(i)]-=info[i]
                elif i in self.h_name:
                    self.health[self.h_name.index(i)]-=info[i]
                elif i in self.d_name:
                    self.defense[self.d_name.index(i)]-=info[i]
                elif i in self.de_name:
                    self.dmg_eh[self.de_name.index(i)]-=info[i]
                else:
                    pass
                    # print(i,"is not loaded to the character")

    def get_properties(self):
        tmp = dict()
        for i in range(len(self.h_name)):
            tmp[self.h_name[i]] = self.health[i]
        for i in range(len(self.att_name)):
            tmp[self.att_name[i]] = self.attack[i]
        for i in range(len(self.d_name)):
            tmp[self.d_name[i]] = self.defense[i]
        for i in range(len(self.de_name)):
            tmp[self.de_name[i]] = self.dmg_eh[i]
        return(tmp)

        
    def put_on(self,a):
        assert(issubclass(a.__class__,Basic_Panel))
        self.load_att(a.get_properties())

            
    def take_off(self,a):
        assert(issubclass(a.__class__,Basic_Panel))
        self.load_att(a.get_properties(),t = "minus")

class Articraft(Basic_Panel):
    def __init__(self,star_level=5):
        super().__init__()
        self.buf = dict()

    def add(self,item,pos):
        assert(pos not in self.buf.keys())
        self.load_att(item)
        self.buf[pos] = item
        #可以加重复报警

    def rm(self,item,pos):
        assert(pos in self.buf.keys())
        self.load_att(item,t="minus")
        self.buf.pop(pos)

    def rm2(self,pos):
        assert(pos in self.buf.keys())
        self.load_att(self.buf[pos],t="minus")
        self.buf.pop(pos)

    def load_json(self,path):
        with open(path, 'r') as fp:
            tmp = json.load(fp)
            for i in tmp:
                self.add(tmp[i],i)
        # self.attack = np.round(self.attack,2)
