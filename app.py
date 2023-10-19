# Modules
from flask import Flask, render_template, request, session, redirect, url_for, make_response
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from turbo_flask import Turbo
from models.task import Task, TaskStatus, db # Import Task database
from models.user import User, RoleType 
from models.team import Team
from models.sprint import Sprint # Import Sprint database
from models.project import Project # Import Project database
import json

from datetime import datetime, date, timedelta

# Variables 
NO_CONTENT = 204 # Status Code

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

# Startup 
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
def sync_current_sprint():
    user = User.query.get_or_404(session['user_ref'])
    sprint_num = user.current_sprint
    users = User.query.all()
    for user in users:
        user.current_sprint = sprint_num # Sync all user's current_sprint to same number
    db.session.commit() # Save database changes
        
def page_task_list_refresh(tasks_show_edit=True):
    tasks = Task.query.filter_by(in_sprint=False).order_by(Task.order).all() # Get all Tasks (backlog) in database (query)
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    sprint.tasks = sorted(sprint.tasks, key=lambda task: task.order) # Sort sprint.tasks by task.order 
    return turbo.replace(render_template('task_list.html', tasks=tasks, tasks_show_edit=tasks_show_edit, TaskStatus=TaskStatus, sprint=sprint), target=f'task_list_{tasks_show_edit}')

def page_sprint_area_refresh():
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    sprint.tasks = sorted(sprint.tasks, key=lambda task: task.order) # Sort sprint.tasks by task.order
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.replace(render_template('sprint_area.html', sprint=sprint, TaskStatus=TaskStatus, sprint_count=sprint_count), target='sprint_area')

def page_task_panel_show():
    return turbo.replace('<div id="side_panel" class="col-3" style="height: 100%; overflow-y: scroll;"><div id="task_panel"></div></div>', target="side_panel")

def page_task_panel_hide():
    return turbo.replace('<div id="side_panel"></div>', target="side_panel")

def page_task_edit_show(task):
    return turbo.replace(render_template('task_edit.html', task=task, TaskStatus=TaskStatus, users=User.query.all()), target="task_panel")

def page_sprint_edit_show(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    return turbo.replace(render_template('sprint_edit.html', sprint=sprint, TaskStatus=TaskStatus), target="task_panel")

def page_team_refresh():
    return turbo.replace(render_template('teams.html', teams=Team.query.all(), users = User.query.all()), target="page_content")

def page_team_list_show():
    return turbo.replace(render_template('team_list.html', users=User.query.all(),teams=Team.query.all()), target="team_list")

def page_user_list_show():
    return turbo.replace(render_template('user_list.html', teams=Team.query.all(), users=User.query.all()), target="user_list")

def page_burndown_show(sprint_id, labels, values, optimal):
    sprint = Sprint.query.filter_by(id=sprint_id).first()
    print(sprint_id, values, labels)
    return turbo.replace(render_template('burndown.html', labels=labels, values=values, optimal=optimal), target="page_content")
    
    
# Routes
@app.route('/', methods=['GET'])
@login_required
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.filter_by(in_sprint=False).order_by(Task.order).all() # Get all Tasks (backlog) in database (query)
    return render_template('index.html', tasks=tasks, tasks_show_edit=False, TaskStatus=TaskStatus, users = User.query.all())

@app.route('/dashboard', methods=['POST'])
@login_required
def dashboard():
    tasks = Task.query.filter_by(in_sprint=False).order_by(Task.order).all() # Get all Tasks (backlog) in database (query)
    return turbo.stream(turbo.replace(render_template('dashboard.html', tasks=tasks, tasks_show_edit=False, TaskStatus=TaskStatus, users = User.query.all()), target='page_content'))

@app.route('/backlog', methods=['POST'])
@login_required
def backlog():
    tasks = Task.query.filter_by(in_sprint=False).order_by(Task.order).all() # Get all Tasks (backlog) in database (query)
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    # sprint = Sprint.query.filter_by(number=user.current_sprint).join(Sprint.tasks).order_by(Task.order).first() # Not working for some reason, so using workaround below instead:
    sprint.tasks = sorted(sprint.tasks, key=lambda task: task.order) # Sort sprint.tasks by task.order
    project1 = Project.query.get_or_404(1)
    sprint_count = len(project1.sprints)
    return turbo.stream(turbo.replace(render_template('backlog.html', tasks=tasks, tasks_show_edit=True, TaskStatus=TaskStatus, users = User.query.all(), sprint=sprint, sprint_count=sprint_count), target='page_content'))

@app.route('/task/add/', methods=['POST'])
def task_add():
    tasks = Task.query.filter_by(in_sprint=False).all() # Get all Tasks (backlog) in database (query)
    task = Task(name=request.form['task_name'])
    task.order = len(tasks) + 1
    db.session.add(task) # Add Task to database
    db.session.commit() # Commit database changes
    sync_current_sprint() # Sync all user's current_sprint to same number
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False), # Index page
    ]) 
    return ('', NO_CONTENT)

