import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.education_parser import EducationParser
from scoring.education_scorer import EducationScorer

def test_education_extraction():
    parser = EducationParser()
    
    resume_text = """
    EDUCATION
    Bachelor of Science in Computer Science
    Stanford University, 2018 - 2022
    GPA: 3.8/4.0
    
    Master of Technology in Artificial Intelligence
    IIT Bombay, 2022 - 2024
    
    CERTIFICATIONS
    AWS Certified Solutions Architect - Associate
    PMP Certification from Project Management Institute
    Deep Learning Specialization by Coursera
    """
    
    results = parser.parse_education_section(resume_text)
    
    print("\n--- Extracted Education ---")
    for edu in results['education']:
        print(f"Degree: {edu['degree']} | Institution: {edu['institution']} | Field: {edu['field_of_study']} | Year: {edu['end_date']}")
    
    print("\n--- Extracted Certifications ---")
    for cert in results['certifications']:
        print(f"Name: {cert['name']} | Category: {cert['category']} | Org: {cert['issuing_organization']}")
    
    assert len(results['education']) >= 2
    assert any("Bachelor" in e['degree'] for e in results['education'])
    assert any("Master" in e['degree'] for e in results['education'])
    assert len(results['certifications']) >= 2

def test_education_scoring():
    scorer = EducationScorer()
    
    education_data = {
        "education": [
            {"degree": "Bachelor of Science", "field_of_study": "Computer Science"},
            {"degree": "Master of Technology", "field_of_study": "Artificial Intelligence"}
        ],
        "certifications": [
            {"name": "AWS Certified Solutions Architect", "category": "Cloud"},
            {"name": "PMP", "category": "Project Management"}
        ]
    }
    
    job_reqs = {
        "minimum_education": "Master of Science",
        "target_field": "Computer Science",
        "preferred_cert_categories": ["Cloud"],
        "required_cert_keywords": ["AWS"]
    }
    
    edu_score = scorer.score_education_relevance(education_data['education'], job_reqs)
    cert_score = scorer.score_certification_relevance(education_data['certifications'], job_reqs)
    total_score = scorer.calculate_total_academic_score(education_data, job_reqs)
    
    print(f"\n--- Scoring Results ---")
    print(f"Education Relevance Score: {edu_score}")
    print(f"Certification Relevance Score: {cert_score}")
    print(f"Total Academic Score: {total_score}")
    
    assert edu_score >= 0.8 # Master level and CS-related field
    assert cert_score == 1.0 # AWS match both category and keyword

if __name__ == "__main__":
    try:
        test_education_extraction()
        test_education_scoring()
        print("\nAll tests passed!")
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
