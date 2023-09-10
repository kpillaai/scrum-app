from flask import Flask, render_template, request, session, redirect,  url_for
from User import User
from RoleType import RoleType

app = Flask(__name__)
app.secret_key = 'dl@31l2s31k24e1n'
users = {}
user1 = User("admin", RoleType.ADMIN, 'email@email.com', '0123456789', 'admin' )
user2 = User("admin2", RoleType.ADMIN, 'email@email.com', '0123456789', 'admin2' )
users[user1.id] = user1
users[user2.id] = user2

@app.route('/')
def index():
    if not 'tasks_db' in session:
        session['tasks_db'] = []
    if 'loggedin' in session:
        if session['loggedin'] == True:
            print('User Logged In: ' + session['username'])
    return render_template('index.html', tasks_db=session["tasks_db"])

@app.route('/post/', methods=['POST'])
def post():
    if request.method == 'POST':
        session['tasks_db'].append(request.form['task'])
        session.modified = True
        return redirect(url_for('backlog'))

@app.route('/remove/<int:index>')
def post_remove(index):
    session["tasks_db"].pop(index)
    session.modified = True
    return redirect(url_for('backlog'))

@app.route('/edit/<int:index>',methods=['GET','POST'])
def edit(index):
    tasks = session['tasks_db'][index]
    if request.method == 'POST':
        session['tasks_db'][index] = request.form['task']
        session.modified = True
        return redirect(url_for('backlog'))
    else:
        return render_template('edit.html',task=tasks, index=index)

@app.route('/backlog/')
def backlog():
    if not 'tasks_db' in session:
        session['tasks_db'] = []
    return render_template('backlog.html', tasks_db=session["tasks_db"])

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

if __name__ == "__main__":
    app.run(debug=True)