"""
Purpose: Redesigned Hybrid Searcher merging SQLite FTS5 (lexical) and FAISS (semantic) branches using Reciprocal Rank Fusion (RRF).
Inputs:
    - bm25_path: str (unused, retained for compatibility)
    - faiss_path: str (path to FAISS index)
    - ids_path: str (unused, ID mappings pulled from SQLite directly)
Outputs:
    - HybridSearcher instance exposing search queries
Complexity: O(log N) search queries.
Production Concerns: Ensure SQLite connections are thread-safe and index mappings align exactly.
Future Improvements: Support dynamic weights tuning instead of RRF default rank constants.
"""

import time
from typing import List, Dict, Tuple
from backend.app.database.fts_index import FTSIndexManager
from backend.app.retrieval.semantic_search import SemanticSearch


class HybridSearcher:
    def __init__(
        self, bm25_path: str = None, faiss_path: str = None, ids_path: str = None
    ):
        print("Initializing SQLite FTS5 & FAISS Hybrid Searcher...")
        start_time = time.time()
        # Initialize FTS5 lexical index manager
        self.fts_branch = FTSIndexManager()
        # Initialize Semantic vector index branch
        self.semantic_branch = SemanticSearch(index_path=faiss_path)
        print(f"Hybrid Searcher initialized in {time.time() - start_time:.2f} seconds.")

    def search(
        self,
        query: str,
        top_k_branch: int = 1000,
        final_top_n: int = 2000,
        k_rrf: int = 60,
    ) -> List[Tuple[str, float]]:
        """
        Executes hybrid search:
        1. FTS5 BM25 retrieves top_k_branch candidates.
        2. Semantic FAISS retrieves top_k_branch candidates.
        3. Reciprocal Rank Fusion (RRF) combines rankings.
        4. Sorts and returns top final_top_n candidates.
        """
        start_time = time.time()

        # 1. Retrieve Lexical matches via SQLite FTS5 index
        fts_results = self.fts_branch.search(query, limit=top_k_branch)

        # 2. Retrieve Semantic matches via FAISS
        semantic_results = self.semantic_branch.search(query, top_k=top_k_branch)

        # 3. Apply Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}

        for rank, (cid, _) in enumerate(fts_results, 1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k_rrf + rank)

        for rank, (cid, _) in enumerate(semantic_results, 1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k_rrf + rank)

        # 4. Sort with deterministic tie-breaking (RRF score desc, candidate_id asc)
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: (-x[1], x[0]))

        final_results = sorted_candidates[:final_top_n]
        print(
            f"Hybrid search query executed in {time.time() - start_time:.4f} seconds."
        )
        return final_results
