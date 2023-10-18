# Modules
from flask import Flask, render_template, request, session, redirect, url_for, make_response
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, ValidationError
from turbo_flask import Turbo
from models.task import Task, TaskStatus, db # Import Task database
from models.user import User, RoleType 
from models.team import Team
from models.sprint import Sprint # Import Sprint database
from models.project import Project # Import Project database

from datetime import datetime


# Server Configuration
app = Flask(__name__)
turbo = Turbo(app) # Turbo flask
app.config['SECRET_KEY'] = 'dl@31l2s31k24e1n'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agility.db" # Configure SQLite database file
db.init_app(app) # Initialize the app with the extension
# Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
with app.app_context():
    #db.drop_all() #CURRENTLY ADDING 2 USERS EACH TIME, ENABLE THIS LINE TO CLEAR THEM
    db.create_all() # Create table schemas in the database if not exist
    # temporarily creating users in the database
    users = User.query.all()
    if (len(users) == 0):
        #user1 = User(name="admin1", role=RoleType.ADMIN, email="admin1email@email.com", phone_number="01234567890", password="admin")
        #db.session.add(user1)
        #db.session.commit()

        #user2 = User(name="admin2", role=RoleType.ADMIN, email="admin2email@email.com", phone_number="0123456789", password="admin2")
        #db.session.add(user2)
        #db.session.commit()
        
        # Temp Sprint1 
        sprint1 = Sprint(name="Sprint 1", number=1)
        db.session.add(sprint1)
        db.session.commit()
        
        # Temp Project1
        project1 = Project(name="Project 1")
        db.session.add(project1)
        project1.sprints.append(sprint1)
        db.session.commit()

# Register class
class RegisterForm(FlaskForm):
    name = StringField(validators=[InputRequired()], render_kw={"placeholder": "Name"})
    phone_number = StringField(render_kw={"placeholder": "Phone Number (Optional)"})
    email = StringField(validators=[InputRequired()], render_kw={"placeholder": "Email"})
    password = StringField(validators=[InputRequired()], render_kw={"placeholder": "Password"})
    admin = BooleanField()
    submit = SubmitField("Register")
    

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("That email is already registered")

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired()], render_kw={"placeholder": "Email"})
    password = StringField(validators=[InputRequired()], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

class TeamForm(FlaskForm):
    team_id = StringField(validators=[InputRequired()], render_kw={"placeholder": "team_id"})
    user_id = StringField(validators=[InputRequired()], render_kw={"placeholder": "user_id"})

class UserForm(FlaskForm):
    password = StringField(validators=[InputRequired()], render_kw={"placeholder": "New Password"})

    submit = SubmitField("Change Password")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Adaptive Page functions
def live_task_list_refresh(): # Push realtime task list changes to all connected clients
    turbo.push([
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False), # Index page
        page_sprint_task_list_refresh()
    ]) 
    
def page_task_list_refresh(tasks_show_edit=True):
    tasks = Task.query.filter_by(in_sprint=False).all() # Get all Tasks in database (query)
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.replace(render_template('task_list.html', tasks=tasks, tasks_show_edit=tasks_show_edit, TaskStatus=TaskStatus, users = User.query.all(), sprint=sprint, sprint_count=sprint_count), target=f'task_list_{tasks_show_edit}')


def page_sprint_task_list_refresh():
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.replace(render_template('sprint_area.html', sprint=sprint, TaskStatus=TaskStatus, sprint_count=sprint_count), target='sprint_area')

def page_task_panel_show():
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.replace(render_template('backlog.html', tasks_show_edit=True, show_task_panel=True, TaskStatus=TaskStatus, sprint=sprint, sprint_count=sprint_count), target="page_content")

def page_task_panel_hide():
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.replace(render_template('backlog.html', tasks_show_edit=True, show_task_panel=False, TaskStatus=TaskStatus, sprint=sprint, sprint_count=sprint_count), target="page_content")

def page_task_edit_show(task):
    return turbo.replace(render_template('task_edit.html', task=task, TaskStatus=TaskStatus, users=User.query.all()), target="task_panel")

def page_sprint_edit_show(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.replace(render_template('sprint_edit.html', sprint=sprint, TaskStatus=TaskStatus, sprint_count=sprint_count), target="task_panel")

def page_team_refresh():
    print(current_user.role)
    if current_user.role == RoleType.ADMIN:
        admin = True
    else:
        admin = False
    return turbo.replace(render_template('teams.html', teams=Team.query.all(), users = User.query.all(), admin=admin), target="page_content") 

def page_team_list_show():
    if current_user.role == RoleType.ADMIN:
        admin = True
    else:
        admin = False
    return turbo.replace(render_template('team_list.html', users=User.query.all(),teams=Team.query.all(), admin=admin), target="team_list")

def page_user_list_show():
    if current_user.role == RoleType.ADMIN:
        admin = True
    else:
        admin = False
    return turbo.replace(render_template('user_list.html', teams=Team.query.all(), users=User.query.all(), admin=admin), target="user_list")
# Routes
@app.route('/', methods=['GET'])
@login_required
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.filter_by(in_sprint=False).all() # Get all Tasks in database (query)
    return render_template('index.html', tasks=tasks, tasks_show_edit=False, TaskStatus=TaskStatus, users = User.query.all())

@app.route('/backlog', methods=['POST'])
@login_required
def backlog():
    tasks = Task.query.filter_by(in_sprint=False).all() # Get all Tasks in database (query)
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.stream(turbo.replace(render_template('backlog.html', tasks=tasks, tasks_show_edit=True, TaskStatus=TaskStatus, users = User.query.all(), sprint=sprint, sprint_count=sprint_count), target='page_content'))

@app.route('/task/add/', methods=['POST'])
def task_add():
    task = Task(name=request.form['task_name'])
    db.session.add(task) # Add Task to database
    db.session.commit() # Commit database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_task_list_refresh(), # Refresh task list so that newly added task will show up
        page_sprint_task_list_refresh()
    ])
        
