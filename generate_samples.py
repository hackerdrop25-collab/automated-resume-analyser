from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_resume(filename, name, email, phone, experience, education, skills, projects):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, height - 50, name)
    
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, f"{email} | {phone}")
    
    # Line
    c.line(50, height - 80, width - 50, height - 80)
    
    y = height - 100
    
    # Experience
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "PROFESSIONAL EXPERIENCE")
    y -= 20
    
    for exp in experience:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, exp['role'])
        c.setFont("Helvetica", 10)
        c.drawRightString(width - 50, y, exp['period'])
        y -= 15
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, y, exp['company'])
        y -= 15
        
        c.setFont("Helvetica", 9)
        for bullet in exp['bullets']:
            c.drawString(60, y, "• " + bullet)
            y -= 12
        y -= 10
        
    # Education
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "EDUCATION")
    y -= 20
    for edu in education:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, edu['degree'])
        c.drawRightString(width - 50, y, edu['year'])
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(50, y, edu['school'])
        y -= 15
    y -= 10
    
    # Skills
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "TECHNICAL SKILLS")
    y -= 20
    c.setFont("Helvetica", 10)
    skill_text = ", ".join(skills)
    c.drawString(50, y, skill_text)
    y -= 30
    
    # Projects
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "KEY PROJECTS")
    y -= 20
    for proj in projects:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, proj['name'])
        y -= 15
        c.setFont("Helvetica", 9)
        c.drawString(50, y, proj['desc'])
        y -= 15
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, y, "Technologies: " + ", ".join(proj['tech']))
        y -= 15
    
    c.save()

# Sample Data
resumes = [
    {
        "filename": "john_doe_software_engineer.pdf",
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1 (555) 123-4567",
        "experience": [
            {
                "role": "Senior Software Engineer",
                "period": "2020 - Present",
                "company": "Tech Solutions Inc.",
                "bullets": [
                    "Led a team of 5 to develop a microservices-based cloud platform using Python and AWS.",
                    "Improved system performance by 40% through optimized database indexing and caching strategies.",
                    "Architected a real-time data processing pipeline handling 1M+ events per minute."
                ]
            },
            {
                "role": "Full Stack Developer",
                "period": "2017 - 2020",
                "company": "Innovate Soft",
                "bullets": [
                    "Developed responsive React.js frontend for an enterprise HRMS system.",
                    "Integrated Stripe API for secure payment processing.",
                    "Reduced page load time by 30% using tree-shaking and lazy loading."
                ]
            }
        ],
        "education": [
            {"degree": "B.S. in Computer Science", "school": "Stanford University", "year": "2017"}
        ],
        "skills": ["Python", "JavaScript", "React", "Node.js", "PostgreSQL", "AWS", "Docker", "Kubernetes"],
        "projects": [
            {
                "name": "AI Image Generator",
                "desc": "A web application that generates images from text prompts using Stable Diffusion.",
                "tech": ["Python", "Flask", "Pytorch", "Next.js"]
            }
        ]
    },
    {
        "filename": "jane_smith_data_scientist.pdf",
        "name": "Jane Smith",
        "email": "jane.smith@datascience.com",
        "phone": "+1 (555) 987-6543",
        "experience": [
            {
                "role": "Lead Data Scientist",
                "period": "2021 - Present",
                "company": "Data Insights Corp",
                "bullets": [
                    "Developed a churn prediction model with 92% accuracy, reducing customer attrition by 15%.",
                    "Implemented an NLP-based sentiment analysis engine for customer feedback.",
                    "Deployed ML models using SageMaker and enforced CI/CD pipelines for models."
                ]
            }
        ],
        "education": [
            {"degree": "M.S. in Statistics", "school": "MIT", "year": "2021"},
            {"degree": "B.A. in Mathematics", "school": "UC Berkeley", "year": "2019"}
        ],
        "skills": ["Python", "R", "SQL", "Scikit-Learn", "TensorFlow", "PyTorch", "Tableau", "Apache Spark"],
        "projects": [
            {
                "name": "Stock Market Predictor",
                "desc": "Used LSTM neural networks to forecast stock prices with high precision.",
                "tech": ["Python", "Keras", "Pandas", "Yahoo Finance API"]
            }
        ]
    }
]

if __name__ == "__main__":
    os.makedirs("sample_resumes", exist_ok=True)
    for r in resumes:
        create_resume(os.path.join("sample_resumes", r['filename']), r['name'], r['email'], r['phone'], r['experience'], r['education'], r['skills'], r['projects'])
    print("Sample resumes generated in 'sample_resumes' folder.")
