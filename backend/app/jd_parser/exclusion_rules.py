import re
from typing import List

# Standard non-technical and administrative titles that are auto-excluded from core ranking
STANDARD_EXCLUDED_ROLES = {
    "project manager", "accountant", "sales executive", "hr", "marketing manager",
    "graphic designer", "content writer", "civil engineer", "mechanical engineer",
    "customer support", "operations manager", "hr manager", "sales", "marketing"
}

class ExclusionRules:
    @staticmethod
    def get_excluded_roles(text: str) -> List[str]:
        """
        Scans lowercased JD text to identify candidate role exclusions.
        Defaults to our standard administrative exclusions if none are explicitly stated in the text.
        """
        text_lower = text.lower()
        matched_exclusions = set()
        
        # Check standard list
        for role in STANDARD_EXCLUDED_ROLES:
            if re.search(rf"\b{role}\b", text_lower):
                matched_exclusions.add(role)
                
        # If no custom exclusions are found in the text, we return the baseline list of excluded roles.
        # This acts as our safety shield.
        if not matched_exclusions:
            return sorted(list(STANDARD_EXCLUDED_ROLES))
            
        return sorted(list(matched_exclusions))

if __name__ == "__main__":
    test_text = "We do not want a Project Manager or Sales manager."
    print("Test Input:")
    print(test_text)
    print("\nMatched Excluded Roles:")
    print(ExclusionRules.get_excluded_roles(test_text))
