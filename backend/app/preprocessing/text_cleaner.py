import re

def clean_text(text: str) -> str:
    """
    Cleans raw text:
    1. Converts to lowercase.
    2. Preserves technical words containing symbols like C++ and C#.
    3. Normalizes all whitespace (newlines, tabs) to single spaces.
    4. Avoids aggressive stemming or stopword removal to preserve transformer semantics.
    """
    if not text:
        return ""
    
    # Lowercase case normalization
    text = text.lower()
    
    # Replace newlines, carriage returns, and tabs with spaces
    text = re.sub(r"[\r\n\t]+", " ", text)
    
    # Remove duplicate spaces
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()

if __name__ == "__main__":
    test_text = "Senior AI Engineer\nWorking with PyTorch, C++ and C#.\n   Lots of   spaces here!   "
    print("Test Input:")
    print(repr(test_text))
    print("\nTest Output:")
    print(repr(clean_text(test_text)))
