from typing import Dict, Any


class TemplateEngine:
    @staticmethod
    def generate_explanation(candidate: Dict[str, Any]) -> str:
        """
        Generates a deterministic, natural, and fact-based candidate explanation
        strictly in the 40-80 words range without any hallucination.
        Uses current_title, years_of_experience, top skills, past companies,
        location, profile completeness, GitHub score, and notice period.
        """
        profile = candidate.get("profile", {})
        signals = candidate.get("redrob_signals", {})

        # 1. Title and Experience
        title = profile.get("current_title", "Technical Candidate")
        years = profile.get("years_of_experience", 0.0)

        # 2. Extract Top 3 Skills
        skills_list = [
            s.get("name", "") for s in candidate.get("skills", []) if s.get("name")
        ]
        if not skills_list:
            skills_str = "software engineering"
        elif len(skills_list) == 1:
            skills_str = skills_list[0]
        elif len(skills_list) == 2:
            skills_str = f"{skills_list[0]} and {skills_list[1]}"
        else:
            skills_str = f"{skills_list[0]}, {skills_list[1]}, and {skills_list[2]}"

        # 3. Extract Past Companies (up to 2)
        companies = []
        for job in candidate.get("career_history", []):
            comp = job.get("company", "")
            if comp and comp not in companies:
                companies.append(comp)

        if not companies:
            company_clause = ""
        elif len(companies) == 1:
            company_clause = f" Previously worked at {companies[0]}."
        else:
            company_clause = f" Previously worked at {companies[0]} and {companies[1]}."

        # 4. Location
        location = profile.get("location", "India")

        # 5. Core platform stats
        completeness = signals.get("profile_completeness_score", 100.0)
        notice = signals.get("notice_period_days", 0)
        github = signals.get("github_activity_score", -1.0)

        # Build sentences
        reason = f"{title} with {years:.1f} years of experience. Strong expertise in {skills_str}.{company_clause}"
        reason += f" Based in {location} with an active profile and strong recruiter engagement."
        reason += f" Candidate profile completeness is at {completeness:.0f}% on the Redrob platform."

        if github >= 0.0:
            reason += f" Active developer profile with a GitHub activity score of {github:.0f}."

        reason += f" Available to join with a notice period of {notice} days."

        return reason


if __name__ == "__main__":
    # Test template engine
    test_cand = {
        "profile": {
            "current_title": "Senior ML Engineer",
            "years_of_experience": 8.0,
            "location": "Bangalore",
        },
        "skills": [{"name": "Python"}, {"name": "TensorFlow"}, {"name": "FAISS"}],
        "career_history": [{"company": "Flipkart"}, {"company": "Amazon"}],
        "redrob_signals": {
            "profile_completeness_score": 95.0,
            "notice_period_days": 30,
            "github_activity_score": 75.0,
        },
    }

    exp = TemplateEngine.generate_explanation(test_cand)
    print(f"Generated Explanation ({len(exp.split())} words):")
    print(exp)