@app.route('/task/remove/<int:id>', methods=['POST'])
def task_remove(id):
    task = Task.query.get_or_404(id) # Get task to be deleted by id
    db.session.delete(task) # Delete task from Task database
    db.session.commit() # Save database changes
    sync_current_sprint() # Sync all user's current_sprint to same number
    turbo.push([ # Push realtime changes to all connected clients
        turbo.replace("<div class='alert alert-danger'>Task removed</div>",target=f'task_{task.id}'), # Remove task opened in edit view for all clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False), # Index page
    ])  
    return ('', NO_CONTENT)
    
@app.route('/task/edit/view/<int:id>', methods=['POST'])
def task_edit_view(id):
    task = Task.query.get_or_404(id)
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_task_edit_show(task), # Show edit task on task panel
    ])

@app.route('/task/edit/<int:id>', methods=['POST'])
def task_edit(id):
    task = Task.query.get_or_404(id)
    task.name = request.form['task_name'] # Edit name
    task.description = request.form['task_description'] # Edit description
    task.priority = request.form['task_priority'] # Edit priority
    
    # If a task is edited in a sprint, update sprint tracking for burndown
    sprints = Sprint.query.all()
    curr_sprint = None
    for sprint in sprints:
        if task in sprint.tasks:
            curr_sprint = sprint
    status_before = None
    status_after = None
    if task.status != request.form['task_status']:
        date_modified = datetime.today().strftime('%m-%d')
        if str(task.status) == str("TaskStatus.TODO"):
            status_before = 1
        elif str(task.status) == str("TaskStatus.IN_PROGRESS"):
            status_before = 0.5
        elif str(task.status) == str("TaskStatus.DONE"):
            status_before = 0
        
        if str(request.form['task_status']) == str("TODO"):
            status_after = 1
        elif str(request.form['task_status']) == str("IN_PROGRESS"):
            status_after = 0.5
        elif str(request.form['task_status']) == str("DONE"):
            status_after = 0          
        
        if curr_sprint is not None:
            if curr_sprint.burndown_tracking is not None:
                nested_array = json.loads(curr_sprint.burndown_tracking)
                nested_array.append([date_modified, status_before, status_after])
                curr_sprint.burndown_tracking = json.dumps(nested_array)
            else:
                curr_sprint.burndown_tracking = json.dumps([[date_modified, status_before, status_after]])
        
    
    task.status = request.form['task_status'] # Edit status
    task.estimated_effort = request.form['task_estimated_effort'] # Edit estimated effort
    task.assignee = request.form['task_assignee'] # Edit assignee
    if request.form['task_start_date'] != "": # Ignore empty value
        task.start_date = datetime.strptime(request.form['task_start_date'], '%Y-%m-%dT%H:%M') # Edit start date
    if request.form['task_due_date'] != "": # Ignore empty value
        task.due_date = datetime.strptime(request.form['task_due_date'], '%Y-%m-%dT%H:%M') # Edit due date
    task.hours_taken = request.form['task_hours_taken'] # Edit hours taken
    db.session.commit() # Save database changes
    # Overide user current sprint to task's sprint number in case it desyncs from other users' realtime changes
    if (len(task.sprint) >= 1):
        User.query.get_or_404(session['user_ref']).current_sprint = task.sprint[0].number
    sync_current_sprint() # Sync all user's current_sprint to same number
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False), # Index page
    ])
    return ('', NO_CONTENT)

@app.route('/task/<int:id>/status/<string:status>', methods=['POST'])
def task_status(id, status):
    task = Task.query.get_or_404(id)
    if (status == "checkbox"):
        if task.status != TaskStatus.DONE:
            task.status_prev = task.status
            status = "DONE"
        else:
            status = task.status_prev.name  
    task.status = TaskStatus[status] # Edit status
    db.session.commit() # Save database changes
    # Overide user current sprint to task's sprint number in case it desyncs from other users' realtime changes
    if (len(task.sprint) >= 1):
        User.query.get_or_404(session['user_ref']).current_sprint = task.sprint[0].number
    sync_current_sprint() # Sync all user's current_sprint to same number
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False), # Index page
    ])
    return ('', NO_CONTENT)

