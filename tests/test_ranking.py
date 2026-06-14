import os
import pytest
from backend.app.signals.final_score import BusinessScorer

def test_sigmoid_scaling():
    # Sigmoid function tests
    assert abs(BusinessScorer.sigmoid(0.0) - 0.5) < 1e-6
    assert BusinessScorer.sigmoid(5.0) > 0.99
    assert BusinessScorer.sigmoid(-5.0) < 0.01
    
    # Preventing overflow/underflow bounds check
    assert BusinessScorer.sigmoid(100.0) == BusinessScorer.sigmoid(20.0)
    assert BusinessScorer.sigmoid(-100.0) == BusinessScorer.sigmoid(-20.0)

def test_business_scorer_pipeline(tmp_path):
    # Setup mock candidate database
    candidates_file = os.path.join(tmp_path, "mock_candidates.jsonl")
    
    import json
    mock_candidates = [
        {
            "candidate_id": "CAND_01",
            "profile": {
                "anonymized_name": "Alice",
                "current_title": "AI Engineer",
                "years_of_experience": 7.0, # Ideal: experience factor 1.0
                "location": "Noida, India" # Target city: location factor 1.0
            },
            "skills": [{"name": "Python", "proficiency": "expert"}],
            "career_history": [],
            "redrob_signals": {
                "profile_completeness_score": 90.0,
                "notice_period_days": 30,
                "recruiter_response_rate": 0.95,
                "github_activity_score": 80.0
            }
        },
        {
            "candidate_id": "CAND_02",
            "profile": {
                "anonymized_name": "Bob",
                "current_title": "ML Engineer",
                "years_of_experience": 2.0, # Not ideal experience
                "location": "Remote, India"
            },
            "skills": [{"name": "Python", "proficiency": "intermediate"}],
            "career_history": [],
            "redrob_signals": {
                "profile_completeness_score": 80.0,
                "notice_period_days": 90, # Penalty notice period
                "recruiter_response_rate": 0.50,
                "github_activity_score": -1.0
            }
        }
    ]
    
    with open(candidates_file, "w", encoding="utf-8") as f:
        for cand in mock_candidates:
            f.write(json.dumps(cand) + "\n")
            
    # Instantiate BusinessScorer with temp file
    scorer = BusinessScorer(candidates_file=candidates_file)
    
    # Input Cross-Encoder logits
    ce_results = [
        ("CAND_01", 1.0), # Sigmoid(1.0) = 0.731
        ("CAND_02", 2.0)  # Sigmoid(2.0) = 0.880
    ]
    
    results = scorer.score_candidates(ce_results, top_n=2)
    assert len(results) == 2
    
    # CAND_01 should rank first because of the ideal experience (7.0 years) and Noida location
    # even though CAND_02 has a slightly higher Cross-Encoder score logit (2.0 vs 1.0).
    assert results[0]["candidate_id"] == "CAND_01"
    
    # Verify values and structure
    c1 = results[0]
    assert c1["candidate_name"] == "Alice"
    assert c1["current_title"] == "AI Engineer"
    assert abs(c1["sigmoid_ce_score"] - BusinessScorer.sigmoid(1.0)) < 1e-5
    assert c1["multipliers"]["experience"] == 1.0
    assert c1["multipliers"]["location"] == 1.0
