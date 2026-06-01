from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl, Field
from datetime import date
from enum import Enum

class ProficiencyLevel(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"
    LEAD = "Lead"

class SkillCategory(str, Enum):
    TECHNICAL = "Technical"
    SOFT = "Soft"
    TOOL = "Tool"
    DOMAIN = "Domain Knowledge"

class LanguageProficiency(str, Enum):
    NATIVE = "Native"
    FLUENT = "Fluent"
    CONVERSATIONAL = "Conversational"
    BASIC = "Basic"

class EmploymentType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"

class ContactInfo(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[HttpUrl] = None
    github: Optional[HttpUrl] = None
    portfolio: Optional[HttpUrl] = None

class Experience(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    key_achievements: List[str] = []
    skills_used: List[str] = []

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    gpa: Optional[str] = None

class Skill(BaseModel):
    name: str
    level: Optional[ProficiencyLevel] = None
    category: Optional[SkillCategory] = None

class Certification(BaseModel):
    name: str
    issuing_organization: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    credential_id: Optional[str] = None

class Language(BaseModel):
    language: str
    proficiency: LanguageProficiency

class Project(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[HttpUrl] = None
    technologies: List[str] = []

class ResumeSchema(BaseModel):
    candidate_id: Optional[str] = None
    full_name: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    experiences: List[Experience]
    education: List[Education]
    skills: List[Skill]
    certifications: List[Certification] = []
    languages: List[Language] = []
    projects: List[Project] = []

class ExperienceRequirement(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None

class JobRequirements(BaseModel):
    years_of_experience: Optional[ExperienceRequirement] = None
    education: List[str] = []

class SkillRequirement(BaseModel):
    name: str
    minimum_proficiency: Optional[ProficiencyLevel] = None

class JobDescriptionSchema(BaseModel):
    job_id: Optional[str] = None
    job_title: str
    company: str
    location: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    summary: Optional[str] = None
    responsibilities: List[str]
    requirements: Optional[JobRequirements] = None
    skills_required: List[SkillRequirement]
    skills_preferred: List[Dict[str, str]] = []
    benefits: List[str] = []
    metadata: Dict[str, Any] = {}

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str
    check_status_url: str

class ScoringRequest(BaseModel):
    resume_data: ResumeSchema
    jd_data: JobDescriptionSchema
    weights: Optional[Dict[str, float]] = None

class ScoringByJDRequest(BaseModel):
    resume_data: ResumeSchema
    jd_filename: str = Field(..., description="Filename of the JD in output/jd files/ folder")
    weights: Optional[Dict[str, float]] = None

class ScoreBreakdown(BaseModel):
    skill_score: float = Field(..., alias="skill_extraction_final_score")
    experience_score: float = Field(..., alias="experience_extraction_final_score")
    education_score: float = Field(..., alias="education_extraction_final_score")
    semantic_similarity: Optional[float] = None

    class Config:
        populate_by_name = True

class ScoringResponse(BaseModel):
    match_score: float
    is_shortlisted: bool
    status_zone: str
    breakdown: ScoreBreakdown
    missing_critical_skills: List[str]
    recommendation: str

class ShortlistRequest(BaseModel):
    jd_data: JobDescriptionSchema
    resumes: List[ResumeSchema]

class ShortlistedCandidate(BaseModel):
    candidate_name: str
    rank: int
    score: float
    highlights: List[str]

class ShortlistResponse(BaseModel):
    job_title: str
    top_candidates: List[ShortlistedCandidate]
