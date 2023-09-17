# Modules
from flask import Flask, render_template, request, session, redirect, url_for
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
    # temporarily creating users in the database
    users = User.query.all()
    if (len(users) == 0):
        user1 = User(name="admin1", role=RoleType.ADMIN, email="admin1email@email.com", phone_number="01234567890", password="admin")
        db.session.add(user1)
        db.session.commit()

        user2 = User(name="admin2", role=RoleType.ADMIN, email="admin2email@email.com", phone_number="0123456789", password="admin2")
        db.session.add(user2)
        db.session.commit()

 
 # Adaptive Page functions
def refresh_task_list():
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('task_list.html', tasks=tasks, show_edit=True)

# Routes
@app.route('/')
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('index.html', tasks=tasks, show_edit=True)

@app.route('/task/add/', methods=['POST'])
def task_add():
    if request.method == 'POST':
        task = Task(description=request.form['task'])
        db.session.add(task) # Add Task to database
        db.session.commit() # Commit database changes
        return turbo.stream([
            turbo.update(render_template('task_add.html'), target='task_add'),
            turbo.update(render_template('task_panel_hide.html'), target="task_area"),
            turbo.update(refresh_task_list(), target='task_list')
        ])
        
    
@app.route('/task/remove/<int:id>', methods=['POST'])
def task_remove(id):
    if request.method == 'POST':
        task = Task.query.get_or_404(id) # Get task to be deleted by id
        db.session.delete(task) # Delete task from Task database
        db.session.commit() # Save database changes
        return turbo.stream([
            turbo.update(render_template('task_panel_hide.html'), target="task_area"),
            turbo.update(refresh_task_list(), target='task_list')
        ])
    
@app.route('/task/edit/view/<int:id>', methods=['POST'])
def task_edit_view(id):
    if request.method == 'POST':
        task = Task.query.get_or_404(id)
        return turbo.stream([
            turbo.update(render_template('task_panel_show.html'), target="task_area"),
            turbo.update(refresh_task_list(), target='task_list'),
            turbo.update(render_template('task_edit.html', task=task), target="task_panel"),
        ])

    
@app.route('/task/edit/<int:id>', methods=['POST'])
def task_edit(id):
    if request.method == 'POST':
        task = Task.query.get_or_404(id)
        task.description = request.form['task_description'] # Edit description
        db.session.commit() # Save database changes
        return turbo.stream([
            turbo.update(render_template('task_panel_hide.html'), target="task_area"),
            turbo.update(refresh_task_list(), target='task_list')
        ])
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    account = False
    if request.method == 'POST':
        username_input = request.form['username']
        password_input = request.form['password']
        # if user with email exists
        if db.session.query(db.session.query(User).filter_by(email=username_input).exists()).scalar():
            # user = db.one_or_404(db.select(User).filter_by(email=username_input))
            user = db.session.query(User).filter_by(email=username_input).one()

            # if correct password
            if user.password == password_input:
                account = True
                id = user.id
                username = user.email

            if account:
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = id
                session['username'] = username
                return redirect(url_for('index'))
            else:
                # if correct email but incorrect password
                error = "Invalid Login Credentials"
        else:
            # if incorrect email
            error = "Invalid Login Credentials"
    return render_template('login.html', error=error)

def logout():
    session['loggedin'] = False
    return render_template('login.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)
    
if __name__ == "__main__":
    app.run(debug=True)