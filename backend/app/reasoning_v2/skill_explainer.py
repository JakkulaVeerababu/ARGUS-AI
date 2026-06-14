from typing import Dict, Any, List

def explain_skills(candidate: Dict[str, Any], must_have: List[str], nice_to_have: List[str]) -> str:
    """
    Generates a deterministic clause describing the candidate's skill fit.
    Compares candidate skills to JD must-have/nice-to-have parameters.
    """
    cand_skills = {s.get("name", "").strip().lower() for s in candidate.get("skills", []) if s.get("name")}
    
    # Filter matching requirements
    matched_must = [m.strip() for m in must_have if m.strip().lower() in cand_skills]
    matched_nice = [n.strip() for n in nice_to_have if n.strip().lower() in cand_skills]
    
    if matched_must:
        top_must = matched_must[:3]
        if len(top_must) > 1:
            skills_str = ", ".join(top_must[:-1]) + f", and {top_must[-1]}"
        else:
            skills_str = top_must[0]
        return f"Demonstrates core proficiency in must-have technical skills like {skills_str}."
        
    elif matched_nice:
        top_nice = matched_nice[:3]
        if len(top_nice) > 1:
            skills_str = ", ".join(top_nice[:-1]) + f", and {top_nice[-1]}"
        else:
            skills_str = top_nice[0]
        return f"Possesses critical alignment in nice-to-have capabilities including {skills_str}."
        
    else:
        # Fallback to general skills from candidate profile
        general_skills = [s.get("name", "").strip() for s in candidate.get("skills", []) if s.get("name")]
        if general_skills:
            top_gen = general_skills[:3]
            if len(top_gen) > 1:
                skills_str = ", ".join(top_gen[:-1]) + f", and {top_gen[-1]}"
            else:
                skills_str = top_gen[0]
            return f"Brings technical software engineering expertise in {skills_str}."
        else:
            return "Brings baseline software engineering and application development skills."
