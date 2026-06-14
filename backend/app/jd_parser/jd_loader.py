import os
from backend.app.utils.docx import parse_docx_text

class JDLoader:
    def __init__(self, default_path: str = None):
        self.default_path = default_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/job_description.docx")
        )

    def load_jd(self, file_path: str = None) -> str:
        """Loads and returns the text representation of the JD docx file."""
        target_path = file_path or self.default_path
        if not os.path.exists(target_path):
            raise FileNotFoundError(f"Job Description file not found at: {target_path}")
        return parse_docx_text(target_path)

if __name__ == "__main__":
    loader = JDLoader()
    try:
        raw_text = loader.load_jd()
        print("Successfully loaded JD!")
        print(f"Text Length: {len(raw_text)}")
    except Exception as e:
        print(f"Error: {e}")
