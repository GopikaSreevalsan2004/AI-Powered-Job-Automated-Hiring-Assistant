import os
import sys
import json
from utils.logger import setup_logger
from utils.text_cleaner import TextCleaner
from utils.file_handler import FileHandler
from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DOCXParser
from ats_engine.skill_extractor import SkillExtractionEngine
from ats_engine.experience_engine import ExperienceEngine
from parsers.resume_classifier import ResumeSectionClassifier

def main():
    # 1. Setup Logging
    logger = setup_logger("extraction_engine", log_file="extraction.log")
    logger.info("Starting Resume Text Extraction Engine...")

    # 2. Configuration
    RESUMES_DIR = "data/resumes"
    PROCESSED_DIR = "data/processed"
    
    # 3. Initialize Components
    file_handler = FileHandler(RESUMES_DIR, PROCESSED_DIR)
    pdf_parser = PDFParser(logger=logger)
    docx_parser = DOCXParser(logger=logger)
    cleaner = TextCleaner()
    skill_extractor = SkillExtractionEngine(logger=logger)
    experience_engine = ExperienceEngine()
    section_classifier = ResumeSectionClassifier()

    # 4. Get Resume Files
    resume_files = file_handler.list_resumes()
    if not resume_files:
        logger.warning(f"No resume files found in {RESUMES_DIR}")
        return

    logger.info(f"Found {len(resume_files)} resumes to process.")

    # 5. Process Each File
    for file_path in resume_files:
        logger.info(f"Processing: {os.path.basename(file_path)}")
        
        # Determine Parser
        ext = os.path.splitext(file_path)[1].lower()
        raw_text = ""
        if ext == '.pdf':
            raw_text = pdf_parser.extract_text(file_path)
        elif ext == '.docx':
            raw_text = docx_parser.extract_text(file_path)
        
        if not raw_text:
            logger.error(f"Failed to extract text from: {file_path}")
            continue

        # Clean Text
        cleaned_text = cleaner.clean(raw_text)
        cleaned_text = cleaner.standardize_headings(cleaned_text)
        
        # Save Output
        output_path = file_handler.save_processed(file_path, cleaned_text)
        
        # Extract and Save Skills
        extracted_skills = skill_extractor.extract_skills(cleaned_text)
        skills_output_path = os.path.splitext(output_path)[0] + "_skills.json"
        with open(skills_output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_skills, f, indent=2)
            
        # Extract and Analyze Experience
        sections = section_classifier.classify_lines(cleaned_text)
        experience_text = ""
        for section in sections:
            if section["label"] == "Experience":
                experience_text = section["text"]
                break
        
        if experience_text:
            # Example requirements for scoring
            dummy_requirements = {
                "target_role": "Software Engineer",
                "required_skills": [s["name"] for s in extracted_skills[:5]] if extracted_skills else []
            }
            exp_results = experience_engine.process_experience_text(experience_text, dummy_requirements)
            
            # Custom JSON serialization for datetime objects in experience results
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if hasattr(obj, 'isoformat'):
                        return obj.isoformat()
                    return super().default(obj)

            exp_output_path = os.path.splitext(output_path)[0] + "_experience.json"
            with open(exp_output_path, 'w', encoding='utf-8') as f:
                json.dump(exp_results, f, indent=2, cls=DateTimeEncoder)
            
            logger.info(f"Successfully processed experience and saved to {exp_output_path}")

        logger.info(f"Successfully processed and saved text to {output_path} and skills to {skills_output_path}")

    logger.info("Resume extraction process completed.")

if __name__ == "__main__":
    main()
