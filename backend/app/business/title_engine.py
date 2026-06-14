"""
Purpose: Computes semantic job title match score using sentence embedding similarity.
Inputs:
    - candidate_title: str
    - target_titles: List[str]
    - model: Optional[SentenceTransformer] (shared encoder reference)
Outputs:
    - float score in range [0.0, 1.0].
Complexity: O(D) vector cosine similarity calculations.
Production Concerns: Avoid loading SentenceTransformer on demand (model reloading causes latency/OOM); fallback gracefully when model is unavailable.
Future Improvements: Maintain a taxonomy mapping (e.g., matching "ML Engineer" to "Data Scientist" using a hierarchy graph).
"""

import re
from typing import List, Any


def get_token_overlap(str1: str, str2: str) -> float:
    """Fallback token overlap calculator."""
    tokens1 = set(re.findall(r"\b\w+\b", str1.lower()))
    tokens2 = set(re.findall(r"\b\w+\b", str2.lower()))
    if not tokens1 or not tokens2:
        return 0.0
    return len(tokens1.intersection(tokens2)) / min(len(tokens1), len(tokens2))


def calculate_title_score(
    candidate_title: str, target_titles: List[str], model: Any = None
) -> float:
    """
    Computes title match score.
    - If target_titles list is empty, returns 1.0.
    - If model is provided, computes embedding cosine similarity and returns the maximum similarity.
    - If model is None, falls back to token overlap.
    """
    cand_title_clean = candidate_title.strip().lower()
    targets_clean = [t.strip().lower() for t in target_titles if t.strip()]

    if not targets_clean:
        return 1.0

    # Check exact match directly
    if cand_title_clean in targets_clean:
        return 1.0

    # Semantic Matching using shared SentenceTransformer
    if model is not None:
        try:
            import numpy as np

            # Encode candidate title
            cand_emb = model.encode(
                [candidate_title],
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )[0]

            # Encode target titles
            target_embs = model.encode(
                target_titles,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

            # Since vectors are normalized, inner product is Cosine Similarity
            similarities = np.dot(target_embs, cand_emb)
            max_sim = float(np.max(similarities))

            # Clip between [0.0, 1.0]
            return max(0.0, min(1.0, max_sim))

        except Exception:
            # Fallback to token overlap on model failure
            pass

    # Fallback to token overlap similarity
    best_overlap = 0.0
    for target in targets_clean:
        overlap = get_token_overlap(cand_title_clean, target)
        if overlap > best_overlap:
            best_overlap = overlap

    return best_overlap
