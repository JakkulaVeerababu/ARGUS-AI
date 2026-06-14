from typing import Dict, Any

def check_certification_violation(candidate: Dict[str, Any]) -> bool:
    """
    Checks if a candidate has certifications dated in the future (> 2026).
    """
    certs = candidate.get("certifications", [])
    
    for c in certs:
        cyear = c.get("year", 0)
        # 2026 is current competition year context
        if cyear > 2026:
            return True
            
    return False
