from typing import Dict, Any
from backend.app.reasoning.template_engine import TemplateEngine


def build_candidate_reasoning(candidate: Dict[str, Any], rank: int) -> str:
    """
    Wrapper function that calls the TemplateEngine to compile
    a natural, fact-based reasoning string for the submission.
    """
    return TemplateEngine.generate_explanation(candidate)
