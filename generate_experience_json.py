import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.abspath('.'))

from parsers.pdf_parser import PDFParser
from utils.text_cleaner import TextCleaner
from ats_engine.experience_engine import ExperienceEngine

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return super().default(obj)

def generate_json():
    engine = ExperienceEngine()
    pdf_parser = PDFParser()
    cleaner = TextCleaner()
    
    resume_dir = 'data/resumes'
    output_data = {}
    
    for filename in os.listdir(resume_dir):
        if not filename.endswith('.pdf'):
            continue
        filepath = os.path.join(resume_dir, filename)
        raw_text = pdf_parser.extract_text(filepath)
        cleaned_text = cleaner.clean(raw_text)
        
        job_requirements = {
            "target_role": "Data Engineer",
            "required_skills": ["Python", "Machine Learning", "Data", "AWS", "Big Data"]
        }
        
        results = engine.process_experience_text(cleaned_text, job_requirements)
        output_data[filename] = results
        
    output_path = 'data/processed/structured_experiences.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, cls=DateTimeEncoder, indent=2)
    print(f"Saved to {output_path}")

if __name__ == '__main__':
    generate_json()
