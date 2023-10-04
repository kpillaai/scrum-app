from flask_sqlalchemy import SQLAlchemy
from models.task import Task, TaskStatus, db

project_sprint = db.Table('project_sprint',
                db.Column('project_id', db.Integer, db.ForeignKey('project.id')),
                db.Column('sprint_id', db.Integer, db.ForeignKey('sprint.id'))
                )
  
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False) # unique id for each project
    name = db.Column(db.String)
    description = db.Column(db.String, default="")
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO) # from TaskStatus, either TODO, IN_PROGRESS or DONE
    start_date = db.Column(db.DateTime(timezone=True))
    due_date = db.Column(db.DateTime(timezone=True))
    sprints = db.relationship('Sprint', secondary=project_sprint, backref='projects')
    
    
