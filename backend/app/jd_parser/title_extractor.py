import re
from typing import List

# Predefined job titles vocabulary
TITLE_VOCABULARY = {
    "ml engineer",
    "machine learning engineer",
    "ai engineer",
    "nlp engineer",
    "deep learning engineer",
    "software engineer",
    "backend engineer",
    "search engineer",
    "recommendation engineer",
    "data engineer",
    "qa engineer",
    "systems engineer",
    "full stack developer",
    "applied ml engineer",
    "developer",
}


class TitleExtractor:
    @staticmethod
    def extract_titles(text: str) -> List[str]:
        """
        Scans lowercased JD text to identify candidate job title expectations.
        """
        text_lower = text.lower()
        matched_titles = set()

        for title in TITLE_VOCABULARY:
            # Word boundary matching
            if re.search(rf"\b{title}\b", text_lower):
                matched_titles.add(title)

        return sorted(list(matched_titles))


if __name__ == "__main__":
    test_text = "Looking for a Senior ML Engineer or AI Engineer to join our team."
    print("Test Input:")
    print(test_text)
    print("\nExtracted Titles:")
    print(TitleExtractor.extract_titles(test_text))
