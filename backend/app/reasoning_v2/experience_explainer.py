from typing import Dict, Any, Optional


def explain_experience(
    candidate: Dict[str, Any],
    min_years: Optional[float] = None,
    max_years: Optional[float] = None,
) -> str:
    """
    Generates a deterministic experience segment for template placeholders.
    """
    years = candidate.get("profile", {}).get("years_of_experience", 0.0)

    if min_years is not None and max_years is not None:
        if min_years <= years <= max_years:
            return f"{years:.1f} years of experience, aligning with the target {min_years}-{max_years} years requirement"
        elif years > max_years:
            return f"{years:.1f} years of experience, exceeding the target maximum of {max_years} years"
        else:
            return f"{years:.1f} years of experience, approaching the target minimum of {min_years} years"

    elif min_years is not None:
        if years >= min_years:
            return f"{years:.1f} years of experience, exceeding the minimum of {min_years} years"
        else:
            return f"{years:.1f} years of experience, building up to the required {min_years} years"

    return f"{years:.1f} years of professional experience"
