from typing import List, Dict, Optional
try:
    from fuzzywuzzy import fuzz
except ImportError:
    # Fallback if fuzzywuzzy is not available
    class Fuzz:
        @staticmethod
        def token_set_ratio(s1, s2):
            return 100 if s1.lower() == s2.lower() else 50
    fuzz = Fuzz()

class EducationScorer:
    """
    Evaluates the relevance of a candidate's academic background and professional 
    certifications against specific job requirements.
    """
    
    DEGREE_HIERARCHY = {
        "Doctor of Philosophy": 5,
        "Master of Science": 4,
        "Master of Technology": 4,
        "Master of Business Administration": 4,
        "Master of Arts": 4,
        "Bachelor of Technology": 3,
        "Bachelor of Science": 3,
        "Bachelor of Engineering": 3,
        "Bachelor of Arts": 2,
        "Diploma": 1,
        "Associate": 1,
        "High School": 0
    }

    def __init__(self):
        # Weights for the overall education score
        self.degree_level_weight = 0.4
        self.field_relevance_weight = 0.5
        self.institution_prestige_weight = 0.1 # Placeholder for future logic

    def calculate_total_academic_score(self, education_data: Dict, job_requirements: Dict) -> float:
        """
        Computes a comprehensive score for a candidate's academic profile.
        """
        education_list = education_data.get("education", [])
        cert_list = education_data.get("certifications", [])
        
        edu_score = self.score_education_relevance(education_list, job_requirements)
        cert_score = self.score_certification_relevance(cert_list, job_requirements)
        
        # Education typically carries more weight than certifications for entry/mid level,
        # but certs are very important for specialized roles.
        total_score = (edu_score * 0.7) + (cert_score * 0.3)
        return round(total_score, 2)

    def score_education_relevance(self, education_list: List[Dict], job_requirements: Dict) -> float:
        """
        Scores the best educational entry against job requirements.
        """
        if not education_list:
            return 0.0

        target_degree = job_requirements.get("minimum_education", "Bachelor of Science")
        target_field = job_requirements.get("target_field", "").lower()
        
        best_score = 0.0
        
        for edu in education_list:
            # 1. Degree Level match
            level_score = self._get_degree_level_score(edu.get("degree", ""), target_degree)
            
            # 2. Field of Study match
            field_score = self._get_field_score(edu.get("field_of_study", ""), target_field)
            
            # Entry score
            current_score = (level_score * 0.4) + (field_score * 0.6)
            if current_score > best_score:
                best_score = current_score
                
        return best_score

    def score_certification_relevance(self, cert_list: List[Dict], job_requirements: Dict) -> float:
        """
        Scores certifications based on relevance categories and job keywords.
        """
        if not cert_list:
            return 0.0
            
        preferred_categories = job_requirements.get("preferred_cert_categories", [])
        required_keywords = job_requirements.get("required_cert_keywords", [])
        
        if not preferred_categories and not required_keywords:
            # Generic boost for having any professional certifications
            return min(len(cert_list) * 0.2, 0.5)
            
        score = 0.0
        for cert in cert_list:
            cert_score = 0.0
            # Category match
            if cert.get("category") in preferred_categories:
                cert_score += 0.6
                
            # Keyword match
            cert_name = cert.get("name", "").lower()
            for kw in required_keywords:
                if kw.lower() in cert_name:
                    cert_score += 0.4
                    break
            
            score = max(score, cert_score)
            
        return min(score, 1.0)

    def _get_degree_level_score(self, cand_degree: str, target_degree: str) -> float:
        cand_val = self.DEGREE_HIERARCHY.get(cand_degree, 1)
        target_val = self.DEGREE_HIERARCHY.get(target_degree, 3) # Default to Bachelor
        
        if cand_val >= target_val:
            return 1.0
        return cand_val / target_val

    def _get_field_score(self, cand_field: str, target_field: str) -> float:
        if not target_field:
            return 0.5 # Neutral if job doesn't specify field
        if not cand_field or cand_field == "Not Specified":
            return 0.0
            
        # Use fuzzy matching for fields (e.g. "Computer Science" vs "Software Engineering")
        similarity = fuzz.token_set_ratio(cand_field.lower(), target_field.lower()) / 100.0
        return similarity
