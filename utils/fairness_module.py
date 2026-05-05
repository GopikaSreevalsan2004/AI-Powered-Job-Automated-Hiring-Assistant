import re
import hashlib
from typing import Dict, List, Any

class FairnessModule:
    """
    Standardizes resume evaluation to reduce bias and improve fairness.
    Includes anonymization (PII masking) and score normalization logic.
    """
    
    def __init__(self):
        # Patterns to identify potentially biased attributes
        self.pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "name_hint": r'\b(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+[A-Z][a-z]+\b', # Basic title + name
            "address": r'\b\d{1,5}\s+[A-Z][a-z]+\s+(?:St|Ave|Blvd|Rd|Dr|Ln)\b',
        }

    def anonymize_text(self, text: str) -> str:
        """Masks non-essential personal attributes from the raw text."""
        if not text:
            return ""
            
        anonymized = text
        for attr, pattern in self.pii_patterns.items():
            anonymized = re.sub(pattern, f"[MASKED_{attr.upper()}]", anonymized)
            
        return anonymized

    def anonymize_candidate_name(self, filename: str) -> str:
        """Converts a filename with a name into a standardized candidate ID."""
        # Use a hash to keep it consistent but anonymous
        hash_id = hashlib.md5(filename.encode()).hexdigest()[:8].upper()
        return f"CANDIDATE-{hash_id}"

    def normalize_scores(self, raw_scores: List[float]) -> List[float]:
        """
        Normalizes scores to a 0-1 range based on the current pool's distribution.
        This prevents 'hard-grading' bias where no one gets shortlisted.
        """
        if not raw_scores:
            return []
            
        min_s = min(raw_scores)
        max_s = max(raw_scores)
        
        if max_s == min_s:
            return [0.5] * len(raw_scores) # Neutral if all are same
            
        return [(s - min_s) / (max_s - min_s) for s in raw_scores]

    def check_bias_indicators(self, resume_text: str) -> Dict[str, Any]:
        """
        Identifies potential bias-triggering keywords (e.g. gendered language, 
        age indicators) to flag for recruiter awareness.
        """
        gendered_terms = ['chairman', 'waitress', 'fireman', 'stewardess', 'freshman']
        age_indicators = ['retired', 'senior citizen', 'student', 'youth', 'experienced professional for 30 years']
        
        found_gendered = [t for t in gendered_terms if t in resume_text.lower()]
        found_age = [t for t in age_indicators if t in resume_text.lower()]
        
        return {
            "has_gendered_language": len(found_gendered) > 0,
            "gendered_terms": found_gendered,
            "has_age_indicators": len(found_age) > 0,
            "age_terms": found_age,
            "recommendation": "Review for gender-neutral language and age-agnostic descriptions." if found_gendered or found_age else "Neutral language detected."
        }
