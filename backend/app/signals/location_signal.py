from typing import Dict, Any

TARGET_CITIES = [
    "delhi",
    "noida",
    "gurgaon",
    "gurugram",
    "ncr",
    "pune",
    "bangalore",
    "bengaluru",
    "hyderabad",
    "mumbai",
]


def calculate_location_factor(candidate: Dict[str, Any]) -> float:
    """
    Computes location multiplier based on target cities and relocation preferences.
    - Matches target cities: 1.0
    - Relocation candidate: 0.9
    - Mismatch and not willing to relocate: 0.6
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    loc = profile.get("location", "").lower()
    willing_relocate = signals.get("willing_to_relocate", False)

    # Check if candidate is located in any target cities
    is_target_location = False
    for city in TARGET_CITIES:
        if city in loc:
            is_target_location = True
            break

    if is_target_location:
        return 1.0

    if willing_relocate:
        return 0.9

    return 0.6
