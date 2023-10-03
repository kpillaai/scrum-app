# Modules
from flask import Flask, render_template, request, session, redirect, url_for,jsonify
from models.task import Task, db # Import Task database
from models.user import User, RoleType 
from models.team import Team 
from sqlalchemy import func

# Server Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dl@31l2s31k24e1n'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agility.db" # Configure SQLite database file
db.init_app(app) # Initialize the app with the extension
with app.app_context():
    db.drop_all() #CURRENTLY ADDING 2 USERS EACH TIME, ENABLE THIS LINE TO CLEAR THEM
    db.create_all() # Create table schemas in the database if not exist
    # # temporarily creating users in the database
    user1 = User(name="admin1", role=RoleType.ADMIN, email="admin1email@email.com", phone_number="01234567890", password="admin")
    db.session.add(user1)
    db.session.commit()

    user2 = User(name="admin2", role=RoleType.ADMIN, email="admin2email@email.com", phone_number="0123456789", password="admin2")
    db.session.add(user2)
    db.session.commit()

# Legacy variables (should convert to database)
# users = {}
# user1 = User("admin", RoleType.ADMIN, 'email@email.com', '0123456789', 'admin' )
# user2 = User("admin2", RoleType.ADMIN, 'email@email.com', '0123456789', 'admin2' )
# users[user1.id] = user1
# users[user2.id] = user2

# Routes
@app.route('/')
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('index.html', tasks=tasks, show_edit=False)

@app.route('/task/add/', methods=['POST'])
def post():
    if request.method == 'POST':
        task = Task(description=request.form['task'])
        db.session.add(task) # Add Task to database
        db.session.commit() # Commit database changes
        return redirect(url_for('backlog'))

@app.route('/task/remove/<int:id>')
def post_remove(id):
    task = Task.query.get_or_404(id) # Get task to be deleted by id
    db.session.delete(task) # Delete task from Task database
    db.session.commit() # Save database changes
    return redirect(url_for('backlog'))

@app.route('/task/edit/<int:id>',methods=['GET','POST'])
def edit(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.description = request.form['task_description'] # Edit description
        db.session.commit() # Save database changes
        return redirect(url_for('backlog'))
    else:
        return render_template('task_edit.html',task=task)

@app.route('/task/backlog/')
def backlog():
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('backlog.html', tasks=tasks, show_edit=True)

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

@app.route('/task/sprint/')
def sprint():
    tasks = Task.query.all() # Get all Tasks in database (query)
    max_sprint_id = db.session.query(func.max(Task.sprint_id)).scalar()
    if max_sprint_id is None:
        max_sprint_id = 0
    return render_template('sprint.html', tasks=tasks,max_id=max_sprint_id)

@app.route('/teams/')
def teams():
    teams = Team.query.all() # Get all Tasks in database (query)
    users = User.query.all()
    return render_template('teams.html', teams=teams, users=users)

@app.route('/teams/move/', methods=['POST'])
def move_user():
    if request.method == 'POST':
        team = Team.query.filter_by(id=request.form['team_id']).first()
        user = User.query.filter_by(id=request.form['users'][0]).first()
        team.users = user
        db.session.merge(team) # Commit database changes
        db.session.commit() # Commit database changes
    return redirect(url_for('teams'))

@app.route('/teams/add/', methods=['POST'])
def add_team():
    if request.method == 'POST':
        team = Team(name=request.form['team'])
        db.session.add(team) #  Task to database
        
        db.session.commit() # Commit database changes
    return redirect(url_for('teams'))

@app.route('/api/tasks/<int:task_id>/sprint/<int:id>', methods=['PUT'])
def add_task(task_id, id):
    task = Task.query.get(task_id)
    task.sprint_id = id
    db.session.commit()
    return "Task added to sprint"
    
if __name__ == "__main__":
    app.run(debug=True)