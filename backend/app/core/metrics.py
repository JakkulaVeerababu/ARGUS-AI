import threading
from typing import Dict, List
from fastapi import APIRouter

router = APIRouter()


class MetricsCollector:
    """Thread-safe collector for server performance metrics."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MetricsCollector, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self.request_count = 0
            self.error_count = 0
            self.cache_hits = 0
            self.cache_misses = 0

            self.latencies: List[float] = []
            self.inference_latencies: List[float] = []
            self.max_records = 1000  # Avoid memory leaks by capping metrics history

    def record_request(self, latency: float, success: bool = True):
        with self._lock:
            self.request_count += 1
            if not success:
                self.error_count += 1
            self.latencies.append(latency)
            if len(self.latencies) > self.max_records:
                self.latencies.pop(0)

    def record_inference(self, latency: float):
        with self._lock:
            self.inference_latencies.append(latency)
            if len(self.inference_latencies) > self.max_records:
                self.inference_latencies.pop(0)

    def record_cache_hit(self):
        with self._lock:
            self.cache_hits += 1

    def record_cache_miss(self):
        with self._lock:
            self.cache_misses += 1

    def get_stats(self) -> Dict:
        with self._lock:

            def percentile(data: List[float], percent: float) -> float:
                if not data:
                    return 0.0
                sorted_data = sorted(data)
                k = (len(sorted_data) - 1) * percent
                f = int(k)
                c = f + 1
                if c < len(sorted_data):
                    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])
                return sorted_data[f]

            avg_lat = (
                sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
            )
            p50_lat = percentile(self.latencies, 0.50)
            p90_lat = percentile(self.latencies, 0.90)
            p99_lat = percentile(self.latencies, 0.99)

            avg_inf = (
                sum(self.inference_latencies) / len(self.inference_latencies)
                if self.inference_latencies
                else 0.0
            )

            total_cache_reqs = self.cache_hits + self.cache_misses
            cache_hit_rate = (
                (self.cache_hits / total_cache_reqs) if total_cache_reqs > 0 else 0.0
            )

            return {
                "request_metrics": {
                    "total_requests": self.request_count,
                    "failed_requests": self.error_count,
                    "avg_latency_seconds": round(avg_lat, 4),
                    "p50_latency_seconds": round(p50_lat, 4),
                    "p90_latency_seconds": round(p90_lat, 4),
                    "p99_latency_seconds": round(p99_lat, 4),
                },
                "cache_metrics": {
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                    "hit_rate": round(cache_hit_rate, 4),
                },
                "inference_metrics": {
                    "total_inferences": len(self.inference_latencies),
                    "avg_inference_latency_seconds": round(avg_inf, 4),
                },
            }


metrics_collector = MetricsCollector()


@router.get("/metrics")
def get_metrics():
    """Returns application performance telemetry and statistics."""
    return metrics_collector.get_stats()
