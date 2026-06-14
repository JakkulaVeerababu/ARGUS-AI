import os
from typing import Dict, Any
from backend.app.jd_parser.jd_loader import JDLoader
from backend.app.jd_parser.skill_extractor import SkillExtractor
from backend.app.jd_parser.experience_extractor import ExperienceExtractor
from backend.app.jd_parser.location_extractor import LocationExtractor
from backend.app.jd_parser.title_extractor import TitleExtractor
from backend.app.jd_parser.exclusion_rules import ExclusionRules

class JDParserEngine:
    def __init__(self, loader: JDLoader = None):
        self.loader = loader or JDLoader()

    def parse(self, file_path: str = None) -> Dict[str, Any]:
        """
        Loads and parses the JD file, executing all sub-extractors sequentially.
        Outputs a clean, structured dictionary of requirements.
        """
        # Step 1: Load Raw Text
        raw_text = self.loader.load_jd(file_path)
        
        # Step 2: Extract Skills (Must-Have vs. Nice-to-Have)
        skills_res = SkillExtractor.extract_skills(raw_text)
        
        # Step 3: Extract Experience Range
        min_exp, max_exp = ExperienceExtractor.extract_experience(raw_text)
        
        # Step 4: Extract Locations
        locations = LocationExtractor.extract_locations(raw_text)
        
        # Step 5: Extract Titles
        titles = TitleExtractor.extract_titles(raw_text)
        
        # Step 6: Extract Exclusions
        excluded_roles = ExclusionRules.get_excluded_roles(raw_text)
        
        # Compile structured output
        return {
            "must_have_skills": skills_res["must_have_skills"],
            "nice_to_have_skills": skills_res["nice_to_have_skills"],
            "experience": (min_exp, max_exp),
            "locations": locations,
            "titles": titles,
            "excluded_roles": excluded_roles
        }

if __name__ == "__main__":
    # Test on the challenge target JD
    engine = JDParserEngine()
    try:
        parsed_jd = engine.parse()
        print("Successfully parsed Job Description!")
        import json
        # Handle tuple serialization for pretty print
        serializable = parsed_jd.copy()
        serializable["experience"] = list(serializable["experience"])
        print(json.dumps(serializable, indent=2))
    except Exception as e:
        print(f"Error during parsing: {e}")
