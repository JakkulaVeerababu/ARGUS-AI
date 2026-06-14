import hashlib
from backend.app.reasoning_v2.template_registry import TEMPLATES

def select_template(candidate_id: str) -> str:
    """
    Selects a template layout deterministically using MD5 hashing of candidate_id.
    Never uses randomness, ensuring reproducible outputs.
    """
    if not candidate_id:
        return TEMPLATES[0]
    hash_val = int(hashlib.md5(candidate_id.encode('utf-8')).hexdigest(), 16)
    idx = hash_val % len(TEMPLATES)
    return TEMPLATES[idx]
