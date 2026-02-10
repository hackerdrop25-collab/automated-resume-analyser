from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
import os
from datetime import datetime
from dotenv import load_dotenv

# Import models and configuration
from models import db, User, Resume, JobDescription, AnalysisResult
from config import get_config
from auth import auth_bp
from storage import save_resume_file, delete_resume_file
from gemini_ai import analyze_resume
import json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(get_config())

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth_bp)

# Create database tables and upload folder
with app.app_context():
    db.create_all()
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    """Home page - redirect based on auth status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - shows analysis history"""
    # Get user's recent analyses
    recent_analyses = AnalysisResult.query.filter_by(user_id=current_user.id)\
        .order_by(AnalysisResult.analyzed_at.desc())\
        .limit(10)\
        .all()
    
    # Get resume count
    resume_count = Resume.query.filter_by(user_id=current_user.id).count()
    
    # Get analysis count
    analysis_count = AnalysisResult.query.filter_by(user_id=current_user.id).count()
    
    return render_template(
        'dashboard.html',
        recent_analyses=recent_analyses,
        resume_count=resume_count,
        analysis_count=analysis_count
    )


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload and analyze resumes"""
    if request.method == 'POST':
        try:
            num_resumes = int(request.form.get('num_resumes', 0))
            if num_resumes <= 0:
                flash('Please specify at least one resume', 'warning')
                return redirect(url_for('upload_resume'))
            
            job_title = request.form.get('job_title', '')
            experience = request.form.get('experience', '')
            certifications = request.form.get('certifications', '')
            project_description = request.form.get('project_description', '')
            
            if not job_title:
                flash('Job title is required', 'warning')
                return redirect(url_for('upload_resume'))
            
            all_analyses = []
            resume_ids = []
            
            for i in range(1, num_resumes + 1):
                file_key = f'resume_{i}'
                if file_key not in request.files:
                    continue
                    
                file = request.files[file_key]
                if not file or file.filename == '':
                    continue
                
                try:
                    # Save resume file
                    original_filename, filepath, file_size = save_resume_file(file, current_user.id)
                    
                    # Store resume metadata in database
                    resume = Resume(
                        user_id=current_user.id,
                        filename=os.path.basename(filepath),
                        original_filename=original_filename,
                        filepath=filepath,
                        file_size=file_size
                    )
                    db.session.add(resume)
                    db.session.flush()  # Get the resume ID
                    
                    # Perform analysis
                    analysis = analyze_resume(filepath, job_title, experience, certifications, project_description)
                    
                    # Store analysis result in database
                    analysis_result = AnalysisResult(
                        user_id=current_user.id,
                        resume_id=resume.id,
                        technical_score=analysis.get('technical_score'),
                        experience_score=analysis.get('experience_score'),
                        formatting_score=analysis.get('formatting_score'),
                        overall_score=analysis.get('overall_score'),
                        summary=analysis.get('summary'),
                        strengths=json.dumps(analysis.get('strengths', [])),
                        weaknesses=json.dumps(analysis.get('weaknesses', [])),
                        recommendations=json.dumps(analysis.get('recommendations', [])),
                        matched_skills=json.dumps(analysis.get('matched_skills', [])),
                        missing_skills=json.dumps(analysis.get('missing_skills', []))
                    )
                    db.session.add(analysis_result)
                    
                    all_analyses.append({
                        'analysis': analysis,
                        'resume_filename': original_filename,
                        'analysis_id': None  # Will be set after commit
                    })
                    resume_ids.append(resume.id)
                    
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error processing {file_key}: {str(e)}', 'danger')
                    continue
            
            db.session.commit()
            
            if not all_analyses:
                flash('No valid resumes were processed', 'warning')
                return redirect(url_for('upload_resume'))
            
            # Add analysis IDs after commit
            for i, analysis_data in enumerate(all_analyses):
                if i < len(resume_ids):
                    analysis_data['analysis_id'] = AnalysisResult.query.filter_by(
                        resume_id=resume_ids[i]
                    ).first().id
            
            flash(f'Successfully analyzed {len(all_analyses)} resume(s)', 'success')
            return render_template('results.html', analyses=all_analyses)
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error during analysis: {str(e)}", "danger")
            return redirect(url_for('upload_resume'))
    
    return render_template('upload.html')


@app.route('/job-description', methods=['GET', 'POST'])
@login_required
def manage_job_descriptions():
    """Manage job descriptions for analysis"""
    if request.method == 'POST':
        try:
            job_title = request.form.get('job_title', '').strip()
            description = request.form.get('description', '')
            experience = request.form.get('experience', '')
            certifications = request.form.get('certifications', '')
            skills = request.form.get('skills', '')
            
            if not job_title:
                flash('Job title is required', 'warning')
                return redirect(url_for('manage_job_descriptions'))
            
            job_desc = JobDescription(
                user_id=current_user.id,
                job_title=job_title,
                description=description,
                required_experience=experience,
                required_certifications=json.dumps(certifications.split(',') if certifications else []),
                required_skills=json.dumps(skills.split(',') if skills else [])
            )
            db.session.add(job_desc)
            db.session.commit()
            
            flash(f'Job description for {job_title} saved', 'success')
            return redirect(url_for('manage_job_descriptions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving job description: {str(e)}', 'danger')
            return redirect(url_for('manage_job_descriptions'))
    
    job_descriptions = JobDescription.query.filter_by(user_id=current_user.id).all()
    return render_template('job_descriptions.html', job_descriptions=job_descriptions)


@app.route('/analysis-history')
@login_required
def analysis_history():
    """View all analysis history"""
    page = request.args.get('page', 1, type=int)
    analyses = AnalysisResult.query.filter_by(user_id=current_user.id)\
        .order_by(AnalysisResult.analyzed_at.desc())\
        .paginate(page=page, per_page=20)
    
    return render_template('analysis_history.html', analyses=analyses)


@app.route('/analysis/<int:analysis_id>')
@login_required
def view_analysis(analysis_id):
    """View detailed analysis result"""
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Verify user owns this analysis
    if analysis.user_id != current_user.id:
        flash('You do not have permission to view this analysis', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('analysis_detail.html', analysis=analysis)


@app.route('/api/analysis/<int:analysis_id>')
@login_required
def get_analysis_data(analysis_id):
    """Get analysis data as JSON"""
    analysis = AnalysisResult.query.get_or_404(analysis_id)
    
    # Verify user owns this analysis
    if analysis.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': analysis.id,
        'overall_score': analysis.overall_score,
        'technical_score': analysis.technical_score,
        'experience_score': analysis.experience_score,
        'formatting_score': analysis.formatting_score,
        'summary': analysis.summary,
        'strengths': analysis.get_strengths(),
        'weaknesses': analysis.get_weaknesses(),
        'recommendations': analysis.get_recommendations(),
        'matched_skills': analysis.get_matched_skills(),
        'missing_skills': analysis.get_missing_skills(),
        'resume': {
            'original_filename': analysis.resume.original_filename,
            'uploaded_at': analysis.resume.uploaded_at.isoformat()
        },
        'analyzed_at': analysis.analyzed_at.isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
