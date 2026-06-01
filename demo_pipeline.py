import os
import json
from parsers.pdf_parser import PDFParser
from parsers.jd_parser import JDParser
from ats_engine.master_scorer import MasterScorer
from ats_engine.shortlisting_engine import ShortlistingEngine
from utils.text_cleaner import TextCleaner
from parsers.resume_classifier import ResumeSectionClassifier
from ats_engine.skill_extractor import SkillExtractionEngine
from ats_engine.experience_engine import ExperienceEngine
from ats_engine.education_engine import EducationEngine
from ats_engine.semantic_engine import SemanticEngine

import sys

# Force UTF-8 encoding for stdout to handle emojis on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def run_demo():
    print("Starting ATS Production-Grade Demo...")
    
    # 1. Setup Components
    pdf_parser = PDFParser()
    jd_parser = JDParser()
    cleaner = TextCleaner()
    section_classifier = ResumeSectionClassifier()
    skill_extractor = SkillExtractionEngine()
    exp_engine = ExperienceEngine()
    edu_engine = EducationEngine()
    sem_engine = SemanticEngine()
    master_scorer = MasterScorer()
    shortlisting_engine = ShortlistingEngine()

    # 2. Load Demo JD
    demo_jd_text = """
    Software Developer (Python/AI)
    
    About the Role:
    Building AI-driven applications using Python and modern data tools.
    
    Required Skills:
    - Python
    - Machine Learning
    - Pandas
    - NumPy
    - Java
    - Hadoop
    
    Qualifications:
    - 2+ years of experience.
    - Bachelor's degree in Computer Science.
    """
    print("\nParsing Job Description...")
    jd_profile = jd_parser.parse(demo_jd_text, filename="Python_AI_Dev_JD.txt")
    jd_data = jd_profile.to_dict()
    print(f"JD Parsed: {jd_data['job_title']} (Experience needed: {jd_data['requirements']['years_of_experience']['min']} years)")

    # 3. Load Demo Resumes
    resumes_dir = "data/resumes"
    # Select Resume1 (Data/AI) and Resume_3 (Data Engineer)
    resume_files = ["Resume1.pdf", "Resume_3_Li_Wei.pdf"]
    
    candidate_scores = {}

    for resume_file in resume_files:
        file_path = os.path.join(resumes_dir, resume_file)
        if not os.path.exists(file_path): continue
        name = os.path.splitext(resume_file)[0]
        print(f"\nProcessing Candidate: {name}...")

        # A. Raw Extraction
        raw_text = pdf_parser.extract_text(file_path)
        cleaned_text = cleaner.clean(raw_text)
        
        # B. Parsing Dimensions
        # Skills
        extracted_skills = skill_extractor.extract_skills(cleaned_text)
        
        # Experience
        sections = section_classifier.classify_lines(cleaned_text)
        exp_text = next((s["text"] for s in sections if s["label"] == "Experience"), "")
        exp_data = exp_engine.process_experience_text(exp_text, {"target_role": jd_data["job_title"]})
        
        # Education
        edu_text = next((s["text"] for s in sections if s["label"] == "Education"), "")
        edu_profile = edu_engine.process_education_text(edu_text, {
            "minimum_education": "Bachelor of Science",
            "target_field": "Computer Science"
        })
        edu_data = edu_profile.to_dict()
        
        # Semantic
        sem_data = sem_engine.calculate_similarity(
            resume_data={
                "skills": extracted_skills, 
                "structured_experiences": exp_data.get("structured_experiences", [])
            },
            jd_data=jd_data
        )

        # C. Master Scoring
        scoring_out = master_scorer.calculate_candidate_score(
            skills_data=extracted_skills,
            experience_data=exp_data,
            education_data=edu_data,
            semantic_data=sem_data,
            jd_requirements={"required_skills": [s["name"] for s in jd_data["skills_required"]]}
        )
        
        # D. Add Explanation
        scoring_out["explanation"] = master_scorer.generate_explanation_text(scoring_out)
        candidate_scores[name] = scoring_out
        
        print(f"Score for {name}: {scoring_out['final_score']*100:.1f}% - {scoring_out['status']}")

    # 4. Bulk Shortlisting
    print("\nGenerating Shortlisting Rankings...")
    shortlisting_results = shortlisting_engine.process_rankings(candidate_scores)
    markdown_report = shortlisting_engine.generate_markdown_summary(shortlisting_results)
    
    print("\n--- FINAL REPORT ---")
    # Wrap print to handle potential unicode in report
    try:
        print(markdown_report)
    except UnicodeEncodeError:
        print(markdown_report.encode('ascii', 'ignore').decode('ascii'))

    # Save to a report file
    with open("demo_evaluation_report.md", "w", encoding='utf-8') as f:
        f.write(markdown_report)
    
    print("\nDemo completed. Report saved to 'demo_evaluation_report.md'.")

if __name__ == "__main__":
    run_demo()
