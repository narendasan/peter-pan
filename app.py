import os
from os import listdir
from os.path import isfile, join

from flask import Flask, flash, request, redirect, render_template, session, abort, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.utils import secure_filename

from models import User


UPLOAD_FOLDER = 'files/uploaded'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
engine = create_engine('sqlite:///users.db', echo=True)


@app.route('/', methods=['GET'])
def index():
    if not session.get('logged_in'):
        return render_template('index.html')
    else:
        return redirect(url_for('files'))

@app.route('/login', methods=['GET'])
def login():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        redirect(url_for('index'))

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')
    


@app.route('/do_login', methods=['POST'])
def do_login():
    username = str(request.form['username'])
    password = str(request.form['password'])
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.username.in_([username]), User.password.in_([password]) )
    result = query.first()
    if result:
        session['logged_in'] = True
    else:
        flash('Unrecognized account! Please try again.')
    return redirect(url_for('index'))

@app.route("/do_logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/files', methods=['GET'])
def files():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        file_names = set([f for f in listdir(UPLOAD_FOLDER) if isfile(join(UPLOAD_FOLDER, f))])
        file_names -= set(['.no_content'])
        return render_template('files.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload_file',
                                filename=filename))

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=5001, debug=True)