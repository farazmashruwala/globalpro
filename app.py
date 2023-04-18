from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
import random
import pandas as pd

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
            flash('You have been logged in!', 'success')
            #return "success"
            return redirect(url_for('admin_panel'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully')
            return redirect(url_for('uploaded'))
    return render_template('upload.html')

@app.route('/uploaded')
def uploaded():
    return render_template('uploaded.html')

@app.route('/admin/{}{}'.format('session_id=',random.randint(100,900)))
def admin_panel():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('admin.html', files=files)


@app.route('/download/<path:filename>')
def download_file(filename):
    uploads_dir = os.path.join(app.root_path, 'uploads')
    path = os.path.join(uploads_dir, filename)
    return send_file(path,mimetype='csv/xlxs', as_attachment=True)


@app.route('/open-file/<filename>')
def open_file(filename):
    if not allowed_file(filename):
        return "Invalid file type. Only CSV and XLSX files are allowed."

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
    except Exception as e:
        return f"Error reading file: {str(e)}"

    table_html = df.to_html(classes="table table-bordered table-striped", index=False)

    return render_template('table.html', table_html=table_html)





if __name__ == '__main__':
    app.run(port=8000,  debug=True)
