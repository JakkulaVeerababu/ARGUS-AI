from typing import Dict, Any


def check_salary_violation(candidate: Dict[str, Any]) -> bool:
    """
    Checks if expected salary range is logically impossible (min > max).
    """
    signals = candidate.get("redrob_signals", {})
    salary_range = signals.get("expected_salary_range_inr_lpa", {})

    if not salary_range:
        return False

    s_min = salary_range.get("min", 0.0)
    s_max = salary_range.get("max", 0.0)

    # If min > max, it is a logical violation
    if s_min > s_max:
        return True

    return False
