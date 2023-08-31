from flask import Flask, render_template, request, session, redirect,  url_for

app = Flask(__name__)
app.secret_key = 'dl@31l2s31k24e1n'

@app.route('/')
def index():
    if not 'tasks_db' in session:
        session['tasks_db'] = []
    return render_template('index.html', tasks_db=session["tasks_db"])

@app.route('/post/', methods=['POST'])
def post():
    if request.method == 'POST':
        session['tasks_db'].append(request.form['task'])
        session.modified = True
        return redirect(url_for('index'))

@app.route('/remove/<int:index>')
def post_remove(index):
    session["tasks_db"].pop(index)
    session.modified = True
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)