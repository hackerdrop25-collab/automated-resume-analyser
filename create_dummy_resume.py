from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "John Doe")
    c.drawString(100, 730, "Software Engineer")
    c.drawString(100, 710, "Experience: 5 years in Python, Flask, and JavaScript.")
    c.drawString(100, 690, "Certifications: AWS Certified Solutions Architect")
    c.drawString(100, 670, "Projects: Built a resume analyzer using Gemini AI.")
    c.save()

if __name__ == "__main__":
    try:
        create_pdf("dummy_resume.pdf")
        print("Scucessfully created dummy_resume.pdf")
    except ImportError:
        print("Reportlab not installed")
