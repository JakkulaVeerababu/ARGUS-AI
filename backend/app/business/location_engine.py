"""
Purpose: Computes candidate location match score dynamically against JD target location preferences.
Inputs:
    - candidate_location: str
    - target_locations: List[str]
    - willing_to_relocate: bool
    - candidate_is_remote: bool (optional)
Outputs:
    - float score in range [0.0, 1.0].
Complexity: O(N * M) string matching where N is number of targets, M is location text length.
Production Concerns: Variations in city spellings (e.g. Bengaluru vs Bangalore); regional grouping definitions (e.g. Noida in NCR).
Future Improvements: Integrate database-backed geocoding to resolve distances in kilometers.
"""

from typing import List

# Regional equivalences maps (e.g., NCR includes Delhi, Noida, Gurgaon, Gurugram, Ghaziabad, Faridabad)
REGIONAL_EQUIVALENTS = {
    "ncr": ["delhi", "noida", "gurgaon", "gurugram", "ghaziabad", "faridabad"],
    "delhi": ["ncr", "noida", "gurgaon", "gurugram", "ghaziabad", "faridabad"],
    "noida": ["delhi", "ncr", "gurgaon", "gurugram"],
    "gurgaon": ["delhi", "ncr", "noida", "gurugram"],
    "gurugram": ["delhi", "ncr", "noida", "gurgaon"],
    "bangalore": ["bengaluru"],
    "bengaluru": ["bangalore"],
    "bombay": ["mumbai"],
    "mumbai": ["bombay"],
}


def calculate_location_score(
    candidate_location: str,
    target_locations: List[str],
    willing_to_relocate: bool = False,
    candidate_is_remote: bool = False,
) -> float:
    """
    Computes location matching score.
    - If target_locations list is empty, location is not a constraint (score = 1.0).
    - If target_locations contains "remote" and candidate is remote -> 1.0.
    - If candidate is in any of the target locations -> 1.0 (exact match).
    - If candidate is in a regionally adjacent city (e.g. Noida for a Delhi role) -> 0.95 (regional match).
    - If candidate is not in target locations, but willing to relocate -> 0.85 (relocation match).
    - If candidate is not matching and not willing to relocate -> 0.50 (mismatch).
    """
    # Normalize inputs
    cand_loc_clean = candidate_location.strip().lower()
    targets_clean = [t.strip().lower() for t in target_locations if t.strip()]

    if not targets_clean:
        return 1.0

    # Check remote compatibility
    is_remote_position = "remote" in targets_clean
    if is_remote_position and candidate_is_remote:
        return 1.0

    # Check exact match or substring matches
    is_exact_match = False
    for target in targets_clean:
        if target in cand_loc_clean or cand_loc_clean in target:
            is_exact_match = True
            break

    if is_exact_match:
        return 1.0

    # Check regional matches (NCR or Bangalore/Bengaluru)
    is_regional_match = False
    for target in targets_clean:
        equivalents = REGIONAL_EQUIVALENTS.get(target, [])
        for eq in equivalents:
            if eq in cand_loc_clean or cand_loc_clean in eq:
                is_regional_match = True
                break
        if is_regional_match:
            break

    if is_regional_match:
        return 0.95

    # Check relocation suitability
    if willing_to_relocate:
        return 0.85

    return 0.50
