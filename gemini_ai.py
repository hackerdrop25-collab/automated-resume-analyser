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
            'key_metrics': {'technical_match': 0, 'experience_match': 0, 'formatting_score': 0},
            'skills_analysis': {'matched_technical_skills': [], 'missing_critical_skills': [], 'soft_skills_detected': []},
            'strengths': [],
            'weaknesses': [],
            'recommendations': ["Add a valid GEMINI_API_KEY to the .env file."],
            'interview_questions': []
        }
    
    # Re-configure if key was added after startup
    genai.configure(api_key=current_api_key)

    # Handle PDF or DOCX
    resume_text = ""
    if filepath.lower().endswith('.pdf'):
        resume_text = extract_text_from_pdf(filepath)
    elif filepath.lower().endswith('.docx'):
        try:
            from docx import Document
            doc = Document(filepath)
            resume_text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting DOCX: {e}")
            
    if not resume_text:
        return {
            'filename': filename,
            'job_title': job_title,
            'summary': "Error: Could not extract text from this resume.",
            'score': 0,
            'key_metrics': {'technical_match': 0, 'experience_match': 0, 'formatting_score': 0},
            'skills_analysis': {'matched_technical_skills': [], 'missing_critical_skills': [], 'soft_skills_detected': []},
            'strengths': [],
            'weaknesses': [],
            'recommendations': ["Ensure the file is a valid PDF or DOCX."],
            'interview_questions': []
        }

    prompt = f"""
    You are a Senior Technical Recruiter with 20+ years of experience.
    Perform a rigorous analysis of this resume against the job requirements.
    
    CRITICAL FOCUS: You must calculate an "Experience Match" based on the required {experience} years vs. what's in the resume.

    Job Profile:
    - Role: {job_title}
    - Required Experience: {experience} years
    - Required Certifications: {certifications}
    - Detailed Requirements: {project_description}
    
    Resume Content:
    {resume_text}
    
    Provide the output in STRICT JSON format:
    {{
        "filename": "{filename}",
        "job_title": "{job_title}",
        "summary": "3-4 sentence professional summary of fit.",
        "score": (0-100 overall score),
        "key_metrics": {{
            "technical_match": (0-100),
            "experience_match": (0-100),
            "formatting_score": (0-100)
        }},
        "skills_analysis": {{
            "matched_technical_skills": ["list", "of", "skills"],
            "missing_critical_skills": ["list", "of", "missing"],
            "soft_skills_detected": ["list", "of", "soft", "skills"]
        }},
        "strengths": ["point 1", "point 2"],
        "weaknesses": ["area 1", "area 2"],
        "recommendations": ["advice 1", "advice 2"],
        "interview_questions": ["question 1", "question 2", "question 3"]
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        result_text = response.text.strip()
        # Remove any markdown code blocks
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:].strip()
        
        result = json.loads(result_text)
        return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {{
            'filename': filename,
            'job_title': job_title,
            'summary': f"Error during AI analysis: {str(e)}",
            'score': 0,
            'key_metrics': {'technical_match': 0, 'experience_match': 0, 'formatting_score': 0},
            'skills_analysis': {'matched_technical_skills': [], 'missing_critical_skills': [], 'soft_skills_detected': []},
            'strengths': [],
            'weaknesses': [],
            'recommendations': ["Check API key and try again."],
            'interview_questions': []
        }}
