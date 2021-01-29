from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///genshin.db"
db = SQLAlchemy(app)
migrate=Migrate(app,db) #Initializing migrate.
manager = Manager(app)
manager.add_command('db',MigrateCommand)
 

 
class Entry(db.Model):
    __tablename__='artifacts'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String)
    pos = db.Column(db.String(10))
    main0 = db.Column(db.String(10),default = 'cd')
    main1 = db.Column(db.Float,default=0.0)
    sub10 = db.Column(db.String(10))
    sub11 = db.Column(db.Float,default=0.0)
    sub20 = db.Column(db.String(10))
    sub21 = db.Column(db.Float,default=0.0)
    sub30 = db.Column(db.String(10))
    sub31 = db.Column(db.Float,default=0.0)
    sub40 = db.Column(db.String(10))
    sub41 = db.Column(db.Float,default=0.0)
    aset = db.Column(db.String(24))
    owner0 = db.Column(db.String,default='')
    owner1 = db.Column(db.String,default='')
    owner2 = db.Column(db.String,default='')
    owner3 = db.Column(db.String,default='')
    owner4 = db.Column(db.String,default='')
    cmts = db.Column(db.String,default='')
    img = db.Column(db.LargeBinary)
    def __init__(self):
        self.main0='cd'

class CRatio(db.Model):
    __tablename__='cover_ratio'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String,unique=True)
    keys = db.Column(db.String)
    values = db.Column(db.String)
 
if __name__ == "__main__":
     manager.run()