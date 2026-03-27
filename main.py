import os
import sys
from utils.logger import setup_logger
from utils.text_cleaner import TextCleaner
from utils.file_handler import FileHandler
from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DOCXParser

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
        logger.info(f"Successfully processed and saved to: {output_path}")

    logger.info("Resume extraction process completed.")

if __name__ == "__main__":
    main()
