import os
import json
import gzip
from typing import Generator, Dict, Any, List
from backend.app.preprocessing.candidate_parser import parse_candidate


class CandidateLoader:
    def __init__(self, filepath: str = None):
        # Default target dataset location
        self.filepath = filepath or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/candidates.jsonl")
        )

    def stream_candidates(self) -> Generator[Dict[str, Any], None, None]:
        """
        Streams candidate profiles line-by-line to prevent high memory usage.
        Supports both plain jsonl and gzip formats.
        """
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Candidate dataset not found at: {self.filepath}")

        if self.filepath.endswith(".gz"):
            open_func = gzip.open
            mode = "rt"
        else:
            open_func = open
            mode = "r"

        with open_func(self.filepath, mode, encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                # Load dictionary and yield parsed candidate representation
                yield parse_candidate(json.loads(line_str))

    def load_all(self, limit: int = -1) -> List[Dict[str, Any]]:
        """Loads all parsed candidate representations into RAM."""
        candidates = []
        count = 0
        for parsed in self.stream_candidates():
            candidates.append(parsed)
            count += 1
            if limit > 0 and count >= limit:
                break
        return candidates


if __name__ == "__main__":
    # Diagnostic test for memory-safe loader
    loader = CandidateLoader()
    print("Streaming first 3 parsed candidates:")
    try:
        count = 0
        for cand in loader.stream_candidates():
            print(json.dumps(cand, indent=2))
            count += 1
            if count >= 3:
                break
    except Exception as e:
        print(f"Error during streaming: {e}")
