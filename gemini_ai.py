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

    # Determine if we should use multimodal (Gemini native file analysis)
    is_multimodal = filepath.lower().endswith(('.pdf', '.png', '.jpg', '.jpeg'))
    
    resume_text = ""
    file_part = None

    if is_multimodal:
        try:
            # Upload the file to Gemini for native processing (OCR + Layout)
            mime_type = 'application/pdf' if filepath.lower().endswith('.pdf') else 'image/jpeg'
            if filepath.lower().endswith('.png'): mime_type = 'image/png'
            
            uploaded_file = genai.upload_file(filepath, mime_type=mime_type)
            file_part = uploaded_file
            resume_text = "[File uploaded for multimodal analysis]"
        except Exception as e:
            print(f"Error uploading to Gemini: {e}")
            # Fallback to text extraction for PDF if upload fails
            if filepath.lower().endswith('.pdf'):
                resume_text = extract_text_from_pdf(filepath)
    
    # Legacy extraction for DOCX
    if not file_part and filepath.lower().endswith('.docx'):
        try:
            from docx import Document
            doc = Document(filepath)
            resume_text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting DOCX: {e}")

    if not file_part and not resume_text:
        return {
            'filename': filename,
            'job_title': job_title,
            'summary': "Error: Could not extract content from this resume.",
            'score': 0,
            'key_metrics': {'technical_match': 0, 'experience_match': 0, 'formatting_score': 0},
            'skills_analysis': {'matched_technical_skills': [], 'missing_critical_skills': [], 'soft_skills_detected': []},
            'strengths': [],
            'weaknesses': [],
            'recommendations': ["Ensure the file is a valid PDF, DOCX, or Image (JPG/PNG)."],
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
    6. SKILL GAP ANALYSIS: Explicitly compare the candidate's skills with the requirements of "{job_title}".
    7. OPTIMIZATION STRATEGY: Provide specific, actionable advice on how the candidate can "create" or modify their resume to better match this specific deployment/role.

    Job Profile:
    - Role: {job_title}
    - Required Experience: {experience} years
    - Required Certifications: {certifications}
    - Detailed Requirements: {project_description}
    
    Resume Content:
    {resume_text if not file_part else "The resume is provided as an attached file (PDF/Image). Analyze its full content visually and contextually."}
    
    IMPORTANT: For each project in the resume, evaluate if it's relevant to "{job_title}". 
    Only include projects that directly relate to the job requirements.
    
    Provide the output in STRICT JSON format:
    {{
        "filename": "{filename}",
        "job_title": "{job_title}",
        "summary": "3-4 sentence professional summary of fit, including a note on 'Advanced Source Verification'.",
        "score": (0-100 overall score),
        "key_metrics": {{
            "technical_match": (0-100),
            "experience_match": (0-100),
            "formatting_score": (0-100),
            "advanced_source_match": (0-100),
            "soft_skills_score": (0-100)
        }},
        "resume_data": {{
            "name": "Candidate Name",
            "email": "Candidate Email",
            "education": ["list"],
            "full_experience": ["list"],
            "certifications_found": ["list"]
        }},
        "skills_analysis": {{
            "matched_technical_skills": ["skills found that match JD"],
            "missing_critical_skills": ["skills in JD but missing in resume"],
            "soft_skills_detected": ["soft skills list"]
        }},
        "relevant_projects": [
            {{
                "project_name": "Name",
                "relevance_score": (0-100),
                "description": "Brief description",
                "technologies": ["list"],
                "role_match_reason": "Why"
            }}
        ],
        "career_trajectory": "Growth prediction.",
        "red_flags": ["concerns"],
        "filtered_project_count": (n),
        "total_project_count": (n),
        "strengths": ["point 1"],
        "weaknesses": ["point 1"],
        "recommendations": ["point 1"],
        "skill_gap_diff": {{
            "core_mismatch": ["major gaps"],
            "bonus_skills_found": ["extra skills candidate has that are useful"],
            "optimization_advice": "Actionable steps to 'create' the matching resume version",
            "optimized_summary": "A 3-4 sentence professional summary of the candidate, perfectly tuned for THIS role, ready to be copied into their resume."
        }},
        "interview_questions": [
            {{
                "question": "question",
                "sample_solution": "answer",
                "logic": "reason"
            }}
        ]
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare inputs: if we have a file_part, send [prompt, file_part], else [prompt]
        inputs = [prompt]
        if file_part:
            inputs.append(file_part)
            
        response = model.generate_content(inputs)
        
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
