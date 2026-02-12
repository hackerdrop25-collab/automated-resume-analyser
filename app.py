from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user, login_user
import os
from datetime import datetime
from dotenv import load_dotenv

# Import models and configuration
from models import db, User, Resume, JobDescription, AnalysisResult, SecurityLog
from config import get_config
# auth blueprint removed — app will auto-login a default local user
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

# Create database tables, ensure default user, and prepare upload folder
with app.app_context():
    db.create_all()
    # ensure a default single-user account exists so app works without login
    DEFAULT_EMAIL = os.environ.get('DEFAULT_USER_EMAIL', 'local@localhost')
    default_user = User.query.filter_by(email=DEFAULT_EMAIL).first()
    if not default_user:
        default_user = User(email=DEFAULT_EMAIL)
        # intentionally set an empty password for local mode (no login required)
        default_user.set_password(os.environ.get('DEFAULT_USER_PASSWORD', ''))
        db.session.add(default_user)
        db.session.commit()
    app.config['DEFAULT_USER_ID'] = default_user.id


# Auto-login default user for every request when no explicit user is logged in
@app.before_request
def auto_login_default_user():
    try:
        if not current_user.is_authenticated:
            user = User.query.get(app.config.get('DEFAULT_USER_ID'))
            if user:
                login_user(user)
    except Exception:
        pass


