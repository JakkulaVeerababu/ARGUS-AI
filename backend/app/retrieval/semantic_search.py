"""
Purpose: Semantic search retriever utilizing FAISS index and shared SentenceTransformer.
Inputs:
    - model_name: str (embedding model name)
    - index_path: str (path to FAISS binary)
    - ids_path: Optional[str] (unused, mapping loaded directly from SQLite)
Outputs:
    - SemanticSearch instance exposing search queries
Complexity: O(M) query embedding generation, O(log N) vector space search.
Production Concerns: Ensure SQLite connection singleton is initialized; memory-safe mapping.
Future Improvements: Use quantization index configurations to optimize vector search speed at scale.
"""

import os
import time
from typing import List, Tuple
import numpy as np
import faiss
from backend.app.inference.batch_scheduler import EmbeddingScheduler

from backend.app.database.sqlite_manager import SQLiteManager


class SemanticSearch:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: str = None,
        ids_path: str = None,
    ):
        self.model_name = model_name
        self.index_path = index_path or os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "../../../artifacts/faiss_index.bin"
            )
        )
        self.model = None
        self.index = None
        self.candidate_ids = []

        # Load models and indexes
        self.load_resources()

    def load_resources(self):
        """Loads SentenceTransformer and FAISS index into memory, fetching mapping IDs from SQLite."""
        # 1. Load sentence-transformers model on CPU
        print(f"Loading Semantic model '{self.model_name}' on CPU...")
        start_time = time.time()
        self.model = EmbeddingScheduler()

        # 2. Load FAISS index
        if not os.path.exists(self.index_path):
            raise FileNotFoundError(f"FAISS index file not found at: {self.index_path}")
        print(f"Loading FAISS index from: {self.index_path}...")
        self.index = faiss.read_index(self.index_path)

        # 3. Load Candidate IDs mapping directly from SQLite (eliminates candidate_ids.pkl)
        print("Fetching candidate ID mappings from SQLite...")
        db = SQLiteManager()
        rows = db.execute_read("SELECT candidate_id FROM candidates ORDER BY ROWID")
        self.candidate_ids = [row["candidate_id"] for row in rows]

        print(
            f"Semantic search resources loaded in {time.time() - start_time:.2f}s. Total vectors: {self.index.ntotal}"
        )

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
            normalize_embeddings=True,
        ).astype(np.float32)

        # Search index
        scores, indices = self.index.search(query_emb, top_k)

        # Map indices to candidate IDs
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS padding/not found indicator
                continue
            if idx < len(self.candidate_ids):
                cid = self.candidate_ids[idx]
                results.append((cid, float(score)))

        return results
