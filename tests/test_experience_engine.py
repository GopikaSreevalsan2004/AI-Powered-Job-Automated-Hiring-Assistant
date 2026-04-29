import sys
import os
import json
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.pdf_parser import PDFParser
from utils.text_cleaner import TextCleaner
from parsers.resume_classifier import ResumeSectionClassifier
from ats_engine.experience_engine import ExperienceEngine

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

def test_experience_engine_with_real_resume():
    # 1. Paths
    resume_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'resumes', 'Resume_2_Sarah_Jenkins.pdf')
    
    if not os.path.exists(resume_path):
        print(f"Resume file not found at {resume_path}")
        return

    print(f"--- Processing {os.path.basename(resume_path)} ---")

    # 2. Extract Text
    pdf_parser = PDFParser()
    raw_text = pdf_parser.extract_text(resume_path)
    
    if not raw_text:
        print("Failed to extract text from PDF.")
        return

    # 3. Clean Text
    cleaner = TextCleaner()
    cleaned_text = cleaner.clean(raw_text)
    cleaned_text = cleaner.standardize_headings(cleaned_text)

    # 4. Process Experience (Using full cleaned text)
    print("--- Using full text for experience extraction ---")
    experience_engine = ExperienceEngine()
    
    # Dummy job requirements for scoring
    job_requirements = {
        "target_role": "Software Engineer",
        "required_skills": ["Python", "Machine Learning", "Data", "AWS"]
    }
    
    results = experience_engine.process_experience_text(cleaned_text, job_requirements)
    
    print("\n--- Structured Experience Object ---")
    print(json.dumps(results, indent=2, cls=DateTimeEncoder))
    
    assert 'structured_experiences' in results
    assert 'analysis' in results
    
    print("\n--- Summary ---")
    print(f"Total Experience: {results['analysis']['total_experience_years']} years")
    print(f"Number of Roles: {len(results['structured_experiences'])}")
    if results['analysis']['gaps']:
        print(f"Detected Gaps: {len(results['analysis']['gaps'])}")
    if results['analysis']['overlaps']:
        print(f"Detected Overlaps: {len(results['analysis']['overlaps'])}")

if __name__ == "__main__":
    try:
        test_experience_engine_with_real_resume()
        print("\nTest passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
