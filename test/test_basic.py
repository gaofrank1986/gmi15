import sys
import pytest
sys.path.append(".")

from basic import Basic_Panel


@pytest.fixture
def b0():
    return(Basic_Panel())

@pytest.fixture
def b1():
    b1  = Basic_Panel()
    b1.health =[1,2,3]
    b1.attack =[4,5,6,7,8,9,10]
    b1.defense =[11,12,13]
    b1.dmg_eh =[14,15,16,17,18,19,20,21,22]
    return(b1)


def test_default(b0):
    assert b0.health == [0,0,0]

def test_get_properties(b1):
    ans = b1.get_properties()
    assert ans['bh'] == 1
    assert ans['ar'] == 5
    assert ans['em'] == 9
    assert ans['dr'] == 12
    assert ans['dphys'] == 14
    assert ans['ed'] == 21
    
def test_put_on(b0,b1):
    b0.put_on(b1)
    ans = b0.get_properties()
    assert ans['bh'] == 1
    assert ans['ar'] == 5
    assert ans['em'] == 9
    assert ans['dr'] == 12
    assert ans['dphys'] == 14
    assert ans['ed'] == 21
    
def test_take_off(b0,b1):
    b0.take_off(b1)
    ans = b0.get_properties()
    assert ans['bh'] == -1
    assert ans['ar'] == -5
    assert ans['em'] == -9
    assert ans['dr'] == -12
    assert ans['dphys'] == -14
    assert ans['ed'] == -21