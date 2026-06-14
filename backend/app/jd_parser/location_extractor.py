import re
from typing import List

# Vocabulary of locations to scan for
TARGET_LOCATIONS = {
    "noida", "pune", "bangalore", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon", "chennai"
}

class LocationExtractor:
    @staticmethod
    def extract_locations(text: str) -> List[str]:
        """
        Scans lowercased JD text to identify candidate location preferences.
        """
        text_lower = text.lower()
        matched_locations = set()
        
        for loc in TARGET_LOCATIONS:
            # Match location names with word boundary to avoid partial substring matching
            if re.search(rf"\b{loc}\b", text_lower):
                matched_locations.add(loc)
                
        # Normalize "delhi" / "ncr" / "gurgaon" if appropriate or return clean list
        return sorted(list(matched_locations))

if __name__ == "__main__":
    test_text = "The role is based in Pune or Noida, India. We also consider remote candidates in Bangalore."
    print("Test Input:")
    print(test_text)
    print("\nExtracted Locations:")
    print(LocationExtractor.extract_locations(test_text))
