from typing import Dict, Any


def explain_engagement(candidate: Dict[str, Any]) -> str:
    """
    Generates a deterministic clause describing platform engagement, notice period, and responsiveness.
    """
    signals = candidate.get("redrob_signals", {})

    completeness = signals.get("profile_completeness_score", 100.0)
    notice = signals.get("notice_period_days", 0)
    github = signals.get("github_activity_score", -1.0)
    open_work = bool(signals.get("open_to_work", False))

    clause = (
        f"Maintains a {completeness:.0f}% complete profile with high responsiveness."
    )

    if github >= 50.0:
        clause += f" Demonstrates strong repository activity with a GitHub score of {github:.0f}."

    if open_work:
        clause += " Listed as actively open to opportunities."

    if notice == 0:
        clause += " Available to onboard immediately."
    else:
        clause += f" Ready to onboard within {notice} days."

    return clause
