from typing import Dict, Any
from parsers.education_parser import EducationParser
from scoring.education_scorer import EducationScorer
from parsers.resume_classifier import ResumeSectionClassifier
from utils.text_cleaner import TextCleaner
from models.education_models import (
    StructuredAcademicProfile,
    EducationEntry,
    CertificationEntry,
    AcademicScoring
)

class EducationEngine:
    """
    Coordinates the parsing, standardization, and scoring of candidate education and certifications.
    Acts as the primary interface for extracting academic profiles from resume text.
    """
    def __init__(self):
        self.parser = EducationParser()
        self.scorer = EducationScorer()

    def process_education_text(self, text: str, job_requirements: Dict = None) -> StructuredAcademicProfile:
        """
        Full pipeline: Classify -> Parse -> Normalize -> Score
        """
        # 1. Isolate Education and Certification Sections
        classifier = ResumeSectionClassifier()
        # Clean text
        text = TextCleaner.standardize_headings(text)
        sections = classifier.classify_lines(text)
        
        education_text = ""
        certification_text = ""
        
        for sec in sections:
            if sec["label"] == "Education":
                education_text += sec["text"] + "\n"
            elif sec["label"] == "Certifications":
                certification_text += sec["text"] + "\n"
                
        # If classifier failed to find sections, fallback to parsing full text
        combined_text = education_text + certification_text
        if not combined_text.strip():
            combined_text = text

        # 2. Parse into structured data
        raw_academic_data = self.parser.parse_education_section(combined_text)
        
        # 3. Normalize naming conventions
        normalized_data = self.parser.normalize_naming(raw_academic_data)
        
        # Build Typed Objects
        edu_entries = [
            EducationEntry(
                degree=edu.get("degree", ""),
                raw_degree=edu.get("raw_degree", ""),
                institution=edu.get("institution", ""),
                field_of_study=edu.get("field_of_study", ""),
                end_date=edu.get("end_date")
            )
            for edu in normalized_data.get("education", [])
        ]
        
        cert_entries = [
            CertificationEntry(
                name=cert.get("name", ""),
                raw_name=cert.get("raw_name", ""),
                category=cert.get("category", "General"),
                issuing_organization=cert.get("issuing_organization", "Unknown"),
                issue_date=cert.get("issue_date")
            )
            for cert in normalized_data.get("certifications", [])
        ]
        
        scoring_obj = AcademicScoring()
        
        # 4. Score relevance logic (if job requirements are provided)
        if job_requirements:
            scoring_obj = AcademicScoring(
                total_academic_score=self.scorer.calculate_total_academic_score(normalized_data, job_requirements),
                education_score=self.scorer.score_education_relevance(normalized_data.get("education", []), job_requirements),
                certification_score=self.scorer.score_certification_relevance(normalized_data.get("certifications", []), job_requirements)
            )
            
        profile = StructuredAcademicProfile(
            education=edu_entries,
            certifications=cert_entries,
            relevance_scoring=scoring_obj
        )
        
        return profile
