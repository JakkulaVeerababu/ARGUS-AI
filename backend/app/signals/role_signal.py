import re
from typing import Dict, Any, List

STRONG_TECH_KEYWORDS = [
    r"\bai\b", r"\bml\b", r"\bmachine learning\b", r"\bnlp\b", r"\bdata scientist\b",
    r"\bbackend\b", r"\bsoftware\b", r"\bdeveloper\b", r"\bretrieval\b", r"\bsearch\b"
]

PENALTY_KEYWORDS = [
    r"\bhr\b", r"\brecruiter\b", r"\bsales\b", r"\bmarketing\b", r"\baccountant\b",
    r"\bproject manager\b", r"\bproduct manager\b", r"\bscrum master\b"
]

CONSULTING_FIRMS = [
    "tcs", "tata consultancy", "infosys", "wipro", "cognizant", "tech mahindra",
    "hcl", "l&t", "lti", "capgemini", "accenture", "deloitte", "ey", "pwc", "kpmg",
    "genpact", "mindtree", "wipro technologies"
]

def calculate_role_factor(candidate: Dict[str, Any]) -> float:
    """
    Calculates role fit factor based on current title and career history.
    Also applies a 0.5x penalty if the entire career is exclusively at IT services/consulting firms.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "").lower()
    
    # 1. Title Fit Scoring
    title_factor = 0.8  # Default neutral/adjacent
    
    # Check strong tech title match
    for kw in STRONG_TECH_KEYWORDS:
        if re.search(kw, title):
            title_factor = 1.0
            break
            
    # Check penalty non-tech title match
    for kw in PENALTY_KEYWORDS:
        if re.search(kw, title):
            title_factor = 0.5
            break

    # 2. IT Consulting Exclusivity Check
    career = candidate.get("career_history", [])
    if career:
        exclusive_consulting = True
        for job in career:
            comp = job.get("company", "").lower()
            if not comp:
                continue
            # Check if this company name matches any known consulting firm
            matched = False
            for firm in CONSULTING_FIRMS:
                if firm in comp:
                    matched = True
                    break
            if not matched:
                exclusive_consulting = False
                break
                
        # If all companies are IT services, apply 0.5x multiplier
        if exclusive_consulting:
            title_factor *= 0.5

    return title_factor
