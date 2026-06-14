from typing import Dict, Any


def check_timeline_violation(candidate: Dict[str, Any]) -> bool:
    """
    Checks if job durations in career history are logically impossible
    compared to the elapsed time between start and end dates.
    Uses June 2026 as the current reference date for ongoing roles.
    """
    career = candidate.get("career_history", [])

    for job in career:
        start = job.get("start_date")
        end = job.get("end_date")
        dur = job.get("duration_months", 0)

        if start:
            try:
                # Format: YYYY-MM-DD
                sy, sm, _ = map(int, start.split("-"))
                if end:
                    ey, em, _ = map(int, end.split("-"))
                else:
                    # Ongoing role - use current local context (June 2026)
                    ey, em = 2026, 6

                elapsed = (ey - sy) * 12 + (em - sm)

                # Allow a margin of 2 months for minor discrepancies
                if dur > elapsed + 2:
                    return True
            except Exception:
                pass

    return False
