from typing import Dict, Any

def check_skill_violation(candidate: Dict[str, Any]) -> bool:
    """
    Checks if the candidate claims "expert" proficiency in multiple skills
    but has zero months of duration recorded for them.
    Returns True if at least 5 such anomalies are found.
    """
    skills = candidate.get("skills", [])
    
    expert_0_dur = [
        s for s in skills
        if s.get("proficiency") == "expert" and s.get("duration_months", 0) == 0
    ]
    
    # Flag if there are 5 or more expert level skills with 0 months duration
    if len(expert_0_dur) >= 5:
        return True
        
    return False
