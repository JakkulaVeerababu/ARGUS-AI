from typing import Dict, Any


def calculate_notice_factor(candidate: Dict[str, Any]) -> float:
    """
    Computes notice period multiplier based on notice_period_days.
    - Notice period <= 60 days: 1.0 (ideal)
    - Notice period 61-90 days: 0.9 (marginal)
    - Notice period > 90 days: 0.7 (penalty)
    """
    signals = candidate.get("redrob_signals", {})
    notice_days = signals.get("notice_period_days", 0)

    if notice_days <= 60:
        return 1.0
    elif notice_days <= 90:
        return 0.9
    else:
        return 0.7
