# Modules
from flask import Flask, render_template, request, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from models.task import Task, db # Import Task database
from models.user import User, RoleType 

# Server Configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dl@31l2s31k24e1n'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agility.db" # Configure SQLite database file
db.init_app(app) # Initialize the app with the extension
with app.app_context():
    # db.drop_all() #CURRENTLY ADDING 2 USERS EACH TIME, ENABLE THIS LINE TO CLEAR THEM
    db.create_all() # Create table schemas in the database if not exist
    # # temporarily creating users in the database
    # user1 = User(name="admin1", role=RoleType.ADMIN, email="admin1email@email.com", phone_number="01234567890", password="admin")
    # db.session.add(user1)
    # db.session.commit()

    # user2 = User(name="admin2", role=RoleType.ADMIN, email="admin2email@email.com", phone_number="0123456789", password="admin2")
    # db.session.add(user2)
    # db.session.commit()

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

    return render_template('login.html', form=form)

def logout():
    session['loggedin'] = False
    return render_template('login.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', error=error)
    
if __name__ == "__main__":
    app.run(debug=True)