@app.route('/task/remove/<int:id>', methods=['POST'])
def task_remove(id):
    task = Task.query.get_or_404(id) # Get task to be deleted by id
    db.session.delete(task) # Delete task from Task database
    db.session.commit() # Save database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    turbo.push(turbo.replace("<div class='alert alert-danger'>Task removed</div>",target=f'task_{task.id}')) # Remove task opened in edit view for all clients
    return turbo.stream([
        page_task_list_refresh(), # Refresh task list
        page_sprint_task_list_refresh()
    ])
    
@app.route('/task/edit/view/<int:id>', methods=['POST'])
def task_edit_view(id):
    task = Task.query.get_or_404(id)
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_task_edit_show(task), # 3Show edit task on task panel
        page_task_list_refresh(), # Refresh task list
        page_sprint_task_list_refresh()
    ])

@app.route('/task/edit/<int:id>', methods=['POST'])
def task_edit(id):
    task = Task.query.get_or_404(id)
    task.name = request.form['task_name'] # Edit name
    task.description = request.form['task_description'] # Edit description
    task.priority = request.form['task_priority'] # Edit priority
    task.status = request.form['task_status'] # Edit status
    task.estimated_effort = request.form['task_estimated_effort'] # Edit estimated effort
    if request.form['task_start_date'] != "": # Ignore empty value
        task.start_date = datetime.strptime(request.form['task_start_date'], '%Y-%m-%dT%H:%M') # Edit start date
    if request.form['task_due_date'] != "": # Ignore empty value
        task.due_date = datetime.strptime(request.form['task_due_date'], '%Y-%m-%dT%H:%M') # Edit due date
    task.assignee = request.form['task_assignee'] # Edit assignee
    task.hours_taken = request.form['task_hours_taken'] # Edit hours taken
    db.session.commit() # Save database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_task_list_refresh(), # Refresh task list
        page_sprint_task_list_refresh()
    ])

@app.route('/task/panel/hide/', methods=['POST'])
def task_panel_hide():
    return turbo.stream([
        page_task_panel_hide(), # Hide task panel
        page_task_list_refresh(), # Refresh task list
        page_sprint_task_list_refresh()
    ])

@app.route('/task/sprint/<int:sprint_number>/task/add/<int:task_id>', methods=['POST'])
def sprint_task_add(sprint_number, task_id):
    task = Task.query.get_or_404(task_id) 
    task.in_sprint = True
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.tasks.append(task) # Add task to sprint's tasks
    db.session.commit() # Commit database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_sprint_task_list_refresh(),
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])
    
@app.route('/task/sprint/<int:sprint_number>/task/remove/<int:task_id>', methods=['POST'])
def sprint_task_remove(sprint_number, task_id):
    task = Task.query.get_or_404(task_id) 
    task.in_sprint = False
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.tasks.remove(task) # Add task to sprint's tasks
    db.session.commit() # Commit database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_sprint_task_list_refresh(), #
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])
    
@app.route('/sprint/edit/view/<int:sprint_number>', methods=['POST'])
def sprint_edit_view(sprint_number):
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(sprint_number),
        page_task_list_refresh(), # Refresh task list
        page_sprint_task_list_refresh()
    ])

@app.route('/sprint/edit/<int:sprint_number>', methods=['POST'])
def sprint_edit(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.name = request.form['sprint_name'] # Edit name
    sprint.description = request.form['sprint_description'] # Edit description
    sprint.status = request.form['sprint_status'] # Edit status
    if request.form['sprint_start_date'] != "": # Ignore empty value
        sprint.start_date = datetime.strptime(request.form['sprint_start_date'], '%Y-%m-%dT%H:%M') # Edit start date
    if request.form['sprint_due_date'] != "": # Ignore empty value
        sprint.due_date = datetime.strptime(request.form['sprint_due_date'], '%Y-%m-%dT%H:%M') # Edit due date
    db.session.commit() # Save database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_task_list_refresh(), # Refresh task list
        page_sprint_task_list_refresh()
    ])

