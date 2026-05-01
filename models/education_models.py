from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class EducationEntry:
    degree: str
    raw_degree: str
    institution: str
    field_of_study: str
    end_date: Optional[str] = None

@dataclass
class CertificationEntry:
    name: str
    raw_name: str
    category: str
    issuing_organization: str = "Unknown"
    issue_date: Optional[str] = None

@dataclass
class AcademicScoring:
    total_academic_score: float = 0.0
    education_score: float = 0.0
    certification_score: float = 0.0

@dataclass
class StructuredAcademicProfile:
    """
    This is the Structured Academic Profile that acts as the final deliverable.
    It encapsulates a candidate's formal education, certifications, and relevance scores.
    """
    education: List[EducationEntry] = field(default_factory=list)
    certifications: List[CertificationEntry] = field(default_factory=list)
    relevance_scoring: AcademicScoring = field(default_factory=AcademicScoring)

    def to_dict(self):
        return {
            "education": [
                {
                    "degree": edu.degree,
                    "raw_degree": edu.raw_degree,
                    "institution": edu.institution,
                    "field_of_study": edu.field_of_study,
                    "end_date": edu.end_date
                }
                for edu in self.education
            ],
            "certifications": [
                {
                    "name": cert.name,
                    "raw_name": cert.raw_name,
                    "category": cert.category,
                    "issuing_organization": cert.issuing_organization,
                    "issue_date": cert.issue_date
                }
                for cert in self.certifications
            ],
            "relevance_scoring": {
                "total_academic_score": self.relevance_scoring.total_academic_score,
                "education_score": self.relevance_scoring.education_score,
                "certification_score": self.relevance_scoring.certification_score
            }
        }
