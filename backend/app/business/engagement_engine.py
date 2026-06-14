"""
Purpose: Computes candidate engagement score by normalizing and combining platform activity signals.
Inputs:
    - open_to_work: bool
    - recruiter_response_rate: float
    - offer_acceptance_rate: float
    - interview_completion_rate: float
    - github_activity_score: float
Outputs:
    - float score in range [0.0, 1.0].
Complexity: O(1) mathematical operations.
Production Concerns: Clipping boundary limits to ensure stability; applying logical fallback defaults for missing metrics.
Future Improvements: Factor in time-decayed login frequency or reply latency metrics.
"""
def calculate_engagement_score(
    open_to_work: bool,
    recruiter_response_rate: float,
    offer_acceptance_rate: float,
    interview_completion_rate: float,
    github_activity_score: float
) -> float:
    """
    Combines engagement signals into a normalized score.
    Weights:
    - open_to_work (bool): Weight 0.3 (Active search indicator)
    - recruiter_response_rate (float 0-1): Weight 0.2 (Responsiveness)
    - github_activity_score (float 0-100, normalized to 0-1): Weight 0.2 (Open-source contribution level)
    - interview_completion_rate (float 0-1): Weight 0.15 (Interview consistency)
    - offer_acceptance_rate (float 0-1): Weight 0.15 (Acceptance probability)
    """
    # Normalize inputs
    otw_val = 1.0 if open_to_work else 0.5
    
    # Clip parameters to bounds [0.0, 1.0]
    resp_val = max(0.0, min(1.0, recruiter_response_rate))
    acceptance_val = max(0.0, min(1.0, offer_acceptance_rate))
    completion_val = max(0.0, min(1.0, interview_completion_rate))
    
    # Normalize github score (0-100) to (0-1) range
    gh_val = max(0.0, min(100.0, github_activity_score)) / 100.0
    
    # Calculate weighted sum
    eng_score = (
        0.30 * otw_val +
        0.20 * resp_val +
        0.20 * gh_val +
        0.15 * completion_val +
        0.15 * acceptance_val
    )
    
    return max(0.0, min(1.0, eng_score))
