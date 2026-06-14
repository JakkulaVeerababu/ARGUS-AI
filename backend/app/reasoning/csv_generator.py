import os
import csv
from typing import List, Dict, Any

class CSVGenerator:
    @staticmethod
    def generate_csv(ranked_candidates: List[Dict[str, Any]], output_path: str):
        """
        Writes the top candidates list to the specified output CSV path.
        Enforces:
        - Header: candidate_id,rank,score,reasoning
        - Strictly sorted scores descending (ties broken by ID ascending).
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Sort to ensure monotonicity and alphabetical tie-breaking
        ranked_candidates.sort(key=lambda x: (-x["final_score"], x["candidate_id"]))
        
        with open(output_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["candidate_id", "rank", "score", "reasoning"])
            
            for rank, record in enumerate(ranked_candidates[:100], 1):
                cid = record["candidate_id"]
                score = record["final_score"]
                reason = record.get("reasoning", "")
                writer.writerow([cid, rank, f"{score:.6f}", reason])
                
        print(f"Successfully wrote 100 rows to: {output_path}")

if __name__ == "__main__":
    test_data = [
        {"candidate_id": "CAND_0000001", "final_score": 0.85, "reasoning": "Test candidate 1"},
        {"candidate_id": "CAND_0000002", "final_score": 0.95, "reasoning": "Test candidate 2"}
    ]
    try:
        CSVGenerator.generate_csv(test_data, "./test_out.csv")
        # Cleanup
        if os.path.exists("./test_out.csv"):
            os.remove("./test_out.csv")
    except Exception as e:
        print(f"Error: {e}")
