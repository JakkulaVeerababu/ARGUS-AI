"""
Purpose: Query Builder to compile parsed JD requirements into optimized FTS5 MATCH queries.
Inputs:
    - parsed_jd: JDRequirementsSchema / Dict[str, Any]
Outputs:
    - str (FTS5 MATCH statement expression)
Complexity: O(R) where R is the number of requirement terms.
Production Concerns: Sanitizing terms to remove punctuation that breaks FTS MATCH queries.
Future Improvements: Support field-specific MATCH patterns (e.g. searching location fields specifically).
"""

import re
from typing import Any, List


def clean_term(term: str) -> str:
    """Removes special characters to prevent FTS syntax errors."""
    return re.sub(r"[^\w\s]", " ", term).strip()


def build_fts_query(parsed_jd: Any) -> str:
    """
    Transforms parsed JD requirements (skills, titles, locations, companies)
    into a unified FTS5 MATCH expression.
    Terms are grouped and joined with OR operators to maximize recall.
    """
    terms: List[str] = []

    # Extract lists safely
    must_skills = []
    nice_skills = []
    locations = []
    titles = []
    companies = []

    if isinstance(parsed_jd, dict):
        must_skills = parsed_jd.get("must_have_skills", [])
        nice_skills = parsed_jd.get("nice_to_have_skills", [])
        locations = parsed_jd.get("locations", [])
        titles = parsed_jd.get("titles", [])
        companies = parsed_jd.get("companies", [])
    else:
        # Pydantic schema instance
        must_skills = getattr(parsed_jd, "must_have_skills", [])
        nice_skills = getattr(parsed_jd, "nice_to_have_skills", [])
        locations = getattr(parsed_jd, "locations", [])
        titles = getattr(parsed_jd, "titles", [])
        companies = getattr(parsed_jd, "companies", [])

    # Append must-have skills
    for s in must_skills:
        ct = clean_term(s)
        if ct:
            # Multi-word terms are put in double quotes for phrase matching
            if " " in ct:
                terms.append(f'"{ct}"')
            else:
                terms.append(ct)

    # Append nice-to-have skills
    for s in nice_skills:
        ct = clean_term(s)
        if ct:
            if " " in ct:
                terms.append(f'"{ct}"')
            else:
                terms.append(ct)

    # Append titles
    for t in titles:
        ct = clean_term(t)
        if ct:
            if " " in ct:
                terms.append(f'"{ct}"')
            else:
                terms.append(ct)

    # Append locations
    for loc in locations:
        ct = clean_term(loc)
        if ct:
            if " " in ct:
                terms.append(f'"{ct}"')
            else:
                terms.append(ct)

    # Append companies
    for c in companies:
        ct = clean_term(c)
        if ct:
            if " " in ct:
                terms.append(f'"{ct}"')
            else:
                terms.append(ct)

    if not terms:
        return ""

    # Join with OR to return a unified recall-maximizing match expression
    return " OR ".join(terms)
