from typing import List, Dict

# Skill mapping to map variants to canonical skill terms
SKILL_ALIASES = {
    "pytorch": ["torch"],
    "tensorflow": ["tf"],
    "retrieval": [
        "semantic search",
        "embeddings-based retrieval",
        "information retrieval",
    ],
    "fastapi": ["rest api", "web api"],
    "vector search": [
        "faiss",
        "vector database",
        "pinecone",
        "milvus",
        "qdrant",
        "weaviate",
    ],
    "machine learning": ["ml", "deep learning"],
}

# Baseline technical terms dictionary
MUST_HAVE_KEYS = {
    "python",
    "faiss",
    "bm25",
    "vector search",
    "retrieval",
    "embeddings",
    "nlp",
    "ndcg",
    "mrr",
    "map",
    "evaluation",
    "machine learning",
}

NICE_TO_HAVE_KEYS = {
    "docker",
    "aws",
    "gcp",
    "mlflow",
    "mlops",
    "bento_ml",
    "fine-tuning",
    "lora",
    "qlora",
    "peft",
    "distributed systems",
    "xgboost",
    "lightgbm",
    "pytorch",
    "tensorflow",
    "fastapi",
    "kubernetes",
}


class SkillExtractor:
    @staticmethod
    def extract_skills(text: str) -> Dict[str, List[str]]:
        """
        Scans lowercased JD text to extract must-have and nice-to-have skills,
        expanding search matching using alias configurations.
        """
        text_lower = text.lower()
        extracted_canonical = set()

        # 1. Expand search vocabulary and test matches
        # Check canonical core vocabularies first
        all_vocab = MUST_HAVE_KEYS.union(NICE_TO_HAVE_KEYS)
        for skill in all_vocab:
            if skill in text_lower:
                extracted_canonical.add(skill)

        # 2. Check alias vocab mappings
        for canonical, aliases in SKILL_ALIASES.items():
            # If the canonical term itself matches
            if canonical in text_lower:
                extracted_canonical.add(canonical)
            # Or if any of its aliases match
            for alias in aliases:
                if alias in text_lower:
                    extracted_canonical.add(canonical)
                    break

        # 3. Categorize into Must-Have vs. Nice-to-Have lists
        must_have = []
        nice_to_have = []

        for skill in extracted_canonical:
            if skill in MUST_HAVE_KEYS:
                must_have.append(skill)
            elif skill in NICE_TO_HAVE_KEYS:
                nice_to_have.append(skill)

        return {
            "must_have_skills": sorted(must_have),
            "nice_to_have_skills": sorted(nice_to_have),
        }


if __name__ == "__main__":
    test_jd = "We need an engineer experienced in Python, ML and faiss. Familiarity with rest api and docker is a plus."
    print("Test JD text:")
    print(test_jd)
    skills = SkillExtractor.extract_skills(test_jd)
    print("\nExtracted Skills:")
    print(skills)
