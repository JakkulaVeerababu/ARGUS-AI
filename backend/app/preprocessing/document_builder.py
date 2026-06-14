from typing import Dict, Any
from backend.app.preprocessing.text_cleaner import clean_text

def build_candidate_document(candidate: Dict[str, Any]) -> str:
    """
    Compiles candidate records into a single textual document for vector/BM25 retrieval.
    Builds a structured output containing current role, skills, experience description, and education.
    """
    profile = candidate.get("profile", {})
    current_title = profile.get("current_title", "")
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")
    current_company = profile.get("current_company", "")
    current_industry = profile.get("current_industry", "")
    
    # 1. Skills compilation (including proficiency to add weight)
    skills = candidate.get("skills", [])
    skill_parts = []
    for s in skills:
        name = s.get("name", "")
        prof = s.get("proficiency", "")
        skill_parts.append(f"{name} ({prof})")
    skills_str = ", ".join(skill_parts)
    
    # 2. Career history compilation (Titles, Companies, Descriptions)
    career = candidate.get("career_history", [])
    past_roles = []
    past_companies = []
    descriptions = []
    
    for job in career:
        title = job.get("title", "")
        company = job.get("company", "")
        desc = job.get("description", "")
        
        if title:
            past_roles.append(title)
        if company:
            past_companies.append(company)
        if desc:
            descriptions.append(f"role of {title} at {company}: {desc}")
            
    past_roles_str = ", ".join(past_roles)
    past_companies_str = ", ".join(past_companies)
    descriptions_str = " | ".join(descriptions)
    
    # 3. Education compilation
    education = candidate.get("education", [])
    edu_parts = []
    for e in education:
        deg = e.get("degree", "")
        field = e.get("field_of_study", "")
        inst = e.get("institution", "")
        edu_parts.append(f"{deg} in {field} from {inst}")
    edu_str = ", ".join(edu_parts)
    
    # 4. Certifications compilation
    certs = candidate.get("certifications", [])
    cert_parts = []
    for c in certs:
        cname = c.get("name", "")
        cissuer = c.get("issuer", "")
        cert_parts.append(f"{cname} by {cissuer}")
    certs_str = ", ".join(cert_parts)
    
    # Construct structured paragraph blocks
    raw_document = (
        f"{current_title}\n\n"
        f"{headline}\n\n"
        f"{summary}\n\n"
        f"Current Company:\n{current_company}\n\n"
        f"Industry:\n{current_industry}\n\n"
        f"Skills:\n{skills_str}\n\n"
        f"Past Roles:\n{past_roles_str}\n\n"
        f"Past Companies:\n{past_companies_str}\n\n"
        f"Role Descriptions:\n{descriptions_str}\n\n"
        f"Education:\n{edu_str}\n\n"
        f"Certifications:\n{certs_str}"
    )
    
    return clean_text(raw_document)
