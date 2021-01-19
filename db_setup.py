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
    cmts = Column(String,default='')
    img = Column(LargeBinary)
    def __init__(self):
        self.main0='cd'
    
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
    data['name'] = r.name
    return data