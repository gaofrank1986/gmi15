from sqlalchemy import create_engine,Column,Integer,Sequence,String,Float,LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,scoped_session

Base = declarative_base()
engine = create_engine('sqlite:///./data/genshin.db', echo = True)
# Base.metadata.reflect(engine,reflect=True)
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

class Entry(Base):
    __tablename__='artifacts'
    id = Column(Integer,primary_key = True)
    name = Column(String)
    pos = Column(String(10))
    main0 = Column(String(10),default = 'cd')
    main1 = Column(Float,default=0.0)
    sub10 = Column(String(10))
    sub11 = Column(Float,default=0.0)
    sub20 = Column(String(10))
    sub21 = Column(Float,default=0.0)
    sub30 = Column(String(10))
    sub31 = Column(Float,default=0.0)
    sub40 = Column(String(10))
    sub41 = Column(Float,default=0.0)
    aset = Column(String(24))
    owner0 = Column(String,default='')
    owner1 = Column(String,default='')
    owner2 = Column(String,default='')
    owner3 = Column(String,default='')
    owner4 = Column(String,default='')
    cmts = Column(String,default='')
    img = Column(LargeBinary)
    def __init__(self):
        self.main0='cd'

class CRatio(Base):
    __tablename__='cover_ratio'
    id = Column(Integer,primary_key = True)
    name = Column(String,unique=True)
    keys = Column(String)
    values = Column(String)

class RWData(Base):
    __tablename__='rw_data'
    id = Column(Integer,primary_key = True)
    name = Column(String,unique=True)
    basic_health = Column(String)
    basic_attack = Column(String)
    basic_defense = Column(String)
    break_thru = Column(String)
    break_thru_v = Column(String)

class Buff_Def(Base):
    __tablename__='buff_definition'
    id = Column(Integer,primary_key = True)
    key = Column(String,unique=True)
    value = Column(String)
    cmts = Column(String)
# Base.metadata.create_all(engine)
def init_db():
    Base.metadata.create_all(bind=engine)

def get_info_by_id(i):
    r = db_session.query(Entry).filter(Entry.id==i).first()
    data={}
    data[r.main0] = r.main1
    data[r.sub10] = r.sub11
    data[r.sub20] = r.sub21
    data[r.sub30] = r.sub31
    data[r.sub40] = r.sub41
    data['set'] = r.aset
    data['name'] = r.name+'/'+str(i)
    return data