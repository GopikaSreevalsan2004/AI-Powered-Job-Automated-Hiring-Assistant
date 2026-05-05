import os
import sys
import json

# Ensure we can import from the root directory
sys.path.append(os.path.abspath('.'))

from parsers.pdf_parser import PDFParser
from utils.text_cleaner import TextCleaner
from ats_engine.education_engine import EducationEngine

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling potential datetime objects."""
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

def generate_academic_profiles():
    """
    Reads all resumes from data/resumes/, parses education/certifications,
    and saves the structured academic profiles to data/processed/.
    """
    engine = EducationEngine()
    pdf_parser = PDFParser()
    cleaner = TextCleaner()
    
    resume_dir = 'data/resumes'
    output_dir = 'data/processed'
    output_filename = 'structured_academic_profiles.json'
    
    if not os.path.exists(resume_dir):
        print(f"Error: Resume directory {resume_dir} does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    # Generic job requirements for scoring
    job_requirements = {
        "minimum_education": "Bachelor of Science",
        "target_field": "Computer Science",
        "preferred_cert_categories": ["Cloud", "Data Science", "Security"],
        "required_cert_keywords": ["AWS", "Google", "Certified"]
    }
    
    all_profiles = {}
    
    print(f"Starting education/certification extraction for resumes in {resume_dir}...")
    
    resumes = [f for f in os.listdir(resume_dir) if f.lower().endswith('.pdf')]
    
    if not resumes:
        print("No PDF resumes found.")
        return
        
    for filename in resumes:
        filepath = os.path.join(resume_dir, filename)
        print(f"Processing {filename}...")
        
        try:
            # 1. Extract text from PDF
            raw_text = pdf_parser.extract_text(filepath)
            
            # 2. Basic cleaning
            cleaned_text = cleaner.clean(raw_text)
            
            # 3. Process through Education Engine
            # This returns a StructuredAcademicProfile object
            profile = engine.process_education_text(cleaned_text, job_requirements)
            
            # 4. Store the profile (converted to dict for JSON serialization)
            all_profiles[filename] = profile.to_dict()
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            all_profiles[filename] = {"error": str(e)}

    # Save to JSON
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_profiles, f, cls=DateTimeEncoder, indent=2)
        
    print(f"\nSuccessfully generated academic profiles for {len(resumes)} resumes.")
    print(f"Results saved to: {output_path}")

if __name__ == '__main__':
    generate_academic_profiles()
