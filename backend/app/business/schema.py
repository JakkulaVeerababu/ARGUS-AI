"""
Purpose: Defines the structure of target requirements parsed dynamically from Job Descriptions.
Inputs: None (schema definition).
Outputs: JDRequirementsSchema Pydantic model.
Complexity: O(1) representation.
Production Concerns: Strict validation; must handle missing fields gracefully with defaults.
Future Improvements: Add custom pydantic validators to sanitize inputs (e.g. converting negative experience values to absolute numbers).
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class ExperienceRequirement(BaseModel):
    min_years: Optional[float] = Field(default=None, description="Minimum years of experience required")
    max_years: Optional[float] = Field(default=None, description="Maximum preferred years of experience")

class JDRequirementsSchema(BaseModel):
    must_have_skills: List[str] = Field(default_factory=list, description="Mandatory technical skills")
    nice_to_have_skills: List[str] = Field(default_factory=list, description="Nice-to-have or optional skills")
    experience: ExperienceRequirement = Field(default_factory=ExperienceRequirement, description="Target experience parameters")
    locations: List[str] = Field(default_factory=list, description="Target cities or regions")
    titles: List[str] = Field(default_factory=list, description="Target job titles")
    companies: List[str] = Field(default_factory=list, description="Preferred companies")
