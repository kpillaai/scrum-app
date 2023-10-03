# Modules
from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from turbo_flask import Turbo
from models.task import Task, db # Import Task database
from models.user import User, RoleType 


# Server Configuration
app = Flask(__name__)
turbo = Turbo(app) # Turbo flask
app.config['SECRET_KEY'] = 'dl@31l2s31k24e1n'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agility.db" # Configure SQLite database file
db.init_app(app) # Initialize the app with the extension
with app.app_context():
    # db.drop_all() #CURRENTLY ADDING 2 USERS EACH TIME, ENABLE THIS LINE TO CLEAR THEM
    db.create_all() # Create table schemas in the database if not exist


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

class UserForm(FlaskForm):
    password = StringField(validators=[InputRequired()], render_kw={"placeholder": "New Password"})

    submit = SubmitField("Change Password")

 
# Adaptive Page functions
def live_task_list_refresh(): # Push realtime task list changes to all connected clients
    turbo.push([
        page_task_list_refresh(tasks_show_edit=True), # Backlog page
        page_task_list_refresh(tasks_show_edit=False) # Index page
    ]) 
    
def page_task_list_refresh(tasks_show_edit=True):
    tasks = Task.query.all() # Get all Tasks in database (query)
    return turbo.replace(render_template('task_list.html', tasks=tasks, tasks_show_edit=tasks_show_edit), target=f'task_list_{tasks_show_edit}')

def page_task_add_clear():
    return turbo.replace(render_template('task_add.html'), target='task_add') # target = id of html element to replace with html from file

def page_task_panel_show():
    return turbo.replace(render_template('task_area.html', tasks_show_edit=True, show_task_panel=True), target="task_area")

def page_task_panel_hide():
    return turbo.replace(render_template('task_area.html', tasks_show_edit=True, show_task_panel=False), target="task_area")

def page_task_edit_show(task):
    return turbo.replace(render_template('task_edit.html', task=task), target="task_panel")


# Routes
@app.route('/')
@login_required
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('index.html', tasks=tasks, tasks_show_edit=False)

@app.route('/backlog', methods=['PUT'])
@login_required
def backlog():
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('backlog.html', tasks=tasks, tasks_show_edit=True)

@app.route('/task/add/', methods=['POST'])
def task_add():
    task = Task(description=request.form['task'])
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
    if request.method == 'POST':
        task.description = request.form['task_description'] # Edit description
        db.session.commit() # Save database changes
        return redirect(url_for('backlog'))
    else:
        return render_template('task_edit.html',task=task)

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
    task.description = request.form['task_description'] # Edit description
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

    


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)


if __name__ == "__main__":
    app.run(debug=True)