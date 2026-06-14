import pytest
import numpy as np
import threading
from backend.app.inference.model_manager import ModelManager
from backend.app.inference.embedding_service import EmbeddingService
from backend.app.inference.cross_encoder_service import CrossEncoderService
from backend.app.inference.batch_scheduler import CrossEncoderScheduler, EmbeddingScheduler

def test_model_manager_singleton():
    manager1 = ModelManager()
    manager2 = ModelManager()
    assert manager1 is manager2

def test_embedding_service_inference():
    service = EmbeddingService()
    
    # Test single text
    text = "python backend developer"
    emb = service.encode(text)
    assert isinstance(emb, np.ndarray)
    assert emb.shape == (384,)
    
    # Test normalization (L2 norm should be close to 1)
    norm = np.linalg.norm(emb)
    assert pytest.approx(norm, abs=1e-5) == 1.0
    
    # Test multiple texts
    texts = ["python developer", "java developer", "data scientist"]
    embs = service.encode(texts)
    assert isinstance(embs, np.ndarray)
    assert embs.shape == (3, 384)
    for i in range(3):
        assert pytest.approx(np.linalg.norm(embs[i]), abs=1e-5) == 1.0

def test_cross_encoder_service_inference():
    service = CrossEncoderService()
    pairs = [
        ("python developer", "experience with django, fastapi and sql"),
        ("python developer", "expert in sales marketing and social media campaigns")
    ]
    scores = service.score_pairs(pairs)
    assert len(scores) == 2
    assert isinstance(scores[0], float)
    assert isinstance(scores[1], float)
    # The first pair should score higher since it is about python dev
    assert scores[0] > scores[1]

def test_schedulers_concurrency():
    ce_scheduler = CrossEncoderScheduler()
    emb_scheduler = EmbeddingScheduler()
    
    # Test CrossEncoderScheduler
    pairs = [
        ("developer", "writing clean code"),
        ("developer", "baking cakes")
    ]
    scores = ce_scheduler.score_pairs(pairs)
    assert len(scores) == 2
    assert scores[0] > scores[1]
    
    # Test EmbeddingScheduler
    texts = ["hello", "world"]
    embs = emb_scheduler.encode(texts)
    assert embs.shape == (2, 384)

    # Test concurrent threads scheduling items
    results = []
    def thread_worker(pair, index):
        res = ce_scheduler.score_pairs([pair])
        results.append((index, res[0]))

    threads = []
    test_pairs = [
        ("engineer", "software development and architecture"),
        ("chef", "cooking recipes in kitchen"),
        ("designer", "ux ui designs and wireframes")
    ]
    for idx, pair in enumerate(test_pairs):
        t = threading.Thread(target=thread_worker, args=(pair, idx))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    assert len(results) == 3
    # Check that they all got float scores
    for idx, score in results:
        assert isinstance(score, float)
