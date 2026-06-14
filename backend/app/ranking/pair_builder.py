from typing import List, Tuple, Dict
from backend.app.preprocessing.candidate_loader import CandidateLoader


class PairBuilder:
    def __init__(self, candidates_file: str = None):
        self.loader = CandidateLoader(candidates_file)

    def build_pairs(
        self, query: str, candidate_ids: List[str]
    ) -> Tuple[List[Tuple[str, str]], List[str]]:
        """
        Reads candidate profiles for the specified candidate_ids,
        and constructs query-document pairs.
        Returns:
            - A list of (query, doc_text) tuples.
            - A list of matching candidate IDs in the exact order of the generated pairs.
        """
        target_ids = set(candidate_ids)
        candidate_docs: Dict[str, str] = {}

        # Stream candidates and extract document text for matched IDs
        for cand in self.loader.stream_candidates():
            cid = cand.get("candidate_id")
            if cid in target_ids:
                candidate_docs[cid] = cand.get("document_text", "")
                # Early stop if we have found all requested profiles
                if len(candidate_docs) >= len(target_ids):
                    break

        # Construct pairs in the exact order of candidate_ids
        pairs = []
        ordered_ids = []
        for cid in candidate_ids:
            if cid in candidate_docs:
                pairs.append((query, candidate_docs[cid]))
                ordered_ids.append(cid)

        return pairs, ordered_ids


if __name__ == "__main__":
    builder = PairBuilder()
    try:
        query = "Python FAISS developer"
        test_ids = ["CAND_0000001", "CAND_0000002"]
        pairs, ids = builder.build_pairs(query, test_ids)
        print(f"Built {len(pairs)} pairs for IDs: {ids}")
    except Exception as e:
        print(f"Error: {e}")
