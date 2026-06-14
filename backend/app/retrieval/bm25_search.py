from typing import List, Tuple
from backend.app.retrieval.bm25_index import BM25Searcher


class BM25Search:
    def __init__(self, cache_path: str = None):
        self.searcher = BM25Searcher(cache_path=cache_path)
        self.searcher.load_index()

    def search(self, query: str, top_k: int = 1000) -> List[Tuple[str, float]]:
        """
        Retrieves the top K candidates matching the query using the BM25 index.
        Returns a list of tuples: (candidate_id, bm25_score)
        """
        scores = self.searcher.score_candidates(query)
        return scores[:top_k]


if __name__ == "__main__":
    try:
        searcher = BM25Search()
        query = "python faiss vector search retrieval ndcg"
        results = searcher.search(query, top_k=5)
        print(f"BM25 Search Top 5 for '{query}':")
        for cid, score in results:
            print(f"  {cid} - Score: {score:.4f}")
    except Exception as e:
        print(f"Error: {e}")
