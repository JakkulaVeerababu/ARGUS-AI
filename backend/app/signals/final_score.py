import json
import gzip
import math
import time
from typing import List, Tuple, Dict, Any

from backend.app.preprocessing.candidate_loader import CandidateLoader
from backend.app.signals.experience_signal import calculate_experience_factor
from backend.app.signals.role_signal import calculate_role_factor
from backend.app.signals.location_signal import calculate_location_factor
from backend.app.signals.engagement_signal import calculate_engagement_factor
from backend.app.signals.github_signal import calculate_github_factor
from backend.app.signals.notice_period_signal import calculate_notice_factor
from backend.app.signals.profile_quality_signal import calculate_profile_quality_factor


class BusinessScorer:
    def __init__(self, candidates_file: str = None):
        self.loader = CandidateLoader(candidates_file)

    @staticmethod
    def sigmoid(x: float) -> float:
        """Applies sigmoid function to scale logits to range (0, 1)."""
        # Clip to prevent overflow
        x = max(-20.0, min(20.0, x))
        return 1.0 / (1.0 + math.exp(-x))

    def score_candidates(
        self, ce_results: List[Tuple[str, float]], top_n: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Reranks candidates by combining Cross-Encoder scores with business multipliers.
        - Streams the candidate file to load the full profiles of the target IDs.
        - Computes Sigmoid(Cross-Encoder logit) * multipliers.
        - Returns top_n candidates sorted by final score descending (ties broken by ID ascending).
        """
        if not ce_results:
            return []

        print(f"Scoring {len(ce_results)} candidates with business signals...")
        start_time = time.time()

        ce_map = {cid: score for cid, score in ce_results}
        target_ids = set(ce_map.keys())

        # Load raw candidate profiles for target IDs directly
        candidate_profiles = {}
        filepath = self.loader.filepath

        if filepath.endswith(".gz"):
            open_func = gzip.open
            mode = "rt"
        else:
            open_func = open
            mode = "r"

        with open_func(filepath, mode, encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                cand = json.loads(line_str)
                cid = cand.get("candidate_id")
                if cid in target_ids:
                    candidate_profiles[cid] = cand
                    if len(candidate_profiles) >= len(target_ids):
                        break

        # Calculate business scores
        final_scores = []

        for cid, ce_logit in ce_results:
            cand = candidate_profiles.get(cid)
            if not cand:
                continue

            profile = cand.get("profile", {})

            # 1. Scale Cross Encoder score to (0, 1) range
            scaled_ce = self.sigmoid(ce_logit)

            # 2. Compute individual multipliers
            exp_mult = calculate_experience_factor(profile)
            role_mult = calculate_role_factor(cand)
            loc_mult = calculate_location_factor(cand)
            eng_mult = calculate_engagement_factor(cand)
            github_mult = calculate_github_factor(cand)
            notice_mult = calculate_notice_factor(cand)
            quality_mult = calculate_profile_quality_factor(cand)

            # 3. Multiply all factors
            final_val = (
                scaled_ce
                * exp_mult
                * role_mult
                * loc_mult
                * eng_mult
                * github_mult
                * notice_mult
                * quality_mult
            )

            final_scores.append(
                {
                    "candidate_id": cid,
                    "candidate_name": profile.get("anonymized_name", ""),
                    "current_title": profile.get("current_title", ""),
                    "years_of_experience": profile.get("years_of_experience", 0.0),
                    "location": profile.get("location", ""),
                    "cross_encoder_score": ce_logit,
                    "sigmoid_ce_score": scaled_ce,
                    "multipliers": {
                        "experience": exp_mult,
                        "role": role_mult,
                        "location": loc_mult,
                        "engagement": eng_mult,
                        "github": github_mult,
                        "notice": notice_mult,
                        "profile_quality": quality_mult,
                    },
                    "final_score": final_val,
                }
            )

        # Sort by final score descending, tie break by candidate ID ascending
        final_scores.sort(key=lambda x: (-x["final_score"], x["candidate_id"]))

        print(f"Scored and sorted in {time.time() - start_time:.2f} seconds.")
        return final_scores[:top_n]


if __name__ == "__main__":
    scorer = BusinessScorer()
    try:
        # Diagnostic test with sample CE scores
        ce_sample = [
            ("CAND_0000001", 1.5),
            ("CAND_0000002", -2.0),
            ("CAND_0000003", 0.0),
        ]
        results = scorer.score_candidates(ce_sample, top_n=3)
        print("\nScoring Results:")
        for r in results:
            print(
                f"  {r['candidate_id']} - CE: {r['cross_encoder_score']:.2f} -> Sigmoid: {r['sigmoid_ce_score']:.4f} -> Final: {r['final_score']:.4f}"
            )
    except Exception as e:
        print(f"Error: {e}")
