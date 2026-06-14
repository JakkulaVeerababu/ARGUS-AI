import re
import os
from typing import Dict, Any, Set
from backend.app.utils.docx import parse_docx_text

# Define dictionary of core tech and business skills to extract
SKILL_VOCABULARY = {
    "embeddings", "vector search", "faiss", "pinecone", "milvus", "qdrant", 
    "weaviate", "opensearch", "elasticsearch", "sentence-transformers", "nlp", 
    "information retrieval", "python", "ndcg", "mrr", "map", "learning-to-rank", 
    "xgboost", "lightgbm", "fine-tuning", "lora", "qlora", "peft", 
    "distributed systems", "scikit-learn", "mlops", "machine learning"
}

# Define location terms
LOCATION_VOCABULARY = {
    "noida", "pune", "hyderabad", "bangalore", "mumbai", "delhi", "chennai", "ncr", "gurgaon"
}

# Consulting/IT services firms to scan for (in both JD and candidate profiles)
CONSULTING_FIRMS = {
    "tcs", "wipro", "infosys", "accenture", "cognizant", "capgemini", "tech mahindra", "mphasis"
}

class JDExtractor:
    @staticmethod
    def extract_requirements(text: str) -> Dict[str, Any]:
        """
        Extracts structural parameters from JD text.
        Includes experience min/max range, locations, required skills, and consulting disqualifiers.
        """
        text_lower = text.lower()
        
        # 1. Experience Range Extraction (looking for patterns like 5-9 years, 6 to 8 yrs)
        exp_min = 5.0
        exp_max = 9.0
        exp_match = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:years|yrs|year|yr)", text_lower)
        if exp_match:
            try:
                exp_min = float(exp_match.group(1))
                exp_max = float(exp_match.group(2))
            except ValueError:
                pass
        
        # 2. Location Extraction
        matched_locations = set()
        for loc in LOCATION_VOCABULARY:
            # Word boundary matching
            if re.search(rf"\b{loc}\b", text_lower):
                matched_locations.add(loc)
                
        # 3. Skills Keyword Extraction
        matched_skills = set()
        for skill in SKILL_VOCABULARY:
            if skill in text_lower:
                matched_skills.add(skill)
                
        # 4. Consulting Exclusions
        matched_consulting = set()
        for firm in CONSULTING_FIRMS:
            if firm in text_lower:
                matched_consulting.add(firm)
                
        return {
            "experience_range": {
                "min": exp_min,
                "max": exp_max
            },
            "locations": list(matched_locations),
            "skills": list(matched_skills),
            "consulting_firms": list(matched_consulting)
        }

if __name__ == "__main__":
    # Test on the parsed docx
    default_jd_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/job_description.docx"))
    try:
        text = parse_docx_text(default_jd_path)
        reqs = JDExtractor.extract_requirements(text)
        print("Successfully extracted JD requirements!")
        print("\nExperience Required Range:")
        print(f"  Min: {reqs['experience_range']['min']} years")
        print(f"  Max: {reqs['experience_range']['max']} years")
        print("\nLocations Extracted:")
        print(f"  {reqs['locations']}")
        print("\nSkills Identified:")
        print(f"  {reqs['skills']}")
    except Exception as e:
        print(f"Error: {e}")
