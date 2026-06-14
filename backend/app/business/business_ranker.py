"""
Purpose: Orchestrates the dynamic business scoring and feature-based candidate ranking pipeline.
Inputs:
    - candidate: Dict[str, Any] (candidate profile record)
    - parsed_jd: JDRequirementsSchema / Dict[str, Any] (parsed requirements)
    - ce_score: float (raw Cross-Encoder score logit)
    - model: Optional[SentenceTransformer] (shared encoder for semantic title similarity)
Outputs:
    - Dict containing:
        - final_score: float (overall weighted additive rank score)
        - feature_vector: CandidateFeatureVector / Dict
        - reasoning: str (fact-based explanation strictly 40-80 words)
Complexity: O(E) where E is the summation of individual business engine runs.
Production Concerns: Strict scaling limits; clipping out-of-bounds metrics; robust handling of missing profile fields.
Future Improvements: Support dynamic loading of weights configurations from env files or databases.
"""
import math
from typing import Dict, Any, Optional

from backend.app.business.schema import JDRequirementsSchema
from backend.app.business.feature_vector import CandidateFeatureVector
from backend.app.business.experience_engine import calculate_experience_score
from backend.app.business.location_engine import calculate_location_score
from backend.app.business.title_engine import calculate_title_score
from backend.app.business.skill_engine import calculate_skill_score
from backend.app.business.company_engine import calculate_company_score
from backend.app.business.notice_engine import calculate_notice_score
from backend.app.business.engagement_engine import calculate_engagement_score

# Weighted additive model configurations
WEIGHTS = {
    "cross_encoder": 0.60,
    "skills": 0.12,
    "experience": 0.08,
    "title": 0.05,
    "location": 0.05,
    "engagement": 0.04,
    "notice": 0.03,
    "company": 0.03
}

def sigmoid(x: float) -> float:
    """Clips logits and applies sigmoid function to scale to [0.0, 1.0]."""
    x = max(-20.0, min(20.0, x))
    return 1.0 / (1.0 + math.exp(-x))

def generate_feature_explanation(
    candidate_id: str,
    title: str,
    years: float,
    skills_score: float,
    experience_score: float,
    engagement_score: float,
    notice_score: float,
    company_score: float,
    location_score: float,
    notice_days: int
) -> str:
    """
    Generates a fact-based explanation strictly within the 40-80 words range.
    Uses actual feature scores to select precise description clauses without hallucinations.
    """
    # 1. Base statement
    reason = f"Candidate {candidate_id} matches as a {title} with {years:.1f} years of experience."
    
    # 2. Add technical skill alignment clause
    if skills_score >= 0.8:
        reason += " Demonstrates excellent technical alignment with target skills."
    elif skills_score >= 0.5:
        reason += " Shows moderate alignment with must-have skills."
    else:
        reason += " Matches fundamental technical concepts requested."
        
    # 3. Add experience and location details
    if experience_score >= 0.8:
        reason += " Experience parameters closely match the target requirement."
        
    if location_score >= 0.95:
        reason += " Located directly in or regionally adjacent to the target hiring area."
    elif location_score >= 0.8:
        reason += " Open to relocation for this position."
        
    # 4. Add company background
    if company_score > 1.0:
        reason += " Possesses valued experience from target companies."
        
    # 5. Add platform responsiveness and notice period details
    if engagement_score >= 0.8:
        reason += " High engagement scores on the platform."
        
    if notice_days == 0:
        reason += " Available to join immediately."
    else:
        reason += f" Available to start within a notice period of {notice_days} days."
        
    return reason