@app.route('/task/reorder/<string:task_type>', methods=['POST'])
def task_reorder(task_type):
    sort_order = request.form['sort_order'].split(',')
    tasks = Task.query.all() # Get all Tasks (backlog) in database (query)
    user = User.query.get_or_404(session['user_ref'])
    sprint = Sprint.query.filter_by(number=user.current_sprint).first()
    for i in range(len(sort_order)):
        for task in tasks:
            if int(task.id) == int(sort_order[i]):
                if (task_type == "backlog") and (task.in_sprint == True): # Remove from sprint if in sprint
                    sprint_task_remove(sprint.number, task.id, refresh=False)
                elif (task_type == "sprint") and (task.in_sprint == False): # Add to sprint if in backlog
                    sprint_task_add(sprint.number, task.id, refresh=False)
                task.order = i+1
                break
    db.session.commit() # Save changes to db
    # Overide user current sprint to task's sprint number in case it desyncs from other users' realtime changes
    if (len(task.sprint) >= 1):
        User.query.get_or_404(session['user_ref']).current_sprint = task.sprint[0].number
    sync_current_sprint() # Sync all user's current_sprint to same number
    time.sleep(0.05) # 50 ms delay to avoid flickers when moving tasks too quickly
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False), # Index page
    ])
    return ('', NO_CONTENT)

@app.route('/task/panel/hide/', methods=['POST'])
def task_panel_hide():
    return turbo.stream([
        page_task_panel_hide(), # Hide task panel
    ])

@app.route('/task/sprint/<int:sprint_number>/task/add/<int:task_id>', methods=['POST'])
def sprint_task_add(sprint_number, task_id, refresh=True):
    task = Task.query.get_or_404(task_id) 
    task.in_sprint = True
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.tasks.append(task) # Add task to sprint's tasks
    db.session.commit() # Commit database changes
    sync_current_sprint() # Sync all user's current_sprint to same number
    if refresh:
        turbo.push([ # Push realtime changes to all connected clients
            page_sprint_area_refresh(),
            page_task_list_refresh(tasks_show_edit=True), # Backlog page
            page_task_list_refresh(tasks_show_edit=False), # Index page
        ]) 
    return ('', NO_CONTENT)
    
@app.route('/task/sprint/<int:sprint_number>/task/remove/<int:task_id>', methods=['POST'])
def sprint_task_remove(sprint_number, task_id, refresh=True):
    task = Task.query.get_or_404(task_id) 
    task.in_sprint = False
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.tasks.remove(task) # Add task to sprint's tasks
    db.session.commit() # Commit database changes
    sync_current_sprint() # Sync all user's current_sprint to same number
    if refresh:
        turbo.push([ # Push realtime changes to all connected clients
            page_sprint_area_refresh(),
            page_task_list_refresh(tasks_show_edit=True), # Backlog page
            page_task_list_refresh(tasks_show_edit=False), # Index page
        ]) 
    return ('', NO_CONTENT)
    
@app.route('/sprint/edit/view/<int:sprint_number>', methods=['POST'])
def sprint_edit_view(sprint_number):
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(sprint_number),
    ])

@app.route('/sprint/edit/<int:sprint_number>', methods=['POST'])
def sprint_edit(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.name = request.form['sprint_name'] # Edit name
    sprint.goal = request.form['sprint_goal'] # Edit description
    sprint.status = request.form['sprint_status'] # Edit status
    if request.form['sprint_start_date'] != "": # Ignore empty value
        sprint.start_date = datetime.strptime(request.form['sprint_start_date'], '%Y-%m-%dT%H:%M') # Edit start date
    if request.form['sprint_due_date'] != "": # Ignore empty value
        sprint.due_date = datetime.strptime(request.form['sprint_due_date'], '%Y-%m-%dT%H:%M') # Edit due date
    if request.form['sprint_end_date'] != "": # Ignore empty value
        sprint.end_date = datetime.strptime(request.form['sprint_end_date'], '%Y-%m-%dT%H:%M') # Edit end date
    db.session.commit() # Save database changes
    User.query.get_or_404(session['user_ref']).current_sprint = sprint.number # Overide user current sprint to task's sprint number in case it desyncs from other users' realtime changes
    sync_current_sprint() # Sync all user's current_sprint to same number
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True) # Backlog page
    ]) 
    return ('', NO_CONTENT)

