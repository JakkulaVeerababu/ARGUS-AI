from typing import Dict, Any

def calculate_github_factor(candidate: Dict[str, Any]) -> float:
    """
    Computes GitHub multiplier based on activity score.
    - No GitHub linked (-1): 1.0 (neutral)
    - Active GitHub (0-100): 1.0 to 1.1 (boosts up to 10%)
    """
    signals = candidate.get("redrob_signals", {})
    github_score = signals.get("github_activity_score", -1.0)
    
    if github_score < 0.0:
        return 1.0
        
    boost = 0.1 * (github_score / 100.0)
    return 1.0 + boost
