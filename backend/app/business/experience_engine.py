"""
Purpose: Computes candidate experience match score based on parsed min/max requirements using Gaussian decay curves.
Inputs:
    - candidate_experience: float
    - min_years: Optional[float]
    - max_years: Optional[float]
Outputs:
    - float score in range [0.0, 1.0].
Complexity: O(1) mathematical evaluations.
Production Concerns: Boundary checks (min > max validation); handling None inputs gracefully.
Future Improvements: Automatically scale standard deviations (sigma) proportional to target ranges.
"""
import math
from typing import Optional

def calculate_experience_score(
    candidate_experience: float,
    min_years: Optional[float] = None,
    max_years: Optional[float] = None,
    sigma_low: float = 1.5,
    sigma_high: float = 3.5
) -> float:
    """
    Computes experience matching score using a Gaussian decay curve.
    - If experience is within target bounds [min_years, max_years], returns 1.0.
    - If experience is below min_years, decays smoothly towards 0.0 using sigma_low.
    - If experience is above max_years, decays smoothly towards 0.0 using sigma_high (allowing a gentler penalty for overqualification).
    """
    # Safeguard against negative experience values
    candidate_experience = max(0.0, candidate_experience)
    
    # If no requirements are specified, match is perfect
    if min_years is None and max_years is None:
        return 1.0
        
    # Standardize boundary limits
    min_val = min_years if min_years is not None else 0.0
    max_val = max_years if max_years is not None else float('inf')
    
    # Validation safeguard for boundary reversal
    if min_val > max_val:
        min_val, max_val = max_val, min_val
        
    if min_val <= candidate_experience <= max_val:
        return 1.0
        
    if candidate_experience < min_val:
        # Lower boundary decay
        diff = candidate_experience - min_val
        score = math.exp(-(diff ** 2) / (2 * (sigma_low ** 2)))
        return max(0.0, min(1.0, score))
    else:
        # Upper boundary decay (overqualification)
        diff = candidate_experience - max_val
        score = math.exp(-(diff ** 2) / (2 * (sigma_high ** 2)))
        return max(0.0, min(1.0, score))
