# Modules
from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from turbo_flask import Turbo
from models.task import Task, TaskStatus, db # Import Task database
from models.user import User, RoleType 
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
    # db.drop_all() #CURRENTLY ADDING 2 USERS EACH TIME, ENABLE THIS LINE TO CLEAR THEM
    db.create_all() # Create table schemas in the database if not exist
    # temporarily creating users in the database
    users = User.query.all()
    if (len(users) == 0):
        user1 = User(name="admin1", role=RoleType.ADMIN, email="admin1email@email.com", phone_number="01234567890", password="admin")
        db.session.add(user1)
        db.session.commit()

        user2 = User(name="admin2", role=RoleType.ADMIN, email="admin2email@email.com", phone_number="0123456789", password="admin2")
        db.session.add(user2)
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Adaptive Page functions
def live_task_list_refresh(): # Push realtime task list changes to all connected clients
    turbo.push([
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False) # Index page
    ]) 
    
def page_task_list_refresh(tasks_show_edit=True):
    tasks = Task.query.all() # Get all Tasks in database (query)
    return turbo.replace(render_template('task_list.html', tasks=tasks, tasks_show_edit=tasks_show_edit, TaskStatus=TaskStatus, users = User.query.all()), target=f'task_list_{tasks_show_edit}')

def page_task_add_clear():
    return turbo.replace(render_template('task_add.html'), target='task_add') # target = id of html element to replace with html from file

def page_task_panel_show():
    return turbo.replace(render_template('task_area.html', tasks_show_edit=True, show_task_panel=True), target="task_area")

def page_task_panel_hide():
    return turbo.replace(render_template('task_area.html', tasks_show_edit=True, show_task_panel=False), target="task_area")

def page_task_edit_show(task):
    return turbo.replace(render_template('task_edit.html', task=task, TaskStatus=TaskStatus, users = User.query.all()), target="task_panel")


# Routes
@app.route('/', methods=['GET'])
@login_required
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('index.html', tasks=tasks, tasks_show_edit=False, TaskStatus=TaskStatus, users = User.query.all())

@app.route('/backlog', methods=['POST'])
@login_required
def backlog():
    tasks = Task.query.all() # Get all Tasks in database (query)
    return turbo.stream(turbo.replace(render_template('backlog.html', tasks=tasks, tasks_show_edit=True, TaskStatus=TaskStatus, users = User.query.all()), target='page_content'))

@app.route('/task/add/', methods=['POST'])
def task_add():
    task = Task(name=request.form['task_name'])
    db.session.add(task) # Add Task to database
    db.session.commit() # Commit database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_task_add_clear(), # Clears add task input after adding a task 
        page_task_list_refresh() # Refresh task list so that newly added task will show up
    ])
        
@app.route('/task/remove/<int:id>', methods=['POST'])
def task_remove(id):
    task = Task.query.get_or_404(id) # Get task to be deleted by id
    db.session.delete(task) # Delete task from Task database
    db.session.commit() # Save database changes
    live_task_list_refresh() # Push realtime changes to all connected clients
    return turbo.stream([
        page_task_panel_hide(), # Hide the task panel
        page_task_list_refresh() # Refresh task list
    ])
    
@app.route('/task/edit/view/<int:id>', methods=['POST'])
def task_edit_view(id):
    task = Task.query.get_or_404(id)
    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_task_edit_show(task), # 3Show edit task on task panel
        page_task_list_refresh() # Refresh task list
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

    return turbo.stream([
        page_task_panel_show(), # Show task panel
        page_task_edit_show(task), # 3Show edit task on task panel
        page_task_list_refresh() # Refresh task list
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
        page_task_panel_hide(), # Hide task panel
        page_task_list_refresh() # Refresh task list
    ])

@app.route('/task/panel/hide/', methods=['POST'])
def task_panel_hide():
    return turbo.stream([
        page_task_panel_hide(), # Hide task panel
        page_task_list_refresh() # Refresh task list
    ])
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password == form.password.data:
                login_user(user)
                return redirect(url_for('index'))

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
    # session['loggedin'] = False
    # return render_template('login.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)


if __name__ == "__main__":
    app.run(debug=True)