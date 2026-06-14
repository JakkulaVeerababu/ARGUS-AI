import time
from typing import List, Tuple
from backend.app.ranking.cross_encoder import CrossEncoderReranker
from backend.app.ranking.pair_builder import PairBuilder

class CrossEncoderRerankingManager:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", candidates_file: str = None):
        self.reranker = CrossEncoderReranker(model_name)
        self.pair_builder = PairBuilder(candidates_file)

    def rerank(self, query: str, candidate_ids: List[str], top_n: int = 200) -> List[Tuple[str, float]]:
        """
        Reranks a list of candidate IDs based on a query using the Cross-Encoder.
        Returns:
            - A list of (candidate_id, cross_encoder_score) sorted by score descending,
              with ties broken alphabetically by candidate_id ascending.
        """
        if not candidate_ids:
            return []
            
        print(f"Reranking {len(candidate_ids)} candidates using Cross-Encoder...")
        start_time = time.time()
        
        # 1. Build query-document pairs
        pairs, ordered_ids = self.pair_builder.build_pairs(query, candidate_ids)
        
        # 2. Score pairs using Cross-Encoder
        scores = self.reranker.score_pairs(pairs)
        
        # 3. Map scores to candidate IDs
        cand_scores = list(zip(ordered_ids, scores))
        
        # 4. Sort by score descending, then by candidate_id ascending (deterministic tie break)
        sorted_candidates = sorted(
            cand_scores,
            key=lambda x: (-x[1], x[0])
        )
        
        final_ranked = sorted_candidates[:top_n]
        print(f"Reranking completed in {time.time() - start_time:.2f} seconds.")
        return final_ranked

if __name__ == "__main__":
    manager = CrossEncoderRerankingManager()
    try:
        # Load model explicitly
        manager.reranker.load_model()
        query = "Python developer with experience in machine learning and faiss search"
        # We can pass simple test candidate IDs if they exist in the sample
        test_ids = ["CAND_0000001", "CAND_0000002", "CAND_0000003"]
        results = manager.rerank(query, test_ids, top_n=2)
        print(f"\nReranked Top 2:")
        for cid, score in results:
            print(f"  {cid} - Score: {score:.4f}")
    except Exception as e:
        print(f"Error: {e}")
