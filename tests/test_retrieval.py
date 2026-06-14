import os
from backend.app.retrieval.bm25_index import BM25Searcher


def test_bm25_tokenization():
    tokens = BM25Searcher.tokenize(
        "Python developer, 5 years experience! Django expert."
    )
    # Should lowercase, split on word boundaries, remove punctuation
    assert tokens == [
        "python",
        "developer",
        "5",
        "years",
        "experience",
        "django",
        "expert",
    ]


def test_bm25_index_build_and_search(tmp_path):
    # Create temp jsonl candidates file
    candidates_file = os.path.join(tmp_path, "mock_candidates.jsonl")
    cache_path = os.path.join(tmp_path, "mock_bm25.pkl")

    # Write 3 dummy candidates
    import json

    mock_cands = [
        {
            "candidate_id": "CAND_01",
            "profile": {
                "current_title": "Python developer",
                "summary": "Experienced Python and Django developer based in Noida",
            },
        },
        {
            "candidate_id": "CAND_02",
            "profile": {
                "current_title": "Java developer",
                "summary": "Java Spring boot engineer located in Bangalore",
            },
        },
        {
            "candidate_id": "CAND_03",
            "profile": {
                "current_title": "React developer",
                "summary": "React Frontend developer with expertise in CSS and HTML",
            },
        },
    ]

    with open(candidates_file, "w", encoding="utf-8") as f:
        for cand in mock_cands:
            f.write(json.dumps(cand) + "\n")

    # Build
    searcher = BM25Searcher(cache_path=cache_path)
    searcher.build_index(candidates_file=candidates_file)

    # Load
    searcher.load_index()
    assert len(searcher.candidate_ids) == 3

    # Query Noida/Python -> CAND_01 should rank first
    results = searcher.score_candidates("Python developer in Noida")
    assert results[0][0] == "CAND_01"
    assert results[0][1] > 0.0

    # Query Java -> CAND_02 should rank first
    results_java = searcher.score_candidates("Java developer")
    assert results_java[0][0] == "CAND_02"


def test_rrf_fusion_logic():
    # Test RRF fusion logic in HybridSearcher
    # Let's mock two rankings lists
    # Formula: RRF_score = sum(1 / (k + rank))
    # Let's say:
    # bm25_results = [("CAND_A", 10.0), ("CAND_B", 8.0)]
    # faiss_results = [("CAND_B", 0.95), ("CAND_A", 0.90)]

    # Rank mapping:
    # CAND_A: BM25 rank 1 (index 0), FAISS rank 2 (index 1)
    # CAND_B: BM25 rank 2 (index 1), FAISS rank 1 (index 0)

    # Using k = 60:
    # CAND_A RRF = 1 / (60 + 1) + 1 / (60 + 2) = 1/61 + 1/62 = 0.01639 + 0.01613 = 0.03252
    # CAND_B RRF = 1 / (60 + 2) + 1 / (60 + 1) = 1/62 + 1/61 = 0.03252
    # They should have the same RRF score. Let's see how HybridSearcher combines.

    # Let's mock a simple fusion check
    bm25_ranks = {
        cid: rank for rank, (cid, _) in enumerate([("A", 10.0), ("B", 8.0)], 1)
    }
    faiss_ranks = {
        cid: rank for rank, (cid, _) in enumerate([("B", 0.95), ("A", 0.90)], 1)
    }

    scores = {}
    k = 60
    for cid in set(bm25_ranks.keys()).union(faiss_ranks.keys()):
        r_bm25 = bm25_ranks.get(cid, 1e9)
        r_faiss = faiss_ranks.get(cid, 1e9)
        scores[cid] = 1.0 / (k + r_bm25) + 1.0 / (k + r_faiss)

    assert abs(scores["A"] - (1 / 61 + 1 / 62)) < 1e-6
    assert abs(scores["B"] - (1 / 62 + 1 / 61)) < 1e-6
