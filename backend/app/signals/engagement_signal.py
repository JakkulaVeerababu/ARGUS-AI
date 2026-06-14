from typing import Dict, Any

def calculate_engagement_factor(candidate: Dict[str, Any]) -> float:
    """
    Computes engagement multiplier based on candidate active flags and response telemetry.
    Aggregates open-to-work flag, response rate, interview completion, and offer acceptance.
    Factor range: [1.0, 1.2]
    """
    signals = candidate.get("redrob_signals", {})
    
    open_to_work = signals.get("open_to_work_flag", False)
    response_rate = signals.get("recruiter_response_rate", 0.0)
    interview_completion = signals.get("interview_completion_rate", 0.0)
    offer_acceptance = signals.get("offer_acceptance_rate", -1.0)
    
    factor = 1.0
    
    if open_to_work:
        factor += 0.05
        
    # Boost by response rate (0 to 1)
    factor += 0.05 * max(0.0, min(1.0, response_rate))
    
    # Boost by interview completion (0 to 1)
    factor += 0.05 * max(0.0, min(1.0, interview_completion))
    
    # Boost by offer acceptance if history is available (>=0)
    if offer_acceptance >= 0.0:
        factor += 0.05 * max(0.0, min(1.0, offer_acceptance))
        
    return factor
