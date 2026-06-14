import queue
import threading
import time
from typing import List, Any, Callable, Tuple, Union
from backend.app.inference.cross_encoder_service import CrossEncoderService
from backend.app.inference.embedding_service import EmbeddingService

class BatchScheduler:
    def __init__(self, process_batch_fn: Callable[[List[Any]], List[Any]], max_batch_size: int = 32, max_delay_seconds: float = 0.005):
        self.process_batch_fn = process_batch_fn
        self.max_batch_size = max_batch_size
        self.max_delay_seconds = max_delay_seconds
        
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.running = False
        self.worker_thread = None

    def start(self):
        """Starts the background worker thread."""
        with self.lock:
            if not self.running:
                self.running = True
                self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
                self.worker_thread.start()

    def stop(self):
        """Stops the background worker thread."""
        with self.lock:
            if self.running:
                self.running = False
                self.queue.put(None)
                if self.worker_thread:
                    self.worker_thread.join()
                    self.worker_thread = None

    def schedule(self, item: Any) -> Any:
        """
        Submits a single item for batch processing, blocks until the result is ready.
        """
        results = self.schedule_batch([item])
        return results[0] if results else None

    def schedule_batch(self, items: List[Any]) -> List[Any]:
        """
        Submits multiple items for batch processing, blocks until all are ready.
        Allows concurrent clients to group items in the queue.
        """
        if not items:
            return []
            
        if not self.running:
            self.start()
            
        events = [threading.Event() for _ in items]
        result_holders = [[] for _ in items]
        
        # Enqueue all items with their tracking events
        for item, event, holder in zip(items, events, result_holders):
            self.queue.put((item, event, holder))
            
        # Wait for all items to be processed
        for event in events:
            event.wait()
            
        # Re-assemble results
        results = []
        for holder in result_holders:
            if holder:
                res = holder[0]
                if isinstance(res, Exception):
                    raise res
                results.append(res)
            else:
                results.append(None)
        return results

    def _worker_loop(self):
        """Background loop to pool items and execute them in batches."""
        while self.running:
            try:
                first_item_tuple = self.queue.get()
                if first_item_tuple is None:
                    self.queue.task_done()
                    break
                    
                batch = [first_item_tuple]
                start_time = time.time()
                
                # Pool more items until batch size limit or delay limit is hit
                while len(batch) < self.max_batch_size:
                    time_elapsed = time.time() - start_time
                    time_remaining = max(0.0, self.max_delay_seconds - time_elapsed)
                    
                    try:
                        item_tuple = self.queue.get(timeout=time_remaining)
                        if item_tuple is None:
                            self.queue.put(None)
                            self.queue.task_done()
                            break
                        batch.append(item_tuple)
                    except queue.Empty:
                        break
                
                # Process the gathered batch
                if batch:
                    inputs = [b[0] for b in batch]
                    try:
                        outputs = self.process_batch_fn(inputs)
                        if len(outputs) != len(batch):
                            raise ValueError(f"Batch function returned {len(outputs)} results for {len(batch)} inputs.")
                            
                        for (item, event, holder), output in zip(batch, outputs):
                            holder.append(output)
                            event.set()
                            self.queue.task_done()
                    except Exception as e:
                        print(f"Error processing batch: {e}")
                        for item, event, holder in batch:
                            holder.append(e)
                            event.set()
                            self.queue.task_done()
                            
            except Exception as e:
                print(f"Unexpected error in scheduler worker: {e}")
                time.sleep(0.01)


class CrossEncoderScheduler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CrossEncoderScheduler, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, service: CrossEncoderService = None, max_batch_size: int = 32):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self.service = service or CrossEncoderService()
            self.scheduler = BatchScheduler(
                process_batch_fn=self._process_batch,
                max_batch_size=max_batch_size
            )
            self.scheduler.start()

    def _process_batch(self, batch_pairs: List[Tuple[str, str]]) -> List[float]:
        return self.service.score_pairs(batch_pairs, batch_size=len(batch_pairs))

    def score_pairs(self, pairs: List[Tuple[str, str]]) -> List[float]:
        """Scores multiple query-document pairs in scheduling batches."""
        return self.scheduler.schedule_batch(pairs)


class EmbeddingScheduler:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingScheduler, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self, service: EmbeddingService = None, max_batch_size: int = 32):
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            self.service = service or EmbeddingService()
            self.scheduler = BatchScheduler(
                process_batch_fn=self._process_batch,
                max_batch_size=max_batch_size
            )
            self.scheduler.start()

    def _process_batch(self, texts: List[str]) -> List[Any]:
        # Return list of individual numpy arrays
        embeddings = self.service.encode(texts, batch_size=len(texts))
        return [embeddings[i] for i in range(len(texts))]

    def encode(self, texts: Union[str, List[str]], *args, **kwargs) -> Any:
        import numpy as np
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]
        if not texts:
            empty_emb = np.empty((0, 384), dtype=np.float32)
            return empty_emb[0] if is_single else empty_emb
        results = self.scheduler.schedule_batch(texts)
        stacked = np.vstack(results)
        return stacked[0] if is_single else stacked
