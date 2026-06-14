import pytest
from backend.app.reasoning.template_engine import TemplateEngine
from backend.app.reasoning.reason_builder import build_candidate_reasoning

def test_template_engine_explanation_generation():
    candidate = {
        "profile": {
            "current_title": "AI Engineer",
            "years_of_experience": 6.5,
            "location": "Pune, India"
        },
        "skills": [
            {"name": "Python", "proficiency": "expert"},
            {"name": "PyTorch", "proficiency": "expert"},
            {"name": "NLP", "proficiency": "expert"}
        ],
        "career_history": [
            {"company": "TCS", "role": "ML Engineer"},
            {"company": "Infosys", "role": "Software Engineer"}
        ],
        "redrob_signals": {
            "profile_completeness_score": 92.0,
            "notice_period_days": 15,
            "github_activity_score": 85.0
        }
    }
    
    explanation = build_candidate_reasoning(candidate, rank=1)
    
    assert isinstance(explanation, str)
    
    # Check word count constraints: must be between 40 and 80 words
    words = explanation.split()
    word_count = len(words)
    print(f"Generated text ({word_count} words): {explanation}")
    assert 40 <= word_count <= 80
    
    # Fact-checking against candidate details
    assert "AI Engineer" in explanation
    assert "6.5" in explanation
    assert "Python" in explanation
    assert "Pune, India" in explanation or "Pune" in explanation
    assert "TCS" in explanation
    assert "92%" in explanation
    assert "85" in explanation
    assert "15 days" in explanation

def test_template_engine_with_minimal_candidate():
    candidate = {
        "profile": {
            "current_title": "Software Engineer",
            "years_of_experience": 2.0,
            "location": "Bangalore"
        },
        "skills": [],
        "career_history": [],
        "redrob_signals": {
            "profile_completeness_score": 55.0,
            "notice_period_days": 90,
            "github_activity_score": -1.0
        }
    }
    
    explanation = build_candidate_reasoning(candidate, rank=10)
    
    assert isinstance(explanation, str)
    words = explanation.split()
    word_count = len(words)
    print(f"Generated text for minimal candidate ({word_count} words): {explanation}")
    assert 40 <= word_count <= 80
    
    assert "Software Engineer" in explanation
    assert "2.0" in explanation
    assert "Bangalore" in explanation
    assert "55%" in explanation
    assert "90 days" in explanation
    # Should not mention github activity score because it is -1.0
    assert "GitHub" not in explanation
