from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication - email/password only"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True, primary_key=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    job_descriptions = db.relationship('JobDescription', backref='user', lazy=True, cascade='all, delete-orphan')
    analysis_results = db.relationship('AnalysisResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Resume(db.Model):
    """Resume model for storing uploaded resume metadata"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    extracted_text = db.Column(db.Text, nullable=True)  # Cached text extraction
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis_results = db.relationship('AnalysisResult', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Resume {self.original_filename}>'


class JobDescription(db.Model):
    """JobDescription model for storing job requirements"""
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    required_experience = db.Column(db.String(255), nullable=True)
    required_certifications = db.Column(db.Text, nullable=True)  # JSON format
    required_skills = db.Column(db.Text, nullable=True)  # JSON format
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis_results = db.relationship('AnalysisResult', backref='job_description', lazy=True, cascade='all, delete-orphan')
    
    def get_certifications(self):
        """Parse certifications JSON"""
        return json.loads(self.required_certifications) if self.required_certifications else []
    
    def get_skills(self):
        """Parse skills JSON"""
        return json.loads(self.required_skills) if self.required_skills else []
    
    def __repr__(self):
        return f'<JobDescription {self.job_title}>'


class AnalysisResult(db.Model):
    """AnalysisResult model for storing resume analysis results"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False, index=True)
    job_description_id = db.Column(db.Integer, db.ForeignKey('job_descriptions.id'), nullable=True, index=True)
    
    # Analysis Scores
    technical_score = db.Column(db.Float, nullable=True)  # 0-100
    experience_score = db.Column(db.Float, nullable=True)  # 0-100
    formatting_score = db.Column(db.Float, nullable=True)  # 0-100
    overall_score = db.Column(db.Float, nullable=True)  # 0-100
    
    # Analysis Details
    summary = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)  # JSON array
    weaknesses = db.Column(db.Text, nullable=True)  # JSON array
    recommendations = db.Column(db.Text, nullable=True)  # JSON array
    matched_skills = db.Column(db.Text, nullable=True)  # JSON array
    missing_skills = db.Column(db.Text, nullable=True)  # JSON array
    
    # New Fields for Project Differentiation
    relevant_projects = db.Column(db.Text, nullable=True)  # JSON array
    filtered_project_count = db.Column(db.Integer, default=0)
    total_project_count = db.Column(db.Integer, default=0)
    
    # Metadata
    analyzed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_strengths(self):
        """Parse strengths JSON"""
        return json.loads(self.strengths) if self.strengths else []
    
    def get_weaknesses(self):
        """Parse weaknesses JSON"""
        return json.loads(self.weaknesses) if self.weaknesses else []
    
    def get_recommendations(self):
        """Parse recommendations JSON"""
        return json.loads(self.recommendations) if self.recommendations else []
    
    def get_matched_skills(self):
        """Parse matched skills JSON"""
        return json.loads(self.matched_skills) if self.matched_skills else []
    
    def get_missing_skills(self):
        """Parse missing skills JSON"""
        return json.loads(self.missing_skills) if self.missing_skills else []
    
    def get_relevant_projects(self):
        """Parse relevant projects JSON"""
        return json.loads(self.relevant_projects) if self.relevant_projects else []
    
    def __repr__(self):
        return f'<AnalysisResult {self.id} - Score: {self.overall_score}>'