@app.route('/sprint/add/', methods=['POST'])
def sprint_add():
    sprint_num = len(Sprint.query.all()) + 1
    newSprint = Sprint(name=f"Sprint {sprint_num}", number=sprint_num)
    db.session.add(newSprint)
    project1 = Project.query.get_or_404(1)
    project1.sprints.append(newSprint)
    user = User.query.get_or_404(session['user_ref'])
    user.current_sprint = sprint_num
    db.session.commit()
    sync_current_sprint() # Sync all user's current_sprint to same number    
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint)
    ]) 
    return ('', NO_CONTENT)

@app.route('/sprint/remove/<int:sprint_number>', methods=['POST'])
def sprint_remove(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    for task in sprint.tasks: # Delete all tasks in the sprint
        db.session.delete(task) # Delete task from Task database
    db.session.delete(sprint) # Delete task from Task database
    project1 = Project.query.get_or_404(1)
    db.session.commit()
    for i in range(len(project1.sprints)):
        project1.sprints[i].number = i + 1
    user = User.query.get_or_404(session['user_ref'])
    user.current_sprint -= 1
    db.session.commit()
    sync_current_sprint() # Sync all user's current_sprint to same number    
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint)
    ]) 
    return ('', NO_CONTENT)

@app.route('/sprint/start/<int:sprint_number>', methods=['POST'])
def sprint_start(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.status = TaskStatus.IN_PROGRESS
    sprint.start_date = datetime.now().replace(second=0, microsecond=0) # Set start date to current datetime
    print(sprint.start_date)
    db.session.commit() # Save database changes
    sync_current_sprint() # Sync all user's current_sprint to same number    
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(sprint_number),
    ]) 
    return ('', NO_CONTENT)
        
@app.route('/sprint/stop/<int:sprint_number>', methods=['POST'])
def sprint_stop(sprint_number):
    sprint = Sprint.query.filter_by(number=sprint_number).first()
    sprint.status = TaskStatus.DONE
    sprint.end_date = datetime.now().replace(second=0, microsecond=0) # Set start date to current datetime
    print(sprint.due_date)
    db.session.commit() # Save database changes
    sync_current_sprint() # Sync all user's current_sprint to same number
    turbo.push([ # Push realtime changes to all connected clients
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(sprint_number)
    ]) 
    return ('', NO_CONTENT)
    
@app.route('/sprint/prev/', methods=['POST'])
def sprint_prev():
    user = User.query.get_or_404(session['user_ref'])
    if  (user.current_sprint > 1):
        user.current_sprint -= 1
        db.session.commit()
    return turbo.stream([
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
    ])  
    
@app.route('/sprint/next/', methods=['POST'])
def sprint_next():
    project1 = Project.query.get_or_404(1)
    user = User.query.get_or_404(session['user_ref'])
    if user.current_sprint < len(project1.sprints):
        user.current_sprint += 1
        db.session.commit()
    return turbo.stream([
        page_sprint_area_refresh(),
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_panel_show(), # Show task panel
        page_sprint_edit_show(user.current_sprint),
    ])  
    
         
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(name=form.name.data, phone_number=form.phone_number.data, email=form.email.data, password=form.password.data)
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

@app.route('/burndown/<int:sprint_id>', methods=['POST'])
def burndown(sprint_id):
    curr_sprint = Sprint.query.filter_by(number=sprint_id).first()
    start_date = curr_sprint.start_date
    end_date = curr_sprint.due_date
    delta = timedelta(days=1)
    curr_date = start_date
    labels = []
    if curr_date == None or end_date == None or start_date == None:
        return turbo.stream([page_burndown_show(sprint_id, ["No start or end dates"], [100], [100])])
    while curr_date <= end_date:
        labels.append(curr_date.strftime("%m") + "-" + curr_date.strftime("%d"))
        curr_date += delta
        
    step = 100 / (len(labels) - 1)
    optimal = [100 - i * step for i in range(len(labels))]
    actual = [100] * len(labels)
    

    if curr_sprint.burndown_tracking is None:
        return turbo.stream([page_burndown_show(sprint_id, labels, [100] * len(labels), optimal)])
    
    total_tasks = len(curr_sprint.tasks)
    task_history = json.loads(curr_sprint.burndown_tracking)
    actual_raw = [total_tasks] * len(labels)
    for tasks in task_history:
        edit_date = tasks[0]
        burndown_change = tasks[1] - tasks[2]
        index = labels.index(edit_date)
        for i in range(index, len(labels)):
            actual_raw[i] = actual_raw[i] - burndown_change
    
    for j in range(len(actual_raw)):
        actual[j] = actual_raw[j] * 100 / total_tasks
    
    return turbo.stream([page_burndown_show(sprint_id, labels, actual, optimal)])

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)

if __name__ == "__main__":
    app.run(debug=True)