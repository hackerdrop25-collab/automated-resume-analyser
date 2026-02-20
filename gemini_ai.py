import os
import json
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

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
    
    current_api_key = os.getenv("GEMINI_API_KEY")
    if not current_api_key or "your_gemini_api_key_here" in current_api_key or current_api_key == "":
        raise ValueError("GEMINI_API_KEY not found. Please set a valid API key in your .env file.")

    genai.configure(api_key=current_api_key)

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
    Perform a rigorous dual-phase analysis:
    Phase 1: Resume Matching against Job Description
    Phase 2: Advanced Source Verification & Inference (simulating checks on GitHub, LinkedIn, Portfolio links)

    CRITICAL FOCUS: 
    1. Extract INDIVIDUAL PROJECTS from the resume
    2. Score each project's relevance to the "{job_title}" role (0-100%)
    3. ONLY include projects with relevance score > 60%
    4. Calculate "Experience Match" based on required {experience} years vs. actual experience
    5. Evaluate "Advanced Source Match" by inferring quality from GitHub links, Portfolio URLs, or Company Reputations mentioned.

    Job Profile:
    - Role: {job_title}
    - Required Experience: {experience} years
    - Required Certifications: {certifications}
    - Detailed Requirements: {project_description}
    
    Resume Content:
    {resume_text}
    
    IMPORTANT: For each project in the resume, evaluate if it's relevant to "{job_title}". 
    Only include projects that directly relate to the job requirements.
    
    Provide the output in STRICT JSON format:
    {
        "filename": "{filename}",
        "job_title": "{job_title}",
        "summary": "3-4 sentence professional summary of fit, including a note on 'Advanced Source Verification' (e.g. 'GitHub profile indicates strong open source contribution...').",
        "score": (0-100 overall score),
        "key_metrics": {
            "technical_match": (0-100),
            "experience_match": (0-100),
            "formatting_score": (0-100),
            "advanced_source_match": (0-100, inferred from links/depth),
            "soft_skills_score": (0-100, based on detected soft skills depth)
        },
        "resume_data": {
            "name": "Candidate Name (if found)",
            "email": "Candidate Email (if found)",
            "education": ["list of education entries"],
            "full_experience": ["list of recent job roles and key responsibilities"],
            "certifications_found": ["list of certifications found in resume"]
        },
        "skills_analysis": {
            "matched_technical_skills": ["list", "of", "skills"],
            "missing_critical_skills": ["list", "of", "missing"],
            "soft_skills_detected": ["list", "of", "soft", "skills"]
        },
        "relevant_projects": [
            {
                "project_name": "Name of the project",
                "relevance_score": (0-100, only include if > 60),
                "description": "Brief description of what the project does",
                "technologies": ["tech1", "tech2"],
                "role_match_reason": "Why this project is relevant to {job_title}"
            }
        ],
        "career_trajectory": "1-2 sentence prediction of the candidate's future growth and potential roles.",
        "red_flags": ["list of potential concerns, e.g. frequent job hopping, gaps without explanation, skill mismatch"],
        "filtered_project_count": (number of relevant projects included),
        "total_project_count": (total number of projects found in resume),
        "strengths": ["point 1", "point 2"],
        "weaknesses": ["area 1", "area 2"],
        "recommendations": ["advice 1", "advice 2"],
        "interview_questions": [
            {
                "question": "Strategic technical or behavioral question based on this specific resume's content",
                "sample_solution": "The 'Sample Solution' (perfect answer) the recruiter should look for",
                "logic": "The reasoning behind asking this specific question for this role"
            }
        ]
    }
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
        return result, resume_text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise e
