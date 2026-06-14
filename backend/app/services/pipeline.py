import os
import json
import gzip
import time
from typing import Generator, Dict, Any, List
from backend.app.models.candidate import Candidate


class DatasetLoader:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def stream_candidates(self) -> Generator[Dict[str, Any], None, None]:
        """Streams raw dictionaries from candidate jsonl file (gzip-aware)."""
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
                yield json.loads(line_str)

    def load_and_validate_all(self, max_records: int = -1) -> List[Candidate]:
        """Loads and validates candidates using Pydantic schemas."""
        candidates = []
        count = 0
        for raw in self.stream_candidates():
            cand = Candidate(**raw)
            candidates.append(cand)
            count += 1
            if max_records > 0 and count >= max_records:
                break
        return candidates


def compile_candidate_document(raw_cand: Dict[str, Any]) -> str:
    """
    Compiles candidate profiles into a single semantic document string.
    This captures title, headline, summary, skill lists, and past role descriptions.
    It preserves punctuation for Bi-Encoder and provides explicit term density for BM25.
    """
    profile = raw_cand.get("profile", {})
    title = profile.get("current_title", "")
    headline = profile.get("headline", "")
    summary = profile.get("summary", "")

    # Skills compilation (including duration and proficiency for query matching)
    skills = raw_cand.get("skills", [])
    skill_parts = []
    for s in skills:
        name = s.get("name", "")
        prof = s.get("proficiency", "")
        dur = s.get("duration_months", 0)
        skill_parts.append(f"{name} ({prof}, {dur}m)")
    skills_str = ", ".join(skill_parts)

    # Past career history (critical for identifying product experience vs. keyword stuffer)
    career = raw_cand.get("career_history", [])
    history_parts = []
    for j in career:
        j_company = j.get("company", "")
        j_title = j.get("title", "")
        j_desc = j.get("description", "")
        history_parts.append(f"Held role of {j_title} at {j_company}: {j_desc}")
    history_str = " | ".join(history_parts)

    # Academic history
    education = raw_cand.get("education", [])
    edu_parts = []
    for e in education:
        deg = e.get("degree", "")
        field = e.get("field_of_study", "")
        inst = e.get("institution", "")
        edu_parts.append(f"{deg} in {field} from {inst}")
    edu_str = ", ".join(edu_parts)

    # Assemble unified representation
    doc_parts = [
        f"Candidate Title: {title}.",
        f"Headline: {headline}.",
        f"Summary: {summary}.",
        f"Skills List: {skills_str}.",
        f"Experience History: {history_str}.",
        f"Education History: {edu_str}.",
    ]
    return " ".join(doc_parts)


def test_preprocessing():
    """Benchmarks preprocessing speed and logs document output format."""
    default_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../data/candidates.jsonl")
    )
    loader = DatasetLoader(default_path)

    print("Testing candidate text compilation...")
    start_time = time.time()

    count = 0
    sample_doc = ""
    for raw in loader.stream_candidates():
        doc = compile_candidate_document(raw)
        count += 1
        if count == 1:
            sample_doc = doc
        if count >= 10000:
            break

    end_time = time.time()
    elapsed = end_time - start_time

    print("\n--- Preprocessing Test Results ---")
    print(f"Compiled {count} candidate documents in {elapsed:.2f} seconds.")
    print(f"Processing throughput: {count / elapsed:.1f} documents/sec")
    print("\nSample Document Output (First Candidate):")
    print(sample_doc[:1200] + "...")


if __name__ == "__main__":
    test_preprocessing()
