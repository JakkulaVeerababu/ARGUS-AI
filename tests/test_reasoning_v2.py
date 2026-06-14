import pytest
from backend.app.reasoning_v2.template_selector import select_template
from backend.app.reasoning_v2.reason_builder_v2 import build_candidate_reasoning_v2

def test_template_selector_deterministic():
    cid = "CAND_0000001"
    t1 = select_template(cid)
    t2 = select_template(cid)
    assert t1 == t2
    
    cid2 = "CAND_0000002"
    t3 = select_template(cid2)
    assert isinstance(t1, str)
    assert isinstance(t3, str)

def test_reason_builder_v2_word_count_limits():
    # 1. Test candidate with minimal info (exercises padding fallback system)
    candidate_minimal = {
        "candidate_id": "CAND_0000101",
        "profile": {
            "current_title": "Python Developer",
            "years_of_experience": 2.5,
            "location": "Pune"
        },
        "skills": [{"name": "Python"}],
        "career_history": [],
        "redrob_signals": {
            "profile_completeness_score": 70.0,
            "notice_period_days": 15
        }
    }
    
    parsed_jd = {
        "must_have_skills": ["Python", "Django"],
        "nice_to_have_skills": ["PostgreSQL"],
        "locations": ["Pune", "Mumbai"],
        "experience": {"min_years": 2.0, "max_years": 5.0}
    }
    
    reason = build_candidate_reasoning_v2(candidate_minimal, rank=1, parsed_jd=parsed_jd)
    words = reason.split()
    word_count = len(words)
    
    assert 40 <= word_count <= 80
    assert reason.endswith(".")
    
    # 2. Test candidate with extensive details (exercises length compression/truncation)
    candidate_extensive = {
        "candidate_id": "CAND_0000102",
        "profile": {
            "current_title": "Principal AI Architect",
            "years_of_experience": 15.5,
            "location": "Bangalore"
        },
        "skills": [
            {"name": "Python"}, {"name": "PyTorch"}, {"name": "TensorFlow"}, 
            {"name": "Transformers"}, {"name": "FAISS"}, {"name": "Docker"},
            {"name": "FastAPI"}, {"name": "Kubernetes"}, {"name": "SQL"}
        ],
        "career_history": [
            {"company": "Google"}, {"company": "Microsoft"}, 
            {"company": "Meta"}, {"company": "Amazon"}
        ],
        "certifications": [
            {"name": "AWS Solution Architect"}, {"name": "Google Cloud Architect"}
        ],
        "redrob_signals": {
            "profile_completeness_score": 100.0,
            "notice_period_days": 90,
            "github_activity_score": 95.0,
            "open_to_work": True
        }
    }
    
    parsed_jd_ext = {
        "must_have_skills": ["Python", "PyTorch", "Transformers"],
        "nice_to_have_skills": ["Docker", "FastAPI"],
        "locations": ["Bangalore"],
        "companies": ["Google", "Microsoft"],
        "experience": {"min_years": 10.0, "max_years": 20.0}
    }
    
    reason_ext = build_candidate_reasoning_v2(candidate_extensive, rank=1, parsed_jd=parsed_jd_ext)
    words_ext = reason_ext.split()
    word_count_ext = len(words_ext)
    
    assert 40 <= word_count_ext <= 80
    assert reason_ext.endswith(".")
