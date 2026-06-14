import os
import time
from typing import List, Dict, Any, Tuple
from backend.app.retrieval.bm25_search import BM25Search
from backend.app.retrieval.semantic_search import SemanticSearch

class HybridSearcher:
    def __init__(self, bm25_path: str = None, faiss_path: str = None, ids_path: str = None):
        print("Initializing Hybrid Searcher...")
        start_time = time.time()
        # Initialize lexical branch
        self.bm25_branch = BM25Search(cache_path=bm25_path)
        # Initialize semantic branch
        self.semantic_branch = SemanticSearch(index_path=faiss_path, ids_path=ids_path)
        print(f"Hybrid Searcher initialized in {time.time() - start_time:.2f} seconds.")

    def search(self, query: str, top_k_branch: int = 1000, final_top_n: int = 2000, k_rrf: int = 60) -> List[Tuple[str, float]]:
        """
        Executes hybrid search:
        1. BM25 retrieves top_k_branch candidates.
        2. Semantic FAISS retrieves top_k_branch candidates.
        3. Reciprocal Rank Fusion (RRF) combines rankings.
        4. Sorts and returns top final_top_n candidates.
        """
        start_time = time.time()
        
        # 1. Retrieve Lexical matches
        bm25_results = self.bm25_branch.search(query, top_k=top_k_branch)
        
        # 2. Retrieve Semantic matches
        semantic_results = self.semantic_branch.search(query, top_k=top_k_branch)
        
        # 3. Apply Reciprocal Rank Fusion
        rrf_scores: Dict[str, float] = {}
        
        for rank, (cid, _) in enumerate(bm25_results, 1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k_rrf + rank)
            
        for rank, (cid, _) in enumerate(semantic_results, 1):
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + 1.0 / (k_rrf + rank)
            
        # 4. Sort with deterministic tie-breaking (RRF score desc, candidate_id asc)
        sorted_candidates = sorted(
            rrf_scores.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        final_results = sorted_candidates[:final_top_n]
        print(f"Hybrid search query executed in {time.time() - start_time:.4f} seconds.")
        return final_results

if __name__ == "__main__":
    try:
        searcher = HybridSearcher()
        query = "python faiss vector search retrieval ndcg"
        results = searcher.search(query, top_k_branch=1000, final_top_n=5)
        print(f"\nHybrid Search Top 5 for '{query}':")
        for cid, score in results:
            print(f"  {cid} - RRF Score: {score:.6f}")
    except Exception as e:
        print(f"Error: {e}")
