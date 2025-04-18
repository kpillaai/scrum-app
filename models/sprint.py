from flask_sqlalchemy import SQLAlchemy
from models.task import Task, TaskStatus, db

sprint_task = db.Table('sprint_task',
                db.Column('sprint_id', db.Integer, db.ForeignKey('sprint.id')),
                db.Column('task_id', db.Integer, db.ForeignKey('task.id'))
                )
  
class Sprint(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False) # unique id for each sprint
    name = db.Column(db.String)
    goal = db.Column(db.String, default="")
    number = db.Column(db.Integer, unique=False)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO) # from TaskStatus, either TODO, IN_PROGRESS or DONE
    start_date = db.Column(db.DateTime(timezone=True))
    end_date = db.Column(db.DateTime(timezone=True))
    burndown_tracking = db.Column(db.String) 
    tasks = db.relationship('Task', secondary=sprint_task, backref='sprint', lazy='joined')
    
    