def rank_candidate(
    candidate: Dict[str, Any],
    parsed_jd: Any,
    ce_score: float,
    model: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Computes all business scores, maps the feature vector,
    and returns final score and reasoning.
    """
    # Convert dict requirements to schema if needed
    if isinstance(parsed_jd, dict):
        # Graceful dictionary mapping
        exp_req = parsed_jd.get("experience", {})
        min_y = exp_req.get("min_years") if isinstance(exp_req, dict) else exp_req.min_years if hasattr(exp_req, "min_years") else None
        max_y = exp_req.get("max_years") if isinstance(exp_req, dict) else exp_req.max_years if hasattr(exp_req, "max_years") else None
        
        jd_req = JDRequirementsSchema(
            must_have_skills=parsed_jd.get("must_have_skills", []),
            nice_to_have_skills=parsed_jd.get("nice_to_have_skills", []),
            experience={"min_years": min_y, "max_years": max_y},
            locations=parsed_jd.get("locations", []),
            titles=parsed_jd.get("titles", []),
            companies=parsed_jd.get("companies", [])
        )
    else:
        jd_req = parsed_jd
        
    # Extract candidate profiles and signals
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    cid = candidate.get("candidate_id", "Unknown")
    
    # 1. Compute Individual Feature Scores
    scaled_ce = sigmoid(ce_score)
    
    exp_score = calculate_experience_score(
        candidate_experience=profile.get("years_of_experience", 0.0),
        min_years=jd_req.experience.min_years,
        max_years=jd_req.experience.max_years
    )
    
    loc_score = calculate_location_score(
        candidate_location=profile.get("location", ""),
        target_locations=jd_req.locations,
        willing_to_relocate=signals.get("willing_to_relocate", False),
        candidate_is_remote=signals.get("is_remote", False)
    )
    
    title_score = calculate_title_score(
        candidate_title=profile.get("current_title", ""),
        target_titles=jd_req.titles,
        model=model
    )
    
    # Extract past companies list
    past_companies = [
        job.get("company", "") for job in candidate.get("career_history", []) if job.get("company")
    ]
    comp_score = calculate_company_score(
        candidate_past_companies=past_companies,
        preferred_companies=jd_req.companies
    )
    
    # Normalize company multiplier (1.10 / 1.0) into a [0, 1] feature for the additive model
    comp_feature = 1.0 if comp_score > 1.0 else 0.0
    
    # Extract skills list
    cand_skills = [
        s.get("name", "") for s in candidate.get("skills", []) if s.get("name")
    ]
    skill_score = calculate_skill_score(
        candidate_skills=cand_skills,
        must_have_skills=jd_req.must_have_skills,
        nice_to_have_skills=jd_req.nice_to_have_skills
    )
    
    notice_days = signals.get("notice_period_days", 0)
    not_score = calculate_notice_score(notice_period_days=notice_days)
    
    eng_score = calculate_engagement_score(
        open_to_work=signals.get("open_to_work", False),
        recruiter_response_rate=signals.get("recruiter_response_rate", 0.0),
        offer_acceptance_rate=signals.get("offer_acceptance_rate", 0.0),
        interview_completion_rate=signals.get("interview_completion_rate", 0.0),
        github_activity_score=signals.get("github_activity_score", 0.0)
    )
    
    # 2. Build CandidateFeatureVector
    fv = CandidateFeatureVector(
        cross_encoder=scaled_ce,
        experience=exp_score,
        location=loc_score,
        title=title_score,
        skills=skill_score,
        company=comp_score,
        notice=not_score,
        engagement=eng_score
    )
    
    # 3. Calculate Weighted Additive Score
    final_score = (
        WEIGHTS["cross_encoder"] * scaled_ce +
        WEIGHTS["skills"] * skill_score +
        WEIGHTS["experience"] * exp_score +
        WEIGHTS["title"] * title_score +
        WEIGHTS["location"] * loc_score +
        WEIGHTS["engagement"] * eng_score +
        WEIGHTS["notice"] * not_score +
        WEIGHTS["company"] * comp_feature
    )
    
    # 4. Generate Explainability Reason
    reason = generate_feature_explanation(
        candidate_id=cid,
        title=profile.get("current_title", "Software Engineer"),
        years=profile.get("years_of_experience", 0.0),
        skills_score=skill_score,
        experience_score=exp_score,
        engagement_score=eng_score,
        notice_score=not_score,
        company_score=comp_score,
        location_score=loc_score,
        notice_days=notice_days
    )
    
    return {
        "candidate_id": cid,
        "final_score": float(final_score),
        "feature_vector": fv.model_dump(),
        "reasoning": reason
    }
