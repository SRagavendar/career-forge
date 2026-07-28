"""Pydantic models for CV, Job Descriptions, and Evaluations"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime


class Experience(BaseModel):
    """Work experience entry"""
    company: str
    title: str
    start_date: str  # Format: "2023-01"
    end_date: Optional[str] = None
    current: bool = False
    achievements: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Anthropic",
                "title": "Senior AI Engineer",
                "start_date": "2023-01",
                "end_date": None,
                "current": True,
                "achievements": ["Led Claude research", "5x performance improvement"]
            }
        }


class Skills(BaseModel):
    """User skills"""
    technical: List[str] = []
    soft: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "technical": ["Python", "Transformers", "PyTorch"],
                "soft": ["Leadership", "Communication"]
            }
        }


class CV(BaseModel):
    """Complete CV data"""
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    experience: List[Experience] = []
    skills: Skills = Field(default_factory=Skills)
    education: List[str] = []
    certifications: List[str] = []

    def to_markdown(self) -> str:
        """Convert CV to markdown for context passing to LLM"""
        lines = [
            f"# {self.name}",
            f"**Email:** {self.email}"
        ]
        
        if self.phone:
            lines.append(f"**Phone:** {self.phone}")
        if self.location:
            lines.append(f"**Location:** {self.location}")
        
        if self.summary:
            lines.append(f"\n## Summary\n{self.summary}")
        
        if self.experience:
            lines.append("\n## Experience")
            for exp in self.experience:
                lines.append(f"### {exp.title} @ {exp.company}")
                end = exp.end_date or "Present"
                lines.append(f"*{exp.start_date} - {end}*")
                for achievement in exp.achievements:
                    lines.append(f"- {achievement}")
                lines.append("")
        
        if self.skills.technical or self.skills.soft:
            lines.append("## Skills")
            if self.skills.technical:
                lines.append("**Technical:** " + ", ".join(self.skills.technical))
            if self.skills.soft:
                lines.append("**Soft Skills:** " + ", ".join(self.skills.soft))
        
        if self.education:
            lines.append("\n## Education")
            for edu in self.education:
                lines.append(f"- {edu}")
        
        if self.certifications:
            lines.append("\n## Certifications")
            for cert in self.certifications:
                lines.append(f"- {cert}")
        
        return "\n".join(lines)


class SeniorityLevel(str, Enum):
    """Job seniority levels"""
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    STAFF = "staff"
    DIRECTOR = "director"
    UNKNOWN = "unknown"


class JobDescription(BaseModel):
    """Job posting data"""
    title: str
    company: str
    url: Optional[str] = None
    description: str
    requirements: List[str] = []
    nice_to_have: List[str] = []
    level: SeniorityLevel = SeniorityLevel.UNKNOWN
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "USD"
    location: str = "Unknown"
    remote: bool = False
    sponsor_visa: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior AI Engineer",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "remote": True,
                "salary_min": 180000,
                "salary_max": 220000,
                "level": "senior",
                "sponsor_visa": True
            }
        }


class EvaluationScore(BaseModel):
    """Individual evaluation scores"""
    role_match: float = Field(..., ge=1.0, le=5.0)
    cv_match: float = Field(..., ge=1.0, le=5.0)
    level_fit: float = Field(..., ge=1.0, le=5.0)
    comp_research: float = Field(..., ge=1.0, le=5.0)
    personalization: float = Field(..., ge=1.0, le=5.0)
    interview_prep: float = Field(..., ge=1.0, le=5.0)

    @property
    def composite(self) -> float:
        """Weighted composite score (1-5)"""
        weights = {
            'role_match': 0.2,
            'cv_match': 0.2,
            'level_fit': 0.15,
            'comp_research': 0.15,
            'personalization': 0.15,
            'interview_prep': 0.15
        }
        total = sum(getattr(self, k) * w for k, w in weights.items())
        return round(total, 2)


class Evaluation(BaseModel):
    """Complete job evaluation"""
    job_id: Optional[str] = None
    company: str
    title: str
    url: Optional[str] = None
    scores: EvaluationScore
    role_summary: str
    cv_match_analysis: str
    level_strategy: str
    comp_insights: str
    tailoring_suggestions: str
    interview_tips: str
    recommendation: str  # "Strong Fit", "Good Fit", "Consider", "Pass"
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "company": "Anthropic",
                "title": "Senior AI Engineer",
                "scores": {
                    "role_match": 4.5,
                    "cv_match": 4.2,
                    "level_fit": 4.0,
                    "comp_research": 4.3,
                    "personalization": 4.1,
                    "interview_prep": 4.0
                },
                "recommendation": "Strong Fit"
            }
        }
