# Automated Resume Analyzer

AI-powered resume analysis against job descriptions using Google Gemini AI.

## Important Commands

### 1. Setup Environment
```bash
# Clone and enter directory
git clone https://github.com/hackerdrop25-collab/automated-resume-analyser.git
cd automated-resume-analyser

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Initialize Database
```bash
# Create tables and test user
python db_init.py init
python db_init.py test-user
```

### 4. Run Application
```bash
python app.py
```
Visit `http://127.0.0.1:5001` in your browser.

## Project Structure
- `app.py`: Flask server & routes
- `gemini_ai.py`: Gemini AI integration
- `models.py`: Database models
- `static/`: Frontend assets
- `templates/`: HTML templates

## License
MIT License

