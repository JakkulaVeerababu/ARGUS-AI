"""
Purpose: Computes candidate notice period score using a smooth exponential decay curve.
Inputs:
    - notice_period_days: int
Outputs:
    - float score in range [0.0, 1.0].
Complexity: O(1) mathematical evaluations.
Production Concerns: Inputs must be validated to prevent negative notice periods.
Future Improvements: Support dynamic decay rates (e.g., steeper decay for highly urgent vacancies).
"""

import math


def calculate_notice_score(
    notice_period_days: int, decay_constant: float = 60.0
) -> float:
    """
    Computes notice period scoring using an exponential decay curve.
    Score = exp(-notice_period_days / decay_constant)

    Score Table:
    - 0 days:   1.00
    - 30 days:  0.61
    - 60 days:  0.37
    - 90 days:  0.22
    - 120 days: 0.14
    """
    # Negative notice periods are mapped to 0 days
    days = max(0.0, float(notice_period_days))

    # Calculate exponential decay
    score = math.exp(-days / decay_constant)

    # Clip between [0.0, 1.0]
    return max(0.0, min(1.0, score))
