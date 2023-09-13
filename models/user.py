from flask_sqlalchemy import SQLAlchemy
from models.task import Task, db
from enum import Enum

class RoleType(Enum):
    ADMIN = 'Admin'
    MEMBER = 'Member'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False) # unique id for each user
    name = db.Column(db.String)
    role = db.Column(db.Enum(RoleType), default=RoleType.MEMBER)  # from RoleType, either Admin or Member
    email = db.Column(db.String, unique=True)
    phone_number = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    # what tasks are assigned to the user
