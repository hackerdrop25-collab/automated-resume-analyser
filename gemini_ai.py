import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini AI
def get_api_key():
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")

api_key = get_api_key()
if api_key:
    genai.configure(api_key=api_key)
else:
    print("CRITICAL: GEMINI_API_KEY for Resume Analyzer not found in environment.")

def extract_text_from_pdf(filepath):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def analyze_resume(filepath, job_title, experience, certifications, project_description):
    """
    Analyzes a resume against job requirements using Gemini AI with advanced detailed metrics.
    """
    filename = os.path.basename(filepath)
    
    # Check for API key first
    current_api_key = os.getenv("GEMINI_API_KEY")
    if not current_api_key or "your_gemini_api_key_here" in current_api_key:
        return {
            'filename': filename,
            'job_title': job_title,
            'summary': "Configuration Error: GEMINI_API_KEY is missing or invalid. Please update your .env file with a valid key.",
            'score': 0,
            'recommendations': ["Add a valid GEMINI_API_KEY to the .env file.", "Restart the server after adding the key."]
        }
    
    # Re-configure if key was added after startup
    genai.configure(api_key=current_api_key)

    resume_text = extract_text_from_pdf(filepath)
    
    if not resume_text:
        return {
            'filename': filename,
            'job_title': job_title,
            'summary': "Error: Could not extract text from this resume.",
            'score': 0,
            'recommendations': ["Ensure the file is a valid PDF and contains readable text."]
        }

    prompt = f"""
    You are a Senior Technical Recruiter and Career Coach with 15+ years of experience.
    Your task is to perform a deep-dive analysis of the following resume against the specific job requirements.
    
    Job Profile:
    - Role: {job_title}
    - Required Experience: {experience} years
    - Required Certifications: {certifications}
    - Detailed Requirements: {project_description}
    
    Resume Content:
    {resume_text}
    
    Analyze the resume for:
    1. Technical Skills Match (What is present vs. missing)
    2. Soft Skills & Leadership qualities.
    3. Experience Relevance & Depth.
    4. Formatting, Clarity, and ATS Optimization.
    5. Cultural Fit indicators.

    Provide the output in the following STRICT JSON format containing ONLY the JSON object. Do not add markdown backticks or any other text.
    {{
        "filename": "{filename}",
        "job_title": "{job_title}",
        "summary": "A professional executive summary of the candidate's fit (3-4 sentences).",
        "score": (0-100 integer),
        "key_metrics": {{
            "technical_match": (0-100 integer),
            "experience_rating": (0-100 integer),
            "formatting_score": (0-100 integer)
        }},
        "skills_analysis": {{
            "matched_technical_skills": ["skill1", "skill2", ...],
            "missing_critical_skills": ["missing1", "missing2", ...],
            "soft_skills_detected": ["soft1", "soft2", ...]
        }},
        "strengths": ["Strong point 1", "Strong point 2", ...],
        "weaknesses": ["Weak area 1", "Weak area 2", ...],
        "recommendations": ["Actionable advice 1", "Actionable advice 2", ...]
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Clean the response to ensure it's valid JSON
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:].strip()
        if result_text.startswith("```"):
             result_text = result_text[3:].strip()
        if result_text.endswith("```"):
            result_text = result_text[:-3].strip()
            
        result = json.loads(result_text)
        return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {
            'filename': filename,
            'job_title': job_title,
            'summary': f"Error during AI analysis: {str(e)}",
            'score': 0,
            'key_metrics': {'technical_match': 0, 'experience_rating': 0, 'formatting_score': 0},
            'skills_analysis': {'matched_technical_skills': [], 'missing_critical_skills': [], 'soft_skills_detected': []},
            'strengths': [],
            'weaknesses': [],
            'recommendations': ["Try again in a few moments.", "Check your API key configuration."]
        }
