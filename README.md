# Automated Resume Analyzer

An AI-powered web application that analyzes multiple resumes against a specific job description using Google Gemini AI.

## Features

- **Batch Analysis**: Upload and analyze multiple resumes simultaneously.
- **AI-Powered Insights**: Uses Gemini AI to compare resumes with job titles, experience, and certifications.
- **Match Scoring**: Get a percentage-based match score for each candidate.
- **Recommendations**: Receive specific suggestions on how candidates can improve their resumes.
- **Modern UI**: Clean, responsive dark-themed interface built with Flask and Vanilla CSS.

## Technology Stack

- **Backend**: Python, Flask
- **AI Engine**: Google Gemini AI
- **Frontend**: HTML5, CSS3 (Glassmorphism design)
- **Deployment Ready**: Standard Flask structure for easy deployment.

## Getting Started

### Prerequisites

- Python 3.12+
- A Google Gemini API Key (set up in the environment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hackerdrop25-collab/automated-resume-analyser.git
   cd automated-resume-analyser
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the Environment:
   - Create a `.env` file in the root directory.
   - Add your Google Gemini API key:
     ```env
     GEMINI_API_KEY=your_actual_api_key_here
     ```
     > **Note**: You can use `.env.example` as a template.

4. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:5000`.

## Project Structure

- `app.py`: Main Flask server and routing logic.
- `gemini_ai.py`: Analysis module powered by Gemini.
- `templates/`: HTML templates for the UI.
- `uploads/`: Temporary storage for uploaded resumes.
- `requirements.txt`: Project dependencies.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
