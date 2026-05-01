import sys
import os
import json

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.pdf_parser import PDFParser
from utils.text_cleaner import TextCleaner
from ats_engine.education_engine import EducationEngine

def test_education_engine_with_real_resume():
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

    # 4. Process Education
    education_engine = EducationEngine()
    
    # Dummy job requirements for scoring
    job_requirements = {
        "minimum_education": "Master of Science",
        "target_field": "Computer Science",
        "preferred_cert_categories": ["Cloud", "Data & AI"],
        "required_cert_keywords": ["AWS"]
    }
    
    profile_obj = education_engine.process_education_text(cleaned_text, job_requirements)
    results = profile_obj.to_dict()
    
    print("\n--- Structured Academic Profile ---")
    print(json.dumps(results, indent=2))
    
    assert 'education' in results
    assert 'certifications' in results
    assert 'relevance_scoring' in results
    
    scoring = results['relevance_scoring']
    assert 'total_academic_score' in scoring
    assert 'education_score' in scoring
    assert 'certification_score' in scoring

if __name__ == "__main__":
    try:
        test_education_engine_with_real_resume()
        print("\nTest passed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
