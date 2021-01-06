import sys
import json
import pytest
sys.path.append(".")

from character import Character
from basic import Articraft



@pytest.fixture
def c0():
    return(Character(1,1))

@pytest.fixture
def c1():
    c1  = Character(1,1)
    c1.health =[1,2,3]
    c1.attack =[4,5,6,7,8,9,10]
    c1.defense =[11,12,13]
    c1.dmg_eh =[14,15,16,17,18,19,20,21,22]
    return(c1)

@pytest.fixture
def c2():
    c2  = Character(6,6)
    c2.load_from_json("./data/test/diluc.json")
    return(c2)

@pytest.fixture
def c3():
    c3  = Character(6,6)
    c3.load_from_json("./data/test/diluc.json")
    c3.load_weapon_from_json("./data/test/claymore.json","lm",1)
    return(c3)

@pytest.fixture
def r1():
    rls = Articraft()
    path = "./data/test/main_list.json"
    with open(path, 'r', encoding='UTF-8') as fp:
        data = json.load(fp)
    tmp = ['head','glass','cup','flower','feather']
    for i in tmp:
        rls.add(data[i][0],i)
    return(rls)
    
    
def test_default(c0):
    assert c0.health == [0,0,0]

def test_get_properties(c1):
    ans = c1.get_properties()
    assert ans['bh'] == 1
    assert ans['ar'] == 5
    assert ans['em'] == 9
    assert ans['dr'] == 12
    assert ans['dphys'] == 14
    assert ans['ed'] == 21
    
def test_put_on(c0,c1):
    c0.put_on(c1)
    ans = c0.get_properties()
    assert ans['bh'] == 1
    assert ans['ar'] == 5
    assert ans['em'] == 9
    assert ans['dr'] == 12
    assert ans['dphys'] == 14
    assert ans['ed'] == 21
    
def test_take_off(c0,c1):
    c0.take_off(c1)
    ans = c0.get_properties()
    assert ans['bh'] == -1
    assert ans['ar'] == -5
    assert ans['em'] == -9
    assert ans['dr'] == -12
    assert ans['dphys'] == -14
    assert ans['ed'] == -21
    
def test_load_from_json(c2):
    assert c2.name == '迪卢克'
    assert c2.formula == ["a2","e","q","w"]
    
def test_load_buff_1(c0):
    c0._load_buff({"c1": [["all"],{"d":15},0.5,"对生命值高于50％的敌人，迪卢克造成的伤害提高15％"]},c0._check1)
    assert c0.skill_effect['a']["d"] == 7.5
    c0._load_buff({"c1": [["all"],{"d":15},0.5,"对生命值高于50％的敌人，迪卢克造成的伤害提高15％"]},c0._check1)
    assert c0.skill_effect['a']["d"] == 15

def test_dmg(c3,r1):
    c3.put_on(r1)
    assert c3.damage_rsl() == 242190
