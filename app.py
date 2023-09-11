# Modules
from flask import Flask, render_template, request, session, redirect, url_for
from models.task import Task, db # Import Task database
from models.user import User, RoleType 

# Server Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dl@31l2s31k24e1n'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agility.db" # Configure SQLite database file
db.init_app(app) # Initialize the app with the extension
with app.app_context():
    db.create_all() # Create table schemas in the database if not exist

# Legacy variables (should convert to database)
users = {}
user1 = User("admin", RoleType.ADMIN, 'email@email.com', '0123456789', 'admin' )
user2 = User("admin2", RoleType.ADMIN, 'email@email.com', '0123456789', 'admin2' )
users[user1.id] = user1
users[user2.id] = user2

# Routes
@app.route('/')
def index():
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    tasks = Task.query.all() # Get all Tasks in database (query)
    return render_template('index.html', tasks=tasks)

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
    return render_template('backlog.html', tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    account = False
    if request.method == 'POST':
        for user in users:
            if request.form['username'] == users[user].name and request.form['password'] == users[user].password:
                account = True
                id = users[user].id
                username = users[user].name
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = id
            session['username'] = username
            return render_template('index.html')
        else:
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