@app.route('/sprint/add/', methods=['POST'])
def sprint_add():
    sprint_num = len(Sprint.query.all()) + 1
    newSprint = Sprint(name=request.form['sprint_name'], number=sprint_num)
    db.session.add(newSprint)
    project1 = Project.query.get_or_404(1)
    project1.sprints.append(newSprint)
    user = User.query.get_or_404(session['user_ref'])
    user.current_sprint = sprint_num
    db.session.commit()
    turbo.push([ 
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
        page_sprint_task_list_refresh()
        ]) 
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
        page_sprint_task_list_refresh(),
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])

@app.route('/sprint/remove/<int:sprint_number>', methods=['POST'])
def sprint_remove(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    db.session.delete(sprint) # Delete task from Task database
    project1 = Project.query.get_or_404(1)
    db.session.commit()
    for i in range(len(project1.sprints)):
        project1.sprints[i].number = i + 1
    user = User.query.get_or_404(session['user_ref'])
    user.current_sprint -= 1
    db.session.commit()
    turbo.push([ 
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
        page_sprint_task_list_refresh()
        ]) 
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
        page_sprint_task_list_refresh(),
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])
    
@app.route('/sprint/prev/', methods=['POST'])
def sprint_prev():
    user = User.query.get_or_404(session['user_ref'])
    if  (user.current_sprint > 1):
        user.current_sprint -= 1
        db.session.commit()
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
        page_sprint_task_list_refresh(),
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])  
    
@app.route('/sprint/next/', methods=['POST'])
def sprint_next():
    project1 = Project.query.get_or_404(1)
    user = User.query.get_or_404(session['user_ref'])
    if user.current_sprint < len(project1.sprints):
        user.current_sprint += 1
        db.session.commit()
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
        page_sprint_task_list_refresh(),
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])  
    
         
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.admin.data:
            user_role = RoleType.ADMIN
        else:
            user_role = RoleType.MEMBER

        new_user = User(name=form.name.data, phone_number=form.phone_number.data, email=form.email.data, password=form.password.data, role=user_role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                session['user_ref'] = user.id
                return redirect(url_for('index'))
            else:
                return render_template('login.html', form=form, isWrongPassword=True)
        else:
            return render_template('login.html', form=form, userNotFound=True)
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    session['loggedin'] = False
    return redirect(url_for('login'))
    # session['loggedin'] = False
    # return render_template('login.html')

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UserForm()
    id = current_user.id
    if form.validate_on_submit():
        user_to_update = User.query.get_or_404(id)
        user_to_update.password = form.password.data
        db.session.commit()
        return redirect(url_for('account'))

    return render_template('account.html', form=form)

@app.route('/set')
@app.route('/set/<theme>')
def set_theme(theme="light"):
  res = make_response(redirect(url_for('account')))
  res.set_cookie("theme", theme)
  return res  

@app.route('/teams/delete/<int:id>', methods=['GET', 'POST'])
def teams_delete(id):
    team = Team.query.get_or_404(id) 
    db.session.delete(team) 
    db.session.commit()
    return turbo.stream([page_team_refresh(),page_team_list_show(),page_user_list_show()])

@app.route('/teams/move/<user_id>', methods=['POST'])
def move_user(user_id):
    if request.method == 'POST':
        form_name = 'teams_select_' + user_id
        team = Team.query.filter_by(name=request.form.get(form_name)).first()
        user = User.query.filter_by(id=user_id).first()
        if team is not None and user is not None:
            exists = False
            for team_user in team.users:
                if user == team_user:
                    exists = True
            if not exists:
                team.users.append(user)
        db.session.commit() # Commit database changes
    return turbo.stream([page_team_refresh(),page_team_list_show(),page_user_list_show()])

@app.route('/teams/remove/<int:team_id>/<int:user_id>', methods=['POST'])
def remove_user(team_id, user_id):
    if request.method == 'POST':
        team = Team.query.filter_by(id=team_id).first()
        user = User.query.filter_by(id=user_id).first()
        #user = User.query.filter_by(id=request.form['users'][0]).first()
        if team is not None and user is not None:
            exists = False
            for team_user in team.users:
                if user == team_user:
                    exists = True
            if exists:
                team.users.remove(user)
        db.session.commit() # Commit database changes
    return turbo.stream([page_team_refresh(),page_team_list_show(),page_user_list_show()])

@app.route('/teams', methods=['GET', 'POST'])
def teams():
    return turbo.stream([page_team_refresh(),page_team_list_show(),page_user_list_show()])

@app.route('/teams/add/', methods=['GET', 'POST'])
def teams_add():
    if request.method == 'POST':
        team = Team(name=request.form['team'], users=[])
        db.session.add(team) #  Team to database
        db.session.commit() # Commit database changes
    return turbo.stream([page_team_refresh(),page_team_list_show(),page_user_list_show()])

@app.route('/myteams', methods=['POST'])
@login_required
def myteams():
    id = current_user.id
    teams = Team.query.all()
    my_teams = []
    print(teams)
    for team in teams:
        for user in team.users:
            if user.id == id:
                print('true')
                my_teams.append(team)
    
    return turbo.stream([turbo.replace(render_template('myteams.html'), target="page_content"), \
        turbo.replace(render_template('team_list.html', users=User.query.all(),teams=my_teams), target="team_list")])


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)

if __name__ == "__main__":
    app.run(debug=True)