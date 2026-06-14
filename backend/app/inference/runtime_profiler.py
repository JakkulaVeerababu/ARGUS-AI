import time
from contextlib import contextmanager

class RuntimeProfiler:
    def __init__(self):
        self.metrics = {
            "embedding_time": 0.0,
            "faiss_time": 0.0,
            "cross_encoder_time": 0.0,
            "total_latency": 0.0
        }
        self.start_time = None

    def start(self):
        """Starts timing the overall search request."""
        self.start_time = time.time()

    def stop(self):
        """Stops timing and calculates the total latency."""
        if self.start_time:
            self.metrics["total_latency"] = time.time() - self.start_time

    @contextmanager
    def track(self, key: str):
        """Context manager to measure the latency of a block of code."""
        start = time.time()
        try:
            yield
        finally:
            elapsed = time.time() - start
            if key in self.metrics:
                self.metrics[key] += elapsed
            else:
                self.metrics[key] = elapsed

    def get_report(self) -> dict:
        """Returns the rounded timing metrics in seconds."""
        return {k: round(v, 4) for k, v in self.metrics.items()}
