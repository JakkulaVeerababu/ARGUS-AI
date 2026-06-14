from typing import Dict, Any
from backend.app.preprocessing.document_builder import build_candidate_document


def parse_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a raw candidate JSON record:
    1. Compiles the raw document text using the document builder.
    2. Extracts specific numerical signals needed for the ranking filters.
    3. Excludes metadata noise like generic names, verification statuses, and connection counts.
    """
    cid = candidate.get("candidate_id")
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    # Compile text representation
    doc_text = build_candidate_document(candidate)

    # Extract targeted properties
    experience = profile.get("years_of_experience", 0.0)
    location = profile.get("location", "")
    github_score = signals.get("github_activity_score", -1.0)
    response_rate = signals.get("recruiter_response_rate", 0.0)
    notice_period = signals.get("notice_period_days", 0)

    return {
        "candidate_id": cid,
        "document_text": doc_text,
        "experience": experience,
        "location": location,
        "github_score": github_score,
        "response_rate": response_rate,
        "notice_period": notice_period,
    }
