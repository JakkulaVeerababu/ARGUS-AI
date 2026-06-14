from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Profile(BaseModel):
    anonymized_name: str
    headline: str
    summary: str
    location: str
    country: str
    years_of_experience: float = Field(..., ge=0, le=50)
    current_title: str
    current_company: str
    current_company_size: str
    current_industry: str

class CareerJob(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None
    duration_months: int = Field(..., ge=0)
    is_current: bool
    industry: str
    company_size: str
    description: str

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_year: int = Field(..., ge=1970, le=2030)
    end_year: int = Field(..., ge=1970, le=2035)
    grade: Optional[str] = None
    tier: str = Field(..., enum=["tier_1", "tier_2", "tier_3", "tier_4", "unknown"])

class Skill(BaseModel):
    name: str
    proficiency: str = Field(..., enum=["beginner", "intermediate", "advanced", "expert"])
    endorsements: int = Field(..., ge=0)
    duration_months: int = Field(..., ge=0)

class Certification(BaseModel):
    name: str
    issuer: str
    year: int

class Language(BaseModel):
    language: str
    proficiency: str = Field(..., enum=["basic", "conversational", "professional", "native"])

class SalaryRange(BaseModel):
    min: float = Field(..., ge=0)
    max: float = Field(..., ge=0)

class RedrobSignals(BaseModel):
    profile_completeness_score: float = Field(..., ge=0, le=100)
    signup_date: str
    last_active_date: str
    open_to_work_flag: bool
    profile_views_received_30d: int = Field(..., ge=0)
    applications_submitted_30d: int = Field(..., ge=0)
    recruiter_response_rate: float = Field(..., ge=0, le=1)
    avg_response_time_hours: float = Field(..., ge=0)
    skill_assessment_scores: Dict[str, float]
    connection_count: int = Field(..., ge=0)
    endorsements_received: int = Field(..., ge=0)
    notice_period_days: int = Field(..., ge=0, le=180)
    expected_salary_range_inr_lpa: SalaryRange
    preferred_work_mode: str = Field(..., enum=["remote", "hybrid", "onsite", "flexible"])
    willing_to_relocate: bool
    github_activity_score: float = Field(..., ge=-1, le=100)
    search_appearance_30d: int = Field(..., ge=0)
    saved_by_recruiters_30d: int = Field(..., ge=0)
    interview_completion_rate: float = Field(..., ge=0, le=1)
    offer_acceptance_rate: float = Field(..., ge=-1, le=1)
    verified_email: bool
    verified_phone: bool
    linkedin_connected: bool

class Candidate(BaseModel):
    candidate_id: str = Field(..., pattern=r"^CAND_[0-9]{7}$")
    profile: Profile
    career_history: List[CareerJob]
    education: List[Education]
    skills: List[Skill]
    certifications: Optional[List[Certification]] = []
    languages: Optional[List[Language]] = []
    redrob_signals: RedrobSignals
