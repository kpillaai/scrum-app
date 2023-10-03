from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
from models.task import db

#db = SQLAlchemy()

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False) # unique id for each task
    name = db.Column(db.String)
    users = db.Column(db.Integer) # just one User per task or multiple?
    