import time
from typing import List, Tuple
from backend.app.inference.batch_scheduler import CrossEncoderScheduler


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self.scheduler = None

    def load_model(self):
        """Loads the CrossEncoder ONNX scheduler."""
        if self.scheduler is None:
            print(f"Loading CrossEncoder scheduler '{self.model_name}'...")
            start_time = time.time()
            self.scheduler = CrossEncoderScheduler()
            print(
                f"CrossEncoder scheduler loaded in {time.time() - start_time:.2f} seconds."
            )

    def score_pairs(
        self, pairs: List[Tuple[str, str]], batch_size: int = 32
    ) -> List[float]:
        """
        Scores query-document pairs using the ONNX scheduler.
        Input format: [(query, doc_text), (query, doc_text), ...]
        Returns a list of float scores.
        """
        self.load_model()
        if not pairs:
            return []

        start_time = time.time()
        scores = self.scheduler.score_pairs(pairs)
        print(f"Scored {len(pairs)} pairs in {time.time() - start_time:.2f} seconds.")
        return [float(score) for score in scores]


if __name__ == "__main__":
    scorer = CrossEncoderReranker()
    try:
        scorer.load_model()
        pairs = [
            ("python developer", "experience with python, django, postgresql"),
            (
                "python developer",
                "experience with marketing campaigns and sales strategy",
            ),
        ]
        scores = scorer.score_pairs(pairs)
        print(f"Test Scores: {scores}")
    except Exception as e:
        print(f"Error: {e}")
