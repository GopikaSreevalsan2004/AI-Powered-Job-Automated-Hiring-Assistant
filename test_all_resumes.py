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

def test_all():
    engine = ExperienceEngine()
    pdf_parser = PDFParser()
    cleaner = TextCleaner()
    
    resume_dir = 'data/resumes'
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
        print(f"--- {filename} ---")
        print(f"Roles found: {len(results['structured_experiences'])}")
        print(f"Total Experience: {results['analysis']['total_experience_years']} years")
        for exp in results['structured_experiences']:
            print(f"  - {exp.get('role')} at {exp.get('company')} ({exp.get('start_date')} to {exp.get('end_date')}) - Score: {exp.get('relevance_score')}")
        print()

if __name__ == '__main__':
    test_all()
