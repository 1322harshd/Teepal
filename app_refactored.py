
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.before_request
def clear_session_once():
    if not hasattr(app, 'session_cleared'):
        session.clear()
        app.session_cleared = True

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']

        if username_or_email == 'admin' and password == 'admin123':
            session['logged_in'] = True
            session['is_admin'] = True
            session['username'] = 'admin'
            return redirect(url_for('admin_dashboard'))

        user = User.query.filter((User.Email == username_or_email) | (User.Name == username_or_email)).first()
        if user and check_password_hash(user.Password, password):
            session['logged_in'] = True
            session['username'] = user.Name
            session['user_id'] = user.UserId
            session['display_name'] = user.DisplayName
            session['user_image'] = user.Image
            return redirect(url_for('home'))
        else:
            error = 'Invalid credentials'

    return render_template('login.html', error=error)

@app.route('/logout_and_home')
def logout_and_home():
    session.clear()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        display_name = request.form['display_name']
        email = request.form['email']
        password = request.form['password']
        image = request.files['image']

        if User.query.filter((User.Email == email) | (User.Name == username)).first():
            error = 'User already exists'
        else:
            filename = None
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            hashed_password = generate_password_hash(password)
            new_user = User(
                Name=username,
                Email=email,
                Password=hashed_password,
                DisplayName=display_name,
                Image=filename
            )
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
