# Template Registry for Advanced ATS Explainability Engine

TEMPLATES = [
    # 0. Professional
    "Candidate {candidate_id} shows strong alignment as a {title_part} with {experience_part}. {skills_part}{company_part} {location_part} {engagement_part}",
    # 1. Skill-first
    "{skills_part} This matches the technical requirements for the {title_part} role. Candidate {candidate_id} possesses {experience_part}.{company_part} {location_part} {engagement_part}",
    # 2. Experience-first
    "With {experience_part} of tenure as a {title_part}, Candidate {candidate_id} matches the search criteria. {skills_part}{company_part} {location_part} {engagement_part}",
    # 3. Company-first
    "{company_part} Candidate {candidate_id} offers deep {experience_part} as a {title_part}. {skills_part} {location_part} {engagement_part}",
    # 4. Balanced
    "Offers balanced qualifications for the target {title_part} profile, showcasing {experience_part}. {skills_part}{company_part} {location_part} {engagement_part}",
]
