from flask import Flask, request, render_template, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gemini_ai import analyze_resume

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        num_resumes = int(request.form['num_resumes'])
        job_title = request.form['job_title']
        experience = request.form['experience']
        certifications = request.form['certifications']
        
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
                
                analysis = analyze_resume(filepath, job_title, experience, certifications)
                all_analyses.append(analysis)
        
        return render_template('results.html', analyses=all_analyses)
            
    return render_template('upload.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
