from typing import Dict, Any

from backend.app.honeypots.salary_rules import check_salary_violation
from backend.app.honeypots.timeline_rules import check_timeline_violation
from backend.app.honeypots.skill_rules import check_skill_violation
from backend.app.honeypots.certification_rules import check_certification_violation


def calculate_inactivity_months(last_active_str: str) -> float:
    """Computes elapsed months from last_active_str to June 2026."""
    try:
        y, m, _ = map(int, last_active_str.split("-"))
        # Reference local date context is June 14, 2026
        return (2026 - y) * 12 + (6 - m)
    except Exception:
        return 0.0


def evaluate_candidate_risk(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates candidate risk and honeypot indicators.
    Hard violations set risk_score = 1.0 (immediately excluded).
    Soft penalties accumulate to risk_score. If risk_score > 0.5, candidate is excluded.
    Returns:
        - candidate_id
        - honeypot_flag: True if any hard validation check fails.
        - risk_score: [0.0, 1.0] scale.
        - reasons: List of triggered flags.
    """
    cid = candidate.get("candidate_id")
    signals = candidate.get("redrob_signals", {})

    # 1. Hard Honeypot Checks
    salary_viol = check_salary_violation(candidate)
    timeline_viol = check_timeline_violation(candidate)
    skill_viol = check_skill_violation(candidate)
    cert_viol = check_certification_violation(candidate)

    reasons = []
    honeypot_flag = False

    if salary_viol:
        reasons.append("Salary min > max")
        honeypot_flag = True
    if timeline_viol:
        reasons.append("Timeline mismatch: claimed duration exceeds elapsed time")
        honeypot_flag = True
    if skill_viol:
        reasons.append("Expert proficiency claimed with 0 duration")
        honeypot_flag = True
    if cert_viol:
        reasons.append("Certification date in future (>2026)")
        honeypot_flag = True

    risk_score = 0.0

    if honeypot_flag:
        risk_score = 1.0
    else:
        # 2. Soft Business Penalties
        # Profile Completeness < 50
        completeness = signals.get("profile_completeness_score", 100.0)
        if completeness < 50.0:
            risk_score += 0.20
            reasons.append(f"Low profile completeness ({completeness:.1f}%)")

        # Notice Period > 90 days
        notice_days = signals.get("notice_period_days", 0)
        if notice_days > 90:
            risk_score += 0.20
            reasons.append(f"Long notice period ({notice_days} days)")

        # Inactivity for > 6 months
        last_active = signals.get("last_active_date", "2026-06-14")
        inactivity = calculate_inactivity_months(last_active)
        if inactivity > 6.0:
            risk_score += 0.20
            reasons.append(f"Inactive for {inactivity:.1f} months")

    return {
        "candidate_id": cid,
        "honeypot_flag": honeypot_flag,
        "risk_score": min(1.0, risk_score),
        "reasons": reasons,
    }


if __name__ == "__main__":
    # Diagnostic test for risk evaluator
    test_cand = {
        "candidate_id": "CAND_0000001",
        "redrob_signals": {
            "profile_completeness_score": 40.0,
            "notice_period_days": 120,
            "last_active_date": "2025-10-01",
        },
    }
    res = evaluate_candidate_risk(test_cand)
    print("Risk Assessment:")
    print(f"  ID: {res['candidate_id']}")
    print(f"  Honeypot: {res['honeypot_flag']}")
    print(f"  Risk Score: {res['risk_score']:.2f}")
    print(f"  Reasons: {res['reasons']}")
