from typing import Dict, Any


def calculate_experience_factor(
    profile: Dict[str, Any], target_min: float = 5.0, target_max: float = 9.0
) -> float:
    """
    Computes experience multiplier based on distance from target range [5.0, 9.0] years.
    Ranges from 1.0 (ideal) down to 0.5 (far away).
    """
    exp = profile.get("years_of_experience", 0.0)

    if target_min <= exp <= target_max:
        return 1.0

    if exp < target_min:
        distance = target_min - exp
    else:
        distance = exp - target_max

    # Apply linear decay of 0.1 per year of distance, capped at 0.5
    factor = 1.0 - 0.1 * distance
    return max(0.5, factor)
