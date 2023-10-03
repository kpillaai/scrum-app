from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from models.task import Task, db
from enum import Enum

class RoleType(Enum):
    ADMIN = 'Admin'
    MEMBER = 'Member'
    
<<<<<<< HEAD
class User(db.Model):
    __tablename__ = 'a_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False) # unique id for each user
    name = db.Column(db.String)
=======
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) # unique id for each user
    name = db.Column(db.String, nullable=False)
>>>>>>> sprint2_merge
    role = db.Column(db.Enum(RoleType), default=RoleType.MEMBER)  # from RoleType, either Admin or Member
    email = db.Column(db.String, unique=True, nullable=False)
    phone_number = db.Column(db.String, unique=True)
<<<<<<< HEAD
    password = db.Column(db.String)
    #A_id = db.Column(db.Integer, db.ForeignKey('a.id'))
    # what tasks are assigned to the user
=======
    password = db.Column(db.String, nullable=False)
    # what tasks are assigned to the user
>>>>>>> sprint2_merge
