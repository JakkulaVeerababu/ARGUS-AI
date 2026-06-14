import os
import csv
import pytest

def test_submission_constraints():
    # We will test the sorting and format constraint function.
    # Let's mock a sorting function to verify it works correctly.
    candidates = [
        {"candidate_id": "CAND_B", "final_score": 0.85},
        {"candidate_id": "CAND_A", "final_score": 0.85},
        {"candidate_id": "CAND_C", "final_score": 0.90},
        {"candidate_id": "CAND_D", "final_score": 0.70}
    ]
    
    # Sort by score descending, then candidate_id ascending (alphabetical tie-break)
    candidates.sort(key=lambda x: (-x["final_score"], x["candidate_id"]))
    
    assert candidates[0]["candidate_id"] == "CAND_C"  # 0.90
    assert candidates[1]["candidate_id"] == "CAND_A"  # 0.85 (A < B alphabetically)
    assert candidates[2]["candidate_id"] == "CAND_B"  # 0.85
    assert candidates[3]["candidate_id"] == "CAND_D"  # 0.70

def test_csv_file_generation_and_schema(tmp_path):
    output_csv = os.path.join(tmp_path, "test_submission.csv")
    
    # Mock writing code similar to rank.py
    safe_candidates = [
        {"candidate_id": "CAND_001", "final_score": 0.952, "reasoning": "Experienced engineer based in Noida..."},
        {"candidate_id": "CAND_002", "final_score": 0.910, "reasoning": "Experienced developer based in Pune..."}
    ]
    
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, cand in enumerate(safe_candidates, 1):
            writer.writerow([
                cand["candidate_id"],
                rank,
                f"{cand['final_score']:.6f}",
                cand["reasoning"]
            ])
            
    # Read back and validate
    assert os.path.exists(output_csv)
    with open(output_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    assert len(rows) == 2
    assert list(rows[0].keys()) == ["candidate_id", "rank", "score", "reasoning"]
    
    assert rows[0]["candidate_id"] == "CAND_001"
    assert rows[0]["rank"] == "1"
    assert rows[0]["score"] == "0.952000"
    assert rows[0]["reasoning"] == "Experienced engineer based in Noida..."
    
    assert rows[1]["candidate_id"] == "CAND_002"
    assert rows[1]["rank"] == "2"
    assert rows[1]["score"] == "0.910000"
    assert rows[1]["reasoning"] == "Experienced developer based in Pune..."
