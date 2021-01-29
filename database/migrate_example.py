from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)
migrate=Migrate(app,db) #Initializing migrate.
manager = Manager(app)
manager.add_command('db',MigrateCommand)
 
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    # email = db.Column(db.String, unique=True, nullable=False)
    age= db.Column(db.Integer, unique=False, nullable=True)
    
class Company(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String, unique=True, nullable=False)
    clocation = db.Column(db.String, unique=False, nullable=False)
 
if __name__ == "__main__":
     manager.run()