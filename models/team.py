from flask_sqlalchemy import SQLAlchemy
from enum import Enum
from datetime import datetime
from models.task import db
from models.user import User

#db = SQLAlchemy()
t_team_user = db.Table(
    'a_team_user', db.Model.metadata,
    db.Column('a_user_id', db.Integer, db.ForeignKey('a_user.id'),
            primary_key=True),
    db.Column('a_team_id', db.Integer, db.ForeignKey('a_team.id'),
            primary_key=True)
    )

class Team(db.Model):
    __tablename__ = 'a_team'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False) # unique id for each task
    name = db.Column(db.String)
    users = db.relationship(User, secondary=t_team_user, backref='team') # just one User per task or multiple?
    