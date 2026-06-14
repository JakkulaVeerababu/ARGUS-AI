from typing import Dict, Any


def explain_title(candidate: Dict[str, Any]) -> str:
    """
    Extracts and formats the candidate's current title for template insertion.
    """
    profile = candidate.get("profile", {})
    title = profile.get("current_title", "")
    if not title:
        return "Technical Specialist"
    return title.strip()
