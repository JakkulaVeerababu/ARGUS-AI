import os
import time
import pickle
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class SemanticSearch:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_path: str = None, ids_path: str = None):
        self.model_name = model_name
        self.index_path = index_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../artifacts/faiss_index.bin")
        )
        self.ids_path = ids_path or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../artifacts/candidate_ids.pkl")
        )
        self.model = None
        self.index = None
        self.candidate_ids = []

        # Load models and indexes
        self.load_resources()

    def load_resources(self):
        """Loads SentenceTransformer and FAISS index into memory."""
        # 1. Load sentence-transformers model on CPU
        print(f"Loading Semantic model '{self.model_name}' on CPU...")
        start_time = time.time()
        self.model = SentenceTransformer(self.model_name, device="cpu")
        
        # 2. Load FAISS index
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"FAISS index file not found at: {self.index_path}")
        print(f"Loading FAISS index from: {self.index_path}...")
        self.index = faiss.read_index(self.index_path)
        
        # 3. Load Candidate IDs mapping
        if not os.path.exists(self.ids_path):
            raise FileNotFoundError(f"Candidate IDs file not found at: {self.ids_path}")
        with open(self.ids_path, "rb") as f:
            self.candidate_ids = pickle.load(f)
            
        print(f"Semantic search resources loaded in {time.time() - start_time:.2f}s. Total vectors: {self.index.ntotal}")

    def search(self, query: str, top_k: int = 1000) -> List[Tuple[str, float]]:
        """
        Encodes query string, searches the FAISS index, and maps results to candidate IDs.
        Returns a list of (candidate_id, cosine_similarity_score).
        """
        # Encode and L2 normalize query
        query_emb = self.model.encode(
            [query],
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)
        
        # Search index
        scores, indices = self.index.search(query_emb, top_k)
        
        # Map indices to candidate IDs
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS padding/not found indicator
                continue
            cid = self.candidate_ids[idx]
            results.append((cid, float(score)))
            
        return results

if __name__ == "__main__":
    try:
        searcher = SemanticSearch()
        query = "python faiss vector search retrieval ndcg"
        results = searcher.search(query, top_k=5)
        print(f"\nSemantic Search Top 5 for '{query}':")
        for cid, score in results:
            print(f"  {cid} - Cosine Similarity: {score:.4f}")
    except Exception as e:
        print(f"Error: {e}")
