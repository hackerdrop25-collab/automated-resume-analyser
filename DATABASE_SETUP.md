# Resume Analyzer Database Setup Guide

## Database System Overview

This resume analyzer now features a complete database system with:

### ✅ Features Implemented

1. **User Authentication**
   - User registration and login system
   - Password hashing with bcrypt
   - Protected routes requiring authentication

2. **Database Models**
   - `User`: User accounts with hashed passwords
   - `Resume`: Uploaded resume metadata and file storage
   - `JobDescription`: Saved job descriptions for reference
   - `AnalysisResult`: Complete analysis results with scores and recommendations

3. **File Storage**
   - User-organized upload directories
   - Secure filename handling
   - File metadata tracking (size, upload time)

4. **Analysis Tracking**
   - All analyses linked to users and resumes
   - Historical analysis records
   - Detailed scoring (technical, experience, formatting)
   - Comprehensive feedback (strengths, weaknesses, recommendations)

---

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
# Create tables
python db_init.py init

# Create a test user
python db_init.py test-user
```

### 3. Configure Environment
Create a `.env` file in the project root:
```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///instance/resume_analyzer.db
# For PostgreSQL: postgresql://user:password@localhost/resume_analyzer

# Upload Configuration
UPLOAD_FOLDER=uploads

# Gemini AI
GEMINI_API_KEY=your-api-key-here
```

### 4. Run Application
```bash
python app.py
```

Visit `http://localhost:5000` and login with your test user credentials.

---

## Database Schema

### Users Table
```
id (PK)
username (unique)
email (unique)
password_hash
created_at
updated_at
```

### Resumes Table
```
id (PK)
user_id (FK → users.id)
filename
original_filename
filepath
file_size
extracted_text
uploaded_at
updated_at
```

### Job Descriptions Table
```
id (PK)
user_id (FK → users.id)
job_title
description
required_experience
required_certifications (JSON)
required_skills (JSON)
created_at
updated_at
```

### Analysis Results Table
```
id (PK)
user_id (FK → users.id)
resume_id (FK → resumes.id)
job_description_id (FK → job_descriptions.id, nullable)
technical_score (0-100)
experience_score (0-100)
formatting_score (0-100)
overall_score (0-100)
summary
strengths (JSON array)
weaknesses (JSON array)
recommendations (JSON array)
matched_skills (JSON array)
missing_skills (JSON array)
analyzed_at
updated_at
```

---

## File Structure

```
automated-resume-analyzer/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── config.py              # Configuration management
├── auth.py                # Authentication routes
├── storage.py             # File storage utilities
├── db_init.py             # Database initialization script
├── gemini_ai.py           # AI analysis engine
├── requirements.txt       # Python dependencies
├── instance/              # Instance files (created)
│   └── resume_analyzer.db # SQLite database
├── uploads/               # User resume uploads
│   ├── user_1/
│   ├── user_2/
│   └── ...
├── static/
│   └── js/
│       └── nexus.js
└── templates/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── upload.html
    ├── results.html
    ├── analysis_history.html
    ├── analysis_detail.html
    ├── job_descriptions.html
    ├── 404.html
    └── 500.html
```

---

## API Routes

### Authentication
- `GET/POST /auth/login` - User login
- `GET/POST /auth/register` - User registration
- `GET /auth/logout` - User logout

### Main Features
- `GET /` - Home (redirects based on auth status)
- `GET /dashboard` - User dashboard
- `GET/POST /upload` - Resume upload and analysis
- `GET/POST /job-description` - Manage job descriptions
- `GET /analysis-history` - View all analyses
- `GET /analysis/<id>` - View detailed analysis

### API Endpoints
- `GET /api/analysis/<id>` - Get analysis as JSON

---

## Database Management Commands

```bash
# Initialize database
python db_init.py init

# Reset database (destructive)
python db_init.py reset

# Drop all tables (destructive)
python db_init.py drop

# Create test user
python db_init.py test-user

# Show statistics
python db_init.py stats
```

---

## Configuration Options

### Environment Variables
- `FLASK_ENV`: development / production / testing
- `SECRET_KEY`: Session encryption key
- `DATABASE_URL`: Database connection string
- `UPLOAD_FOLDER`: Upload directory path
- `MAX_CONTENT_LENGTH`: Max upload size (default: 16MB)
- `GEMINI_API_KEY`: AI analysis API key

### Allowed File Extensions
- `.pdf`
- `.docx`
- `.doc`
- `.txt`

---

## Usage Examples

### Using the Web Interface
1. Register a new account
2. Login with credentials
3. Upload resumes
4. View analysis results
5. Browse analysis history
6. Manage job descriptions

### Using Python API
```python
from app import app, db
from models import User, Resume, AnalysisResult

with app.app_context():
    # Get user analyses
    user = User.query.filter_by(username='john').first()
    analyses = AnalysisResult.query.filter_by(user_id=user.id).all()
    
    for analysis in analyses:
        print(f"Overall Score: {analysis.overall_score}%")
        print(f"Strengths: {analysis.get_strengths()}")
```

---

## Backup & Migration

### SQLite Backup
```bash
# Copy the database file
cp instance/resume_analyzer.db instance/resume_analyzer.db.backup
```

### PostgreSQL Migration
1. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/resume_analyzer
   ```
2. Install PostgreSQL driver: `pip install psycopg2-binary`
3. Run: `python db_init.py reset`

---

## Troubleshooting

### Database Error: "table already exists"
```bash
python db_init.py reset
```

### Permission Denied on uploads folder
```bash
mkdir -p uploads
chmod 755 uploads
```

### Foreign Key Constraint Error
- Ensure SQLite is properly configured
- For production, use PostgreSQL

### User Can't Login
- Check password hash is correctly generated
- Verify user exists: `python db_init.py stats`

---

## Production Deployment Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Use PostgreSQL database
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Set up proper file upload directory with permissions
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging
- [ ] Use environment variables (never hardcode secrets)
- [ ] Enable HTTPS

---

## Support & Documentation

For more information, see:
- Flask: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Flask-Login: https://flask-login.readthedocs.io/

---

**Last Updated:** February 2026
