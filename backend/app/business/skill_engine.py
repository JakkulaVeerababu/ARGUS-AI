"""
Purpose: Computes candidate skill match score dynamically by checking overlap with must-have (80%) and nice-to-have (20%) skill targets.
Inputs:
    - candidate_skills: List[str]
    - must_have_skills: List[str]
    - nice_to_have_skills: List[str]
Outputs:
    - float score in range [0.0, 1.0].
Complexity: O(C * (M + N)) where C is candidate skills count, M, N are requirement lists lengths.
Production Concerns: Flexible naming match (e.g. "Python 3" vs "Python"); casing variations.
Future Improvements: Embed skill sets and run semantic mapping or taxonomy matches (e.g., "PyTorch" is a subset of "Deep Learning").
"""
from typing import List

def is_skill_matched(cand_skill: str, target_skill: str) -> bool:
    """Checks substring matching to handle suffix/prefix variations (e.g. 'ReactJS' matches 'React')."""
    cs = cand_skill.strip().lower()
    ts = target_skill.strip().lower()
    return ts in cs or cs in ts

def calculate_skill_score(
    candidate_skills: List[str],
    must_have_skills: List[str],
    nice_to_have_skills: List[str]
) -> float:
    """
    Computes weighted skill matching score.
    - S_must = ratio of must_have skills matched. If must_have list is empty, S_must = 1.0.
    - S_nice = ratio of nice_to_have skills matched. If nice_to_have list is empty, S_nice = 1.0.
    - Final score = 0.8 * S_must + 0.2 * S_nice.
    """
    cand_skills_clean = [s.strip().lower() for s in candidate_skills if s.strip()]
    must_clean = [s.strip().lower() for s in must_have_skills if s.strip()]
    nice_clean = [s.strip().lower() for s in nice_to_have_skills if s.strip()]
    
    # S_must calculation
    if not must_clean:
        s_must = 1.0
    else:
        matched_must = 0
        for target in must_clean:
            # Check if any candidate skill matches this target
            if any(is_skill_matched(cand, target) for cand in cand_skills_clean):
                matched_must += 1
        s_must = matched_must / len(must_clean)
        
    # S_nice calculation
    if not nice_clean:
        s_nice = 1.0
    else:
        matched_nice = 0
        for target in nice_clean:
            if any(is_skill_matched(cand, target) for cand in cand_skills_clean):
                matched_nice += 1
        s_nice = matched_nice / len(nice_clean)
        
    # Combine with weighted formula
    return 0.8 * s_must + 0.2 * s_nice
