from typing import Dict, Any

def calculate_profile_quality_factor(candidate: Dict[str, Any]) -> float:
    """
    Computes profile completeness factor.
    - Completeness 0-100: scales from 0.9 to 1.0.
    """
    signals = candidate.get("redrob_signals", {})
    completeness = signals.get("profile_completeness_score", 0.0)
    
    boost = 0.1 * (completeness / 100.0)
    return 0.9 + boost
