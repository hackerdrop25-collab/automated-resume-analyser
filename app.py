from flask import Flask, request, render_template, redirect, url_for, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from gemini_ai import analyze_resume
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    analyses = db.relationship('AnalysisHistory', backref='author', lazy=True)

class AnalysisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_json = db.Column(db.Text, nullable=False) # Stores stringified list of analysis objects
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload_resume'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(email=email, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Email already exists.', 'danger')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload_resume'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('upload_resume'))
        else:
            flash('Login unsuccessful. Check email/password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == 'POST':
        num_resumes = int(request.form['num_resumes'])
        job_title = request.form['job_title']
        experience = request.form['experience']
        certifications = request.form['certifications']
        project_description = request.form['project_description']
        
        all_analyses = []
        
        for i in range(1, num_resumes + 1):
            file_key = f'resume_{i}'
            if file_key not in request.files:
                continue
            file = request.files[file_key]
            if file.filename == '':
                continue
                
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Perform analysis
                analysis = analyze_resume(filepath, job_title, experience, certifications, project_description)
                all_analyses.append(analysis)
        
        # Save to history
        new_history = AnalysisHistory(
            job_title=job_title,
            data_json=json.dumps(all_analyses),
            author=current_user
        )
        db.session.add(new_history)
        db.session.commit()
        
        return render_template('results.html', analyses=all_analyses)
            
    return render_template('upload.html')

@app.route('/history')
@login_required
def view_history():
    histories = AnalysisHistory.query.filter_by(user_id=current_user.id).order_by(AnalysisHistory.timestamp.desc()).all()
    # Parse data_json back to list for display
    for h in histories:
        h.parsed_data = json.loads(h.data_json)
    return render_template('dashboard.html', histories=histories)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
