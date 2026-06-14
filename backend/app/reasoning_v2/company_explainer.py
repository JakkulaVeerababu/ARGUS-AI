from typing import Dict, Any, List, Optional

def explain_companies(candidate: Dict[str, Any], preferred_companies: Optional[List[str]] = None) -> str:
    """
    Generates a deterministic clause detailing the candidate's career history.
    Highlights matching preferred employers if found in candidate career history.
    """
    history = candidate.get("career_history", [])
    cand_companies = []
    for job in history:
        c = job.get("company", "").strip()
        if c and c not in cand_companies:
            cand_companies.append(c)
            
    # Check overlaps with preferred companies list
    matched = []
    if preferred_companies:
        for pref in preferred_companies:
            pref_clean = pref.strip().lower()
            if not pref_clean:
                continue
            if any(pref_clean in cc.lower() for cc in cand_companies):
                matched.append(pref.strip())
                
    if matched:
        top_matched = matched[:2]
        if len(top_matched) > 1:
            comp_str = f"{top_matched[0]} and {top_matched[1]}"
        else:
            comp_str = top_matched[0]
        return f"Previously worked at targeted organizations including {comp_str}."
        
    elif cand_companies:
        top_comp = cand_companies[:2]
        if len(cand_companies) > 2:
            comp_str = f"{', '.join(top_comp)}, and others"
        elif len(top_comp) > 1:
            comp_str = f"{top_comp[0]} and {top_comp[1]}"
        else:
            comp_str = top_comp[0]
        return f"Brings a professional background at companies like {comp_str}."
        
    return ""
