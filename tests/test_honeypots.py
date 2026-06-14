import pytest
from backend.app.honeypots.gatekeeper import evaluate_candidate_risk
from backend.app.honeypots.salary_rules import check_salary_violation
from backend.app.honeypots.timeline_rules import check_timeline_violation
from backend.app.honeypots.skill_rules import check_skill_violation
from backend.app.honeypots.certification_rules import check_certification_violation

def test_salary_rules():
    # Valid salary
    valid_cand = {
        "redrob_signals": {
            "expected_salary_range_inr_lpa": {"min": 10.0, "max": 15.0}
        }
    }
    assert not check_salary_violation(valid_cand)

    # Invalid salary (min > max)
    invalid_cand = {
        "redrob_signals": {
            "expected_salary_range_inr_lpa": {"min": 20.0, "max": 15.0}
        }
    }
    assert check_salary_violation(invalid_cand)

def test_timeline_rules():
    # Valid work history durations
    valid_cand = {
        "career_history": [
            {
                "start_date": "2020-01-01",
                "end_date": "2022-01-01",
                "duration_months": 24.0
            }
        ]
    }
    assert not check_timeline_violation(valid_cand)

    # Claimed duration far exceeds date range
    invalid_cand = {
        "career_history": [
            {
                "start_date": "2020-01-01",
                "end_date": "2020-06-01",
                "duration_months": 24.0  # Claimed 2 years for 5 months period
            }
        ]
    }
    assert check_timeline_violation(invalid_cand)

def test_skill_rules():
    # Valid expert skill
    valid_cand = {
        "skills": [
            {
                "name": "Python",
                "proficiency": "expert",
                "duration_months": 36.0
            }
        ]
    }
    assert not check_skill_violation(valid_cand)

    # Expert skill with 0 duration_months (must be >= 5 to trigger flag)
    invalid_cand = {
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 0.0},
            {"name": "Java", "proficiency": "expert", "duration_months": 0.0},
            {"name": "Go", "proficiency": "expert", "duration_months": 0.0},
            {"name": "JS", "proficiency": "expert", "duration_months": 0.0},
            {"name": "C++", "proficiency": "expert", "duration_months": 0.0}
        ]
    }
    assert check_skill_violation(invalid_cand)

def test_certification_rules():
    # Valid certification date
    valid_cand = {
        "certifications": [
            {
                "name": "AWS Solutions Architect",
                "year": 2024
            }
        ]
    }
    assert not check_certification_violation(valid_cand)

    # Certification in the future (exceeding reference June 2026)
    invalid_cand = {
        "certifications": [
            {
                "name": "AWS Solutions Architect",
                "year": 2027
            }
        ]
    }
    assert check_certification_violation(invalid_cand)

def test_gatekeeper_risk_evaluation():
    # Clean profile
    clean_cand = {
        "candidate_id": "CAND_001",
        "profile": {},
        "redrob_signals": {
            "profile_completeness_score": 85.0,
            "notice_period_days": 30,
            "last_active_date": "2026-05-01"
        }
    }
    risk = evaluate_candidate_risk(clean_cand)
    assert not risk["honeypot_flag"]
    assert risk["risk_score"] == 0.0

    # Candidate with soft penalties
    risky_cand = {
        "candidate_id": "CAND_002",
        "profile": {},
        "redrob_signals": {
            "profile_completeness_score": 40.0,  # +0.20
            "notice_period_days": 100,            # +0.20
            "last_active_date": "2025-01-01"     # +0.20 (inactive > 6 months)
        }
    }
    risk = evaluate_candidate_risk(risky_cand)
    assert not risk["honeypot_flag"]
    assert risk["risk_score"] == pytest.approx(0.60)
    assert len(risk["reasons"]) == 3
