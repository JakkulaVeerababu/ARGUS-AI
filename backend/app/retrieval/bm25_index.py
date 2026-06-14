import os
import pickle
import re
from typing import List, Dict, Any, Tuple
from rank_bm25 import BM25Okapi
from backend.app.preprocessing.candidate_loader import CandidateLoader

class BM25Searcher:
    def __init__(self, cache_path: str = None):
        self.cache_path = cache_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../artifacts/bm25_index.pkl")
        )
        self.bm25: BM25Okapi = None
        self.candidate_ids: List[str] = []

    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenizes text: lowercases and splits on alphanumeric word boundaries."""
        return re.findall(r"\b\w+\b", text.lower())

    def build_index(self, candidates_file: str = None):
        """Builds the BM25 index over the preprocessed candidates and saves it."""
        print("Building BM25 index...")
        loader = CandidateLoader(candidates_file)
        
        corpus_tokens = []
        cids = []
        
        for cand in loader.stream_candidates():
            cid = cand.get("candidate_id")
            doc = cand.get("document_text", "")
            corpus_tokens.append(self.tokenize(doc))
            cids.append(cid)
            
        print(f"Fitting Okapi BM25 on {len(cids)} candidates...")
        self.bm25 = BM25Okapi(corpus_tokens)
        self.candidate_ids = cids
        
        # Save cache
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "wb") as f:
            pickle.dump((self.bm25, self.candidate_ids), f, protocol=pickle.HIGHEST_PROTOCOL)
        print(f"Cached BM25 index to: {self.cache_path}")

    def load_index(self):
        """Loads index cache from artifacts."""
        if not os.path.exists(self.cache_path):
            raise FileNotFoundError(f"BM25 index file not found at: {self.cache_path}")
        with open(self.cache_path, "rb") as f:
            self.bm25, self.candidate_ids = pickle.load(f)
        print(f"BM25 index loaded successfully. Indexed: {len(self.candidate_ids)}")

    def score_candidates(self, query: str) -> List[Tuple[str, float]]:
        """Scores candidate docs against query, returning sorted (candidate_id, score) tuples."""
        if self.bm25 is None:
            raise RuntimeError("BM25 index is not loaded.")
        
        query_tokens = self.tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        results = list(zip(self.candidate_ids, scores))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

if __name__ == "__main__":
    searcher = BM25Searcher()
    try:
        searcher.build_index()
        searcher.load_index()
        query = "python faiss vector search retrieval ndcg"
        results = searcher.score_candidates(query)[:5]
        print(f"\nTop 5 matches for query '{query}':")
        for rank, (cid, score) in enumerate(results, 1):
            print(f"  {rank}. {cid} - Score: {score:.4f}")
    except Exception as e:
        print(f"Error: {e}")
