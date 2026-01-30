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
    Analyzes a resume against job requirements using Gemini AI.
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
    You are an expert HR Recruiter and Career Coach. 
    Analyze the following resume against the job requirements and project description.
    
    Job Title: {job_title}
    Required Experience: {experience} years
    Required Certifications: {certifications}
    Project Description/Job Requirements: {project_description}
    
    Resume Content:
    {resume_text}
    
    Provide your analysis in the following JSON format ONLY. 
    Do not include any other text or formatting.
    {{
        "filename": "{filename}",
        "job_title": "{job_title}",
        "summary": "A concise professional summary of the match (2-3 sentences).",
        "score": (A number between 0 and 100 representing the match percentage),
        "recommendations": ["Recommendation 1", "Recommendation 2", ...]
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Clean the response to ensure it's valid JSON
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
        elif result_text.startswith("```"):
            result_text = result_text[3:-3].strip()
            
        result = json.loads(result_text)
        return result
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {
            'filename': filename,
            'job_title': job_title,
            'summary': f"Error during AI analysis: {str(e)}",
            'score': 0,
            'recommendations': ["Try again in a few moments.", "Check your API key configuration."]
        }
