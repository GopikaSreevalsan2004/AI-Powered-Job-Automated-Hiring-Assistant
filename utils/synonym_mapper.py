import re
import json
import logging
import os

class SynonymMapper:
    """
    A utility class to normalize skill names and role titles into standard formats.
    This helps the AI matching engine map interchangeable terms (e.g., ML -> Machine Learning).
    """

    ROLE_SYNONYMS = {
        "SDE": "Software Engineer",
        "SWE": "Software Engineer",
        "ML Engineer": "Machine Learning Engineer",
        "Data Sci": "Data Scientist",
        "Big Data Eng": "Big Data Engineer",
        "Front end Developer": "Frontend Engineer",
        "Back end Developer": "Backend Engineer",
        "Full stack Developer": "Fullstack Engineer"
    }

    # Fallback in case dictionary file is missing
    FALLBACK_SKILL_SYNONYMS = {
        "ML": "Machine Learning",
        "AI": "Artificial Intelligence",
        "DL": "Deep Learning",
        "NLP": "Natural Language Processing",
        "CV": "Computer Vision",
        "SWE": "Software Engineering",
        "SDE": "Software Development",
        "AWS": "Amazon Web Services",
        "GCP": "Google Cloud Platform",
        "K8S": "Kubernetes",
        "JS": "JavaScript",
        "TS": "TypeScript",
        "PY": "Python",
        "DB": "Database",
        "RDBMS": "Relational Database",
        "NOSQL": "NoSQL",
        "HDFS": "Hadoop Distributed File System",
        "BI": "Business Intelligence",
        "ETL": "Extract, Transform, Load",
        "ELT": "Extract, Load, Transform",
        "CI/CD": "Continuous Integration/Continuous Deployment"
    }

    EDUCATION_SYNONYMS = {
        "BS": "Bachelor of Science",
        "BSC": "Bachelor of Science",
        "B.S.": "Bachelor of Science",
        "B.SC.": "Bachelor of Science",
        "BTECH": "Bachelor of Technology",
        "B.TECH": "Bachelor of Technology",
        "MS": "Master of Science",
        "MSC": "Master of Science",
        "M.S.": "Master of Science",
        "M.SC.": "Master of Science",
        "MTECH": "Master of Technology",
        "M.TECH": "Master of Technology",
        "MBA": "Master of Business Administration",
        "PHD": "Doctor of Philosophy",
        "P.H.D.": "Doctor of Philosophy",
        "BBA": "Bachelor of Business Administration",
        "BA": "Bachelor of Arts",
        "MA": "Master of Arts"
    }

    CERTIFICATION_SYNONYMS = {
        "PMP": "Project Management Professional",
        "AWS CSA": "AWS Certified Solutions Architect",
        "AWS CDA": "AWS Certified Developer Associate",
        "CCNA": "Cisco Certified Network Associate",
        "CCNP": "Cisco Certified Network Professional",
        "GCP": "Google Cloud Professional",
        "AZURE": "Microsoft Azure Certification"
    }

    def __init__(self, dictionary_path: str = "data/skill_dictionary.json"):
        self.skill_synonyms = self.FALLBACK_SKILL_SYNONYMS.copy()
        
        try:
            if os.path.exists(dictionary_path):
                with open(dictionary_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "Synonyms" in data:
                        # Overwrite with external JSON synonyms
                        self.skill_synonyms.update(data["Synonyms"])
            else:
                logging.debug(f"Synonym dictionary not found at {dictionary_path}, using fallback.")
        except Exception as e:
            logging.error(f"Error loading synonym dictionary: {e}")

    def normalize_skill(self, skill: str) -> str:
        """
        Takes an extracted raw skill string and returns its standard alias if one exists.
        """
        upper_skill = skill.strip().upper()
        
        # Exact match of uppercase (common for acronyms)
        if upper_skill in self.skill_synonyms:
            return self.skill_synonyms[upper_skill]
            
        # Exact string match (case-sensitive from dictionary keys)
        if skill.strip() in self.skill_synonyms:
            return self.skill_synonyms[skill.strip()]
            
        # Check standard dictionary with case-insensitivity
        lower_skill = skill.strip().lower()
        for alias, standard in self.skill_synonyms.items():
            if lower_skill == alias.lower():
                return standard
                
        # If no strict match, title-case the cleaned original word
        return skill.strip().title()

    @classmethod
    def normalize_role(cls, role: str) -> str:
        """
        Normalizes role names from JDs to standard internal taxonomy labels.
        """
        role_cleaned = role.strip()
        role_lower = role_cleaned.lower()
        
        for alias, standard in cls.ROLE_SYNONYMS.items():
            if alias.lower() in role_lower:
                return standard
                
        return role_cleaned.title()

    @classmethod
    def normalize_education(cls, degree: str) -> str:
        """
        Normalizes degree names to a standard format.
        """
        degree_clean = degree.strip().upper().replace('.', '')
        return cls.EDUCATION_SYNONYMS.get(degree_clean, degree.strip().title())

    @classmethod
    def normalize_certification(cls, cert: str) -> str:
        """
        Normalizes certification names.
        """
        cert_upper = cert.strip().upper()
        for alias, standard in cls.CERTIFICATION_SYNONYMS.items():
            if alias in cert_upper:
                return standard
        return cert.strip().title()
