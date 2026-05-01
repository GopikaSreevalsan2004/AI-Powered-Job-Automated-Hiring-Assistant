from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class GapOrOverlap:
    role1: str = ""
    role2: str = ""
    duration_months: int = 0
    type: str = "Gap" # "Gap" or "Overlap"

@dataclass
class ExperienceAnalysis:
    total_experience_years: float = 0.0
    gaps: List[Dict] = field(default_factory=list) # e.g. [{"after_role": "X", "before_role": "Y", "gap_months": 3}]
    overlaps: List[Dict] = field(default_factory=list) # e.g. [{"role1": "X", "role2": "Y", "overlap_months": 2}]

@dataclass
class ProfessionalRole:
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: str = ""
    relevance_score: float = 0.0
    start_dt: Optional[datetime] = None
    end_dt: Optional[datetime] = None

@dataclass
class CandidateExperienceProfile:
    """
    This is the Structured Experience Object that acts as the final deliverable.
    It encapsulates the timeline of a candidate's career, scoring against a JD, and gaps/overlaps.
    """
    structured_experiences: List[ProfessionalRole] = field(default_factory=list)
    analysis: ExperienceAnalysis = field(default_factory=ExperienceAnalysis)

    def to_dict(self):
        return {
            "structured_experiences": [
                {
                    "company": exp.company,
                    "role": exp.role,
                    "start_date": exp.start_date,
                    "end_date": exp.end_date,
                    "description": exp.description,
                    "relevance_score": exp.relevance_score
                }
                for exp in self.structured_experiences
            ],
            "analysis": {
                "total_experience_years": self.analysis.total_experience_years,
                "gaps": self.analysis.gaps,
                "overlaps": self.analysis.overlaps
            }
        }