def log_security_event(event_type, description):
    """Utility to log system security events"""
    try:
        log = SecurityLog(
            user_id=current_user.id if current_user.is_authenticated else None,
            event_type=event_type,
            description=description,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Failed to log security event: {str(e)}")


@app.route('/')
def index():
    """Home page - show dashboard"""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard - upload resume"""
    return render_template('dashboard.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_resume():
    """Upload and analyze resumes"""
    if request.method == 'POST':
        try:
            log_security_event('UPLOAD_START', f"User starting upload of resumes.")
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
                    log_security_event('ANALYSIS_START', f"Starting AI analysis for resume: {original_filename}")
                    analysis = analyze_resume(filepath, job_title, experience, certifications, project_description)
                    log_security_event('ANALYSIS_COMPLETE', f"Successfully analyzed resume: {original_filename}")
                    
                    # Normalize analysis data for storage and template
                    # Gemini returns keys like 'score', 'key_metrics', etc.
                    metrics = analysis.get('key_metrics', {})
                    skills_analysis = analysis.get('skills_analysis', {})
                    
                    overall_score = analysis.get('score', 0)
                    tech_score = metrics.get('technical_match', 0)
                    exp_score = metrics.get('experience_match', 0)
                    fmt_score = metrics.get('formatting_score', 0)
                    
                    # Store analysis result in database
                    analysis_result = AnalysisResult(
                        user_id=current_user.id,
                        resume_id=resume.id,
                        technical_score=tech_score,
                        experience_score=exp_score,
                        formatting_score=fmt_score,
                        overall_score=overall_score,
                        summary=analysis.get('summary'),
                        strengths=json.dumps(analysis.get('strengths', [])),
                        weaknesses=json.dumps(analysis.get('weaknesses', [])),
                        recommendations=json.dumps(analysis.get('recommendations', [])),
                        matched_skills=json.dumps(skills_analysis.get('matched_technical_skills', [])),
                        missing_skills=json.dumps(skills_analysis.get('missing_critical_skills', [])),
                        relevant_projects=json.dumps(analysis.get('relevant_projects', [])),
                        filtered_project_count=analysis.get('filtered_project_count', 0),
                        total_project_count=analysis.get('total_project_count', 0)
                    )
                    db.session.add(analysis_result)
                    
                    # Store processed data for the immediate response
                    processed_analysis = {
                        'overall_score': overall_score,
                        'technical_score': tech_score,
                        'experience_score': exp_score,
                        'formatting_score': fmt_score,
                        'summary': analysis.get('summary'),
                        'strengths': analysis.get('strengths', []),
                        'weaknesses': analysis.get('weaknesses', []),
                        'recommendations': analysis.get('recommendations', []),
                        'matched_skills': skills_analysis.get('matched_technical_skills', []),
                        'missing_skills': skills_analysis.get('missing_critical_skills', []),
                        'relevant_projects': analysis.get('relevant_projects', []),
                        'filtered_project_count': analysis.get('filtered_project_count', 0),
                        'total_project_count': analysis.get('total_project_count', 0)
                    }
                    
                    all_analyses.append({
                        'analysis': processed_analysis,
                        'resume_filename': original_filename,
                        'analysis_id': None
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
            return render_template('matching.html', analyses=all_analyses)
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error during analysis: {str(e)}", "danger")
            return redirect(url_for('upload_resume'))
    
    return render_template('upload.html')


@app.route('/results/latest')
@login_required
def view_latest_results():
    """View the most recent analysis results"""
    # Get all analysis results for current user, ordered by most recent
    results = AnalysisResult.query.filter_by(user_id=current_user.id).order_by(AnalysisResult.analyzed_at.desc()).all()
    
    if not results:
        flash('No analysis results found. Please upload and analyze resumes first.', 'info')
        return redirect(url_for('upload_resume'))
    
    # Group results by analysis session (same analyzed_at timestamp within 1 minute)
    from datetime import timedelta
    sessions = []
    current_session = []
    last_time = None
    
    for result in results:
        if last_time is None or abs((result.analyzed_at - last_time).total_seconds()) < 60:
            current_session.append(result)
            last_time = result.analyzed_at
        else:
            if current_session:
                sessions.append(current_session)
            current_session = [result]
            last_time = result.analyzed_at
    
    if current_session:
        sessions.append(current_session)
    
    # Use the most recent session
    latest_session = sessions[0] if sessions else []
    
    # Format data for template
    all_analyses = []
    for result in latest_session:
        analysis_data = {
            'overall_score': result.overall_score or 0,
            'technical_score': result.technical_score or 0,
            'experience_score': result.experience_score or 0,
            'formatting_score': result.formatting_score or 0,
            'summary': result.summary,
            'strengths': result.get_strengths(),
            'weaknesses': result.get_weaknesses(),
            'recommendations': result.get_recommendations(),
            'matched_skills': result.get_matched_skills(),
            'missing_skills': result.get_missing_skills(),
            'relevant_projects': result.get_relevant_projects(),
            'filtered_project_count': result.filtered_project_count,
            'total_project_count': result.total_project_count
        }
        
        all_analyses.append({
            'analysis': analysis_data,
            'resume_filename': result.resume.original_filename,
            'analysis_id': result.id
        })
    
    return render_template('matching.html', analyses=all_analyses)


@app.route('/results/<int:resume_id>')
@login_required
def view_specific_result(resume_id):
    """View analysis result for a specific resume"""
    result = AnalysisResult.query.filter_by(resume_id=resume_id, user_id=current_user.id).first_or_404()
    
    # Format data for template
    analysis_data = {
        'overall_score': result.overall_score or 0,
        'technical_score': result.technical_score or 0,
        'experience_score': result.experience_score or 0,
        'formatting_score': result.formatting_score or 0,
        'summary': result.summary,
        'strengths': result.get_strengths(),
        'weaknesses': result.get_weaknesses(),
        'recommendations': result.get_recommendations(),
        'matched_skills': result.get_matched_skills(),
        'missing_skills': result.get_missing_skills(),
        'relevant_projects': result.get_relevant_projects(),
        'filtered_project_count': result.filtered_project_count,
        'total_project_count': result.total_project_count
    }
    
    all_analyses = [{
        'analysis': analysis_data,
        'resume_filename': result.resume.original_filename,
        'analysis_id': result.id
    }]
    
    return render_template('matching.html', analyses=all_analyses)


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


@app.route('/admin/security')
@login_required
def security_audit():
    """Security audit dashboard - view system logs"""
    logs = SecurityLog.query.order_by(SecurityLog.timestamp.desc()).limit(100).all()
    return render_template('security.html', logs=logs)


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
    app.run(debug=True, port=5001)
