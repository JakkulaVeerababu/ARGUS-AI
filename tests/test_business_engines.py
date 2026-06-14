"""
Unit tests for the new dynamic business scoring and ranking engines.
"""

from backend.app.business.experience_engine import calculate_experience_score
from backend.app.business.location_engine import calculate_location_score
from backend.app.business.title_engine import calculate_title_score
from backend.app.business.skill_engine import calculate_skill_score
from backend.app.business.company_engine import calculate_company_score
from backend.app.business.notice_engine import calculate_notice_score
from backend.app.business.engagement_engine import calculate_engagement_score
from backend.app.business.business_ranker import rank_candidate
from backend.app.business.schema import JDRequirementsSchema


def test_experience_engine_gaussian():
    # In range [5.0, 9.0] -> should be 1.0
    assert calculate_experience_score(7.0, min_years=5.0, max_years=9.0) == 1.0
    assert calculate_experience_score(5.0, min_years=5.0, max_years=9.0) == 1.0
    assert calculate_experience_score(9.0, min_years=5.0, max_years=9.0) == 1.0

    # Below range -> decays smoothly
    score_low = calculate_experience_score(3.0, min_years=5.0, max_years=9.0)
    assert 0.0 < score_low < 1.0

    # Above range -> decays smoothly (under overqualification)
    score_high = calculate_experience_score(12.0, min_years=5.0, max_years=9.0)
    assert 0.0 < score_high < 1.0

    # Asserting overqualification decay is gentler (sigma=3.5) than low experience decay (sigma=1.5)
    # Distance of 2 below range (5 - 3 = 2) vs distance of 2 above range (11 - 9 = 2)
    s_under = calculate_experience_score(
        3.0, min_years=5.0, max_years=9.0, sigma_low=1.5, sigma_high=3.5
    )
    s_over = calculate_experience_score(
        11.0, min_years=5.0, max_years=9.0, sigma_low=1.5, sigma_high=3.5
    )
    assert s_over > s_under


def test_location_engine():
    targets = ["Bangalore", "Noida"]

    # Exact Match
    assert calculate_location_score("Bangalore, India", targets) == 1.0

    # Regional adjacent match (Delhi-Noida equivalent NCR mapping)
    assert calculate_location_score("Delhi, India", targets) == 0.95

    # Relocatable matching
    assert (
        calculate_location_score("Pune, India", targets, willing_to_relocate=True)
        == 0.85
    )

    # Mismatch
    assert (
        calculate_location_score("Pune, India", targets, willing_to_relocate=False)
        == 0.50
    )


def test_title_engine_fallback():
    # Model is None fallback to token overlap
    targets = ["Senior ML Engineer", "Data Scientist"]
    assert calculate_title_score("Senior ML Engineer", targets) == 1.0
    assert calculate_title_score("Senior ML Developer", targets) > 0.0
    assert calculate_title_score("Analyst", targets) == 0.0


def test_skill_engine():
    must = ["Python", "PyTorch"]
    nice = ["FAISS"]

    # Match all
    assert calculate_skill_score(["Python", "PyTorch", "FAISS"], must, nice) == 1.0

    # Match must-haves only (0.8 weight)
    assert calculate_skill_score(["Python", "PyTorch"], must, nice) == 0.80

    # Match partial must-have and nice-have
    # Matched must: Python (1/2 = 0.5 ratio) -> 0.5 * 0.8 = 0.4
    # Matched nice: FAISS (1/1 = 1.0 ratio) -> 1.0 * 0.2 = 0.2
    # Total: 0.4 + 0.2 = 0.6
    assert abs(calculate_skill_score(["Python", "FAISS"], must, nice) - 0.6) < 1e-5


def test_company_engine():
    pref = ["Google", "Stripe"]
    assert calculate_company_score(["Google Inc."], pref) == 1.10
    assert calculate_company_score(["Infosys"], pref) == 1.0


def test_notice_engine_decay():
    # Exponential decay verification
    assert calculate_notice_score(0) == 1.0
    assert 0.60 <= calculate_notice_score(30) <= 0.62
    assert 0.35 <= calculate_notice_score(60) <= 0.38
    assert 0.20 <= calculate_notice_score(90) <= 0.24
    assert 0.12 <= calculate_notice_score(120) <= 0.15


def test_engagement_engine():
    # Maximum engagement
    high_score = calculate_engagement_score(
        open_to_work=True,
        recruiter_response_rate=1.0,
        offer_acceptance_rate=1.0,
        interview_completion_rate=1.0,
        github_activity_score=100.0,
    )
    assert high_score == 1.0

    # Minimum engagement
    low_score = calculate_engagement_score(
        open_to_work=False,
        recruiter_response_rate=0.0,
        offer_acceptance_rate=0.0,
        interview_completion_rate=0.0,
        github_activity_score=0.0,
    )
    assert 0.0 < low_score < 0.5


def test_business_ranker_integration():
    candidate = {
        "candidate_id": "CAND_TEST_99",
        "profile": {
            "current_title": "ML Engineer",
            "years_of_experience": 8.0,
            "location": "Bangalore",
        },
        "skills": [{"name": "Python"}, {"name": "PyTorch"}, {"name": "FAISS"}],
        "career_history": [{"company": "Google"}],
        "redrob_signals": {
            "willing_to_relocate": True,
            "open_to_work": True,
            "recruiter_response_rate": 0.90,
            "github_activity_score": 80.0,
            "notice_period_days": 30,
        },
    }

    jd = JDRequirementsSchema(
        must_have_skills=["Python", "PyTorch"],
        nice_to_have_skills=["FAISS"],
        experience={"min_years": 5.0, "max_years": 10.0},
        locations=["Bangalore"],
        titles=["ML Engineer"],
        companies=["Google"],
    )

    res = rank_candidate(candidate, jd, ce_score=2.0)
    assert "final_score" in res
    assert "feature_vector" in res
    assert "reasoning" in res
    assert 0.0 <= res["final_score"] <= 1.0
    assert len(res["reasoning"].split()) >= 20  # Has descriptive explainability
