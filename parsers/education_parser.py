import re
import logging
from typing import List, Dict, Optional
from utils.synonym_mapper import SynonymMapper

class EducationParser:
    """
    Parser to extract educational qualifications and professional certifications from resume text.
    Handles degree normalization, field of study extraction, and certification categorization.
    """

    DEGREE_PATTERNS = [
        r"\b(Bachelor|Master|Doctor|PhD|B\.?S\.?c?|M\.?S\.?c?|B\.?A\.?|M\.?A\.?|B\.?E\.?|M\.?E\.?|B\.?Tech|M\.?Tech|MBA|BBA)\b",
        r"\b(Diploma|High School)\b",
        r"\b(Associate Degree|Associate's Degree)\b"
    ]

    # Headers to ignore when looking for certs or degrees
    IGNORE_HEADERS = ["EDUCATION", "CERTIFICATIONS", "ACADEMIC PROFILE", "QUALIFICATIONS"]

    INSTITUTION_KEYWORDS = [
        "University", "College", "Institute", "School", "Academy", "Polytechnic", 
        "IIT", "NIT", "BITS", "IIM", "Stanford", "MIT", "Harvard"
    ]

    CERTIFICATION_CATEGORIES = {
        "Cloud": ["AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "Cloud Architect"],
        "Project Management": ["PMP", "Project Management Professional", "Scrum Master", "Agile", "PRINCE2"],
        "Network": ["CCNA", "CCNP", "Cisco", "CompTIA Network+", "Network Engineer"],
        "Security": ["CISSP", "CEH", "CompTIA Security+", "Cybersecurity", "Information Security"],
        "Data & AI": ["TensorFlow", "Data Science", "Machine Learning", "Deep Learning", "Tableau", "Power BI"],
        "Software Development": ["Java Certified", "Oracle Certified", "Python", "Full Stack", "MERN"],
        "General": ["Udacity", "Coursera", "edX", "Pluralsight", "LinkedIn Learning"]
    }

    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.synonym_mapper = SynonymMapper()

    def parse_education_section(self, text: str) -> Dict[str, List[Dict]]:
        """
        Parses educational and certification data from a dedicated section of the resume.
        """
        if not text:
            return {"education": [], "certifications": []}

        education_entries = []
        certification_entries = []
        
        # Split by lines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_edu_entry = None
        
        for i, line in enumerate(lines):
            # 1. Look for Degrees
            degree_match = self._find_degree(line)
            if degree_match:
                if current_edu_entry:
                    education_entries.append(current_edu_entry)
                
                current_edu_entry = {
                    "degree": self.synonym_mapper.normalize_education(degree_match),
                    "raw_degree": degree_match,
                    "institution": "Unknown Institution",
                    "field_of_study": "Not Specified",
                    "end_date": None
                }
                
                # Try to extract institution from the same line or nearby
                self._enrich_education_entry(current_edu_entry, lines, i)
                continue

            # 2. Look for Certifications
            cert_name = self._find_certification(line)
            if cert_name:
                cert_entry = {
                    "name": self.synonym_mapper.normalize_certification(cert_name),
                    "raw_name": cert_name,
                    "issuing_organization": self._extract_issuing_org(line),
                    "issue_date": self._extract_year(line),
                    "category": self._categorize_certification(cert_name)
                }
                certification_entries.append(cert_entry)
                continue

            # 3. If we have a current education entry but haven't filled institution/field yet
            if current_edu_entry:
                if current_edu_entry["institution"] == "Unknown Institution":
                    inst = self._find_institution(line)
                    if inst:
                        current_edu_entry["institution"] = inst
                
                if current_edu_entry["field_of_study"] == "Not Specified":
                    field = self._find_field_of_study(line)
                    if field:
                        current_edu_entry["field_of_study"] = field

                if not current_edu_entry["end_date"]:
                    year = self._extract_year(line)
                    if year:
                        current_edu_entry["end_date"] = f"{year}-01-01"

        if current_edu_entry:
            education_entries.append(current_edu_entry)

        return {
            "education": education_entries,
            "certifications": certification_entries
        }

    def _find_degree(self, line: str) -> Optional[str]:
        if line.upper() in self.IGNORE_HEADERS:
            return None
        for pattern in self.DEGREE_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(0)
        return None

    def _find_institution(self, line: str) -> Optional[str]:
        for keyword in self.INSTITUTION_KEYWORDS:
            if keyword.lower() in line.lower():
                return line
        return None

    def _find_field_of_study(self, line: str) -> Optional[str]:
        # Heuristic: Fields of study often follow "in", "of", or "Major:"
        patterns = [
            r"(?:in|of|Major:)\s+([A-Za-z\s&]{3,})",
            r"\b(Computer Science|Information Technology|Engineering|Business Administration|Economics|Physics|Mathematics|Biology|Artificial Intelligence|Machine Learning)\b"
        ]
        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Prioritize the group if it exists
                field = match.group(1) if match.lastindex and match.lastindex >= 1 else match.group(0)
                if field:
                    # Clean up the field (remove common suffixes that might have been caught)
                    field = re.sub(r'\b(University|College|Institute|at)\b.*', '', field, flags=re.IGNORECASE).strip()
                    return field
        return None

    def _find_certification(self, line: str) -> Optional[str]:
        if line.upper() in self.IGNORE_HEADERS:
            return None
            
        # Certification indicators
        indicators = ["Certified", "Certification", "Certificate", "Credential", "Specialization", "Professional", "Nanodegree"]
        # Also check for known major certifications even without "Certified"
        major_certs = ["PMP", "CCNA", "CCNP", "CISSP", "AWS", "GCP", "Azure"]
        
        line_lower = line.lower()
        
        # Check if line contains indicators or major certs
        has_indicator = any(ind.lower() in line_lower for ind in indicators)
        has_major_cert = any(re.search(r'\b' + re.escape(cert) + r'\b', line, re.IGNORECASE) for cert in major_certs)
        
        if has_indicator or has_major_cert:
            # Avoid matching education keywords
            if not any(edu.lower() in line_lower for edu in self.INSTITUTION_KEYWORDS) and \
               not self._find_degree(line):
                return line
        return None

    def _enrich_education_entry(self, entry: Dict, lines: List[str], current_idx: int):
        # Look at the current line for institution
        inst = self._find_institution(lines[current_idx])
        if inst:
            entry["institution"] = inst
            
        # Look at current line for field
        field = self._find_field_of_study(lines[current_idx])
        if field:
            entry["field_of_study"] = field
            
        # Look at current line for year
        year = self._extract_year(lines[current_idx])
        if year:
            entry["end_date"] = f"{year}-01-01"

    def _extract_year(self, line: str) -> Optional[str]:
        match = re.search(r'\b(19|20)\d{2}\b', line)
        if match:
            return match.group(0)
        return None

    def _extract_issuing_org(self, line: str) -> str:
        orgs = ["Amazon", "Google", "Microsoft", "Cisco", "Oracle", "PMI", "Udacity", "Coursera"]
        for org in orgs:
            if org.lower() in line.lower():
                return org
        return "Unknown"

    def _categorize_certification(self, cert_name: str) -> str:
        cert_name_lower = cert_name.lower()
        for category, keywords in self.CERTIFICATION_CATEGORIES.items():
            if any(keyword.lower() in cert_name_lower for keyword in keywords):
                return category
        return "General"

    def normalize_naming(self, education_data: Dict) -> Dict:
        """
        Ensures all names are normalized using the synonym mapper.
        """
        for edu in education_data.get("education", []):
            edu["degree"] = self.synonym_mapper.normalize_education(edu["degree"])
            
        for cert in education_data.get("certifications", []):
            cert["name"] = self.synonym_mapper.normalize_certification(cert["name"])
            
        return education_data
