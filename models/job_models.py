import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SkillRequirement:
    name: str # The skill extracted as-is
    standard_name: str # After synonym mapping
    proficiency: Optional[str] = None # e.g. "Expert", "Beginner", "Lead", or None
    required: bool = True

@dataclass
class ExperienceRequirement:
    min_years: int = 0
    max_years: int = 0
    
@dataclass
class JobRequirementProfile:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_title: str = ""
    standard_role_name: str = ""
    company: str = ""
    location: str = ""
    employment_type: str = "Full-time"
    summary: str = ""
    responsibilities: List[str] = field(default_factory=list)
    experience: ExperienceRequirement = field(default_factory=ExperienceRequirement)
    education: List[str] = field(default_factory=list)
    skills: List[SkillRequirement] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "job_title": self.job_title,
            "standard_role_name": self.standard_role_name,
            "company": self.company,
            "location": self.location,
            "employment_type": self.employment_type,
            "summary": self.summary,
            "responsibilities": self.responsibilities,
            "requirements": {
                "years_of_experience": {
                    "min": self.experience.min_years,
                    "max": self.experience.max_years
                },
                "education": self.education
            },
            "skills_required": [
                {
                    "name": s.name,
                    "standard_name": s.standard_name,
                    "minimum_proficiency": s.proficiency,
                    "required": s.required
                } for s in self.skills if s.required
            ],
            "skills_preferred": [
                {
                    "name": s.name,
                    "standard_name": s.standard_name
                } for s in self.skills if not s.required
            ],
            "benefits": self.benefits,
            "metadata": self.metadata
        }
