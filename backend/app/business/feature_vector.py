"""
Purpose: Defines the structured representation of candidate scoring feature vectors.
Inputs: None (schema definition).
Outputs: CandidateFeatureVector Pydantic model.
Complexity: O(1) definition.
Production Concerns: Strict validation checks; default initializers for missing fields.
Future Improvements: Add feature metadata description parameters for transparency.
"""
from pydantic import BaseModel, Field

class CandidateFeatureVector(BaseModel):
    cross_encoder: float = Field(..., description="Normalized semantic Cross-Encoder score (Sigmoid applied)")
    experience: float = Field(..., description="Gaussian experience matching score [0, 1]")
    location: float = Field(..., description="Location match score [0, 1]")
    title: float = Field(..., description="Title semantic matching score [0, 1]")
    skills: float = Field(..., description="Weighted skill overlap score [0, 1]")
    company: float = Field(..., description="Company boost factor [1.0, 1.10]")
    notice: float = Field(..., description="Notice period decay score [0, 1]")
    engagement: float = Field(..., description="Normalized candidate activity and engagement index [0, 1]")
