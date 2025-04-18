from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class TaskStatus(Enum):
    TODO = 'To Do'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False) # unique id for each task
    order = db.Column(db.Integer) # Used to track the order of displaying tasks
    name = db.Column(db.String)
    description = db.Column(db.String, default="")
    priority = db.Column(db.Integer, unique=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO) # from TaskStatus, either TODO, IN_PROGRESS or DONE
    status_prev = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO) # from TaskStatus, either TODO, IN_PROGRESS or DONE
    status_order = db.Column(db.Integer, default=0) # Used to track the order of displaying tasks
    estimated_effort = db.Column(db.Integer, default=1)
    start_date = db.Column(db.DateTime(timezone=True))
    end_date = db.Column(db.DateTime(timezone=True))
    assignee =  db.Column(db.Integer, db.ForeignKey('a_user.id')) # ForeignKey = reference to another db table (id)
    hours_taken = db.Column(db.Integer)
    in_sprint = db.Column(db.Boolean, default=False)
    status_date_modified = db.Column(db.String)
    
