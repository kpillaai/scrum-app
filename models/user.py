from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from models.task import Task, db
from enum import Enum

class RoleType(Enum):
    ADMIN = 'Admin'
    MEMBER = 'Member'
    
class User(db.Model, UserMixin):
    __tablename__ = 'a_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False) # unique id for each user
    name = db.Column(db.String, nullable=False)

    role = db.Column(db.Enum(RoleType), default=RoleType.MEMBER)  # from RoleType, either Admin or Member
    email = db.Column(db.String, unique=False, nullable=False)
    phone_number = db.Column(db.String, unique=False)
    password = db.Column(db.String, nullable=False)
    current_sprint =  db.Column(db.Integer, db.ForeignKey('sprint.id'), default=1) # ForeignKey = reference to another db table (id)
    # what tasks are assigned to the user
