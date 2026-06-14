from typing import Dict, Any, List, Optional

def explain_location(candidate: Dict[str, Any], target_locations: Optional[List[str]] = None) -> str:
    """
    Generates a deterministic location clause based on actual geography and relocation settings.
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    
    loc = profile.get("location", "").strip()
    if not loc:
        loc = "India"
        
    is_remote = bool(signals.get("is_remote", False))
    relocate = bool(signals.get("willing_to_relocate", False))
    
    # Check regional target alignment
    matched = False
    if target_locations:
        loc_lower = loc.lower()
        matched = any(t.strip().lower() in loc_lower for t in target_locations if t.strip())
        
    if matched:
        return f"Located in {loc}, which matches the target hiring geography."
    elif is_remote:
        return f"Based in {loc} and supports remote working arrangements."
    elif relocate:
        return f"Based in {loc} and is fully willing to relocate for this position."
    else:
        return f"Geographically positioned in {loc}."
