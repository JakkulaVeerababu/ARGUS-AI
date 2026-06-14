"""
Purpose: Computes preferred company boost factor dynamically against JD company list.
Inputs:
    - candidate_past_companies: List[str]
    - preferred_companies: List[str]
Outputs:
    - float boost multiplier in range [1.0, 1.10].
Complexity: O(C * P) where C is candidate past companies list, P is preferred companies list.
Production Concerns: Casing variations and suffixes (e.g. "Google LLC" matches "Google").
Future Improvements: Support tier-based company classification mappings (e.g. Tier-1 Product, Tier-2 Service).
"""
from typing import List

def calculate_company_score(
    candidate_past_companies: List[str],
    preferred_companies: List[str],
    max_boost: float = 1.10
) -> float:
    """
    Computes company ranking score.
    - If preferred_companies is empty, returns 1.0 (no boost).
    - If any candidate company matches any preferred company (substring match), returns max_boost (1.10).
    - Otherwise, returns 1.0.
    """
    cand_comps_clean = [c.strip().lower() for c in candidate_past_companies if c.strip()]
    pref_comps_clean = [p.strip().lower() for p in preferred_companies if p.strip()]
    
    if not pref_comps_clean:
        return 1.0
        
    for p_comp in pref_comps_clean:
        for c_comp in cand_comps_clean:
            if p_comp in c_comp or c_comp in p_comp:
                return max_boost
                
    return 1.0
