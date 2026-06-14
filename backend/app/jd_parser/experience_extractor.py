import re
from typing import Tuple, Optional


class ExperienceExtractor:
    @staticmethod
    def extract_experience(text: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Parses years of experience requirements from JD text using regular expressions.
        Supports range patterns ("5-9 years") and lower-bound patterns ("3+ years").
        """
        text_lower = text.lower()

        # Pattern 1: Range match (e.g., "5-9 years", "5 to 9 yrs")
        range_match = re.search(
            r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years|yrs|year|yr)", text_lower
        )
        if range_match:
            try:
                min_exp = int(range_match.group(1))
                max_exp = int(range_match.group(2))
                return min_exp, max_exp
            except ValueError:
                pass

        # Pattern 2: Minimum plus match (e.g., "3+ years", "3+ yrs")
        plus_match = re.search(r"(\d+)\s*\+\s*(?:years|yrs|year|yr)", text_lower)
        if plus_match:
            try:
                min_exp = int(plus_match.group(1))
                return min_exp, None
            except ValueError:
                pass

        # Pattern 3: Minimal word bound match (e.g., "at least 5 years")
        at_least_match = re.search(
            r"(?:at least|minimum of)\s*(\d+)\s*(?:years|yrs|year|yr)", text_lower
        )
        if at_least_match:
            try:
                min_exp = int(at_least_match.group(1))
                return min_exp, None
            except ValueError:
                pass

        # Fallback default when no patterns are discovered
        return None, None


if __name__ == "__main__":
    tests = [
        "Required: 5-9 years of applied AI experience.",
        "Expected 3+ years in software engineering.",
        "Must have at least 6 years of experience.",
        "No experience stated.",
    ]
    print("Experience Extraction Tests:")
    for t in tests:
        res = ExperienceExtractor.extract_experience(t)
        print(f"  Text: '{t}' -> Experience: {res}")
