from flask import Flask, request, render_template, redirect, url_for, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from gemini_ai import analyze_resume
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
app.config['UPLOAD_FOLDER'] = 'uploads'

# No database needed for this simplified version
# If you want to keep history without login, we could use session or just skip for now.
# For now, let's keep it simple as requested.

@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        try:
            num_resumes = int(request.form.get('num_resumes', 0))
            job_title = request.form.get('job_title', '')
            experience = request.form.get('experience', '')
            certifications = request.form.get('certifications', '')
            project_description = request.form.get('project_description', '')
            
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
            
            return render_template('results.html', analyses=all_analyses)
        except Exception as e:
            flash(f"Error during analysis: {str(e)}", "danger")
            return redirect(url_for('upload_resume'))
            
    return render_template('upload.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
