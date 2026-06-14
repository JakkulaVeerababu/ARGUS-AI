import os
import csv
import argparse
import time
from typing import List, Dict, Any

from backend.app.jd_parser.parser_engine import JDParserEngine
from backend.app.retrieval.hybrid_search import HybridSearcher
from backend.app.ranking.reranker import CrossEncoderRerankingManager
from backend.app.signals.final_score import BusinessScorer
from backend.app.honeypots.gatekeeper import evaluate_candidate_risk
from backend.app.reasoning_v2.reason_builder_v2 import build_candidate_reasoning_v2

def run_ranking_pipeline(candidates_path: str, jd_path: str, output_csv: str):
    """
    Runs the full end-to-end ranking and filtering pipeline:
    1. Parse Job Description.
    2. Retrieve top candidates using Hybrid Search (BM25 + FAISS).
    3. Re-rank top 300 using Cross-Encoder.
    4. Apply Business Signal Score multipliers over top 200.
    5. Filter out Honeypots and high-risk profiles using Gatekeeper.
    6. Select top 100 safe candidates.
    7. Generate natural explanations and save as submission CSV.
    """
    print("==================================================")
    print("       ARGUS AI - Candidate Discovery Engine      ")
    print("==================================================")
    start_time = time.time()

    # 1. Parse Job Description
    print(f"\n[Step 1] Parsing Job Description from: {jd_path}...")
    parser = JDParserEngine()
    parsed_jd = parser.parse(jd_path)
    
    # Construct robust query from JD requirements
    query_parts = []
    if parsed_jd.get("titles"):
        query_parts.extend(parsed_jd["titles"])
    if parsed_jd.get("must_have_skills"):
        query_parts.extend(parsed_jd["must_have_skills"])
    if parsed_jd.get("nice_to_have_skills"):
        query_parts.extend(parsed_jd["nice_to_have_skills"])
        
    query_text = " ".join(query_parts)
    print(f"Constructed Query: '{query_text}'")

    # 2. Retrieve candidates using Hybrid Search
    print("\n[Step 2] Executing Hybrid Retrieval (BM25 + FAISS)...")
    hybrid_searcher = HybridSearcher(
        bm25_path=os.path.abspath("./artifacts/bm25_index.pkl"),
        faiss_path=os.path.abspath("./artifacts/faiss_index.bin"),
        ids_path=os.path.abspath("./artifacts/candidate_ids.pkl")
    )
    # Get top 300 candidates to pass to the Cross-Encoder Reranker
    retrieved_candidates = hybrid_searcher.search(
        query_text,
        top_k_branch=1000,
        final_top_n=300,
        k_rrf=60
    )
    print(f"Retrieved {len(retrieved_candidates)} candidate IDs via RRF.")

    # 3. Re-rank using Cross-Encoder
    print("\n[Step 3] Executing Cross-Encoder Reranking...")
    reranking_manager = CrossEncoderRerankingManager(
        model_name="cross-encoder/ms-marco-MiniLM-L-6-v2",
        candidates_file=candidates_path
    )
    candidate_ids = [cid for cid, _ in retrieved_candidates]
    # Rerank and output top 200 candidates
    reranked_candidates = reranking_manager.rerank(
        query=query_text,
        candidate_ids=candidate_ids,
        top_n=200
    )
    print(f"Cross-Encoder reranked top {len(reranked_candidates)} candidates.")

    # 4. Apply Business Signal Score multipliers
    print("\n[Step 4] Applying Business Signal Scoring...")
    business_scorer = BusinessScorer(candidates_file=candidates_path)
    scored_candidates = business_scorer.score_candidates(
        ce_results=reranked_candidates,
        top_n=200
    )
    print(f"Scored {len(scored_candidates)} candidates with business multipliers.")

    # 5. Filter out Honeypots and high-risk profiles using Gatekeeper
    print("\n[Step 5] Executing Honeypot & Risk Gatekeeper Filtering...")
    safe_candidates = []
    honeypot_count = 0
    high_risk_count = 0
    
    # Stream the full profiles of scored candidates to run gatekeeper
    # Scorer already loads candidate details, we can load them to inspect
    # Load candidate profiles matching our scored set
    target_ids = set([c["candidate_id"] for c in scored_candidates])
    candidate_profiles = {}
    
    # Access candidates raw JSON to run validation rules
    import json
    import gzip
    if candidates_path.endswith(".gz"):
        open_func = gzip.open
        mode = "rt"
    else:
        open_func = open
        mode = "r"
        
    with open_func(candidates_path, mode, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            cand = json.loads(line_str)
            cid = cand.get("candidate_id")
            if cid in target_ids:
                candidate_profiles[cid] = cand
                if len(candidate_profiles) >= len(target_ids):
                    break
                    
    for c_record in scored_candidates:
        cid = c_record["candidate_id"]
        cand = candidate_profiles.get(cid)
        if not cand:
            continue
            
        # Run gatekeeper risk checks
        risk_res = evaluate_candidate_risk(cand)
        
        if risk_res["honeypot_flag"]:
            print(f"  [Filtered] Honeypot {cid} - Reasons: {risk_res['reasons']}")
            honeypot_count += 1
            continue
            
        if risk_res["risk_score"] > 0.5:
            print(f"  [Filtered] High-Risk {cid} - Score: {risk_res['risk_score']:.2f} - Reasons: {risk_res['reasons']}")
            high_risk_count += 1
            continue
            
        safe_candidates.append(c_record)
        
        # Stop once we have exactly 100 safe candidates
        if len(safe_candidates) >= 100:
            break
            
    print(f"Gatekeeper complete. Filtered {honeypot_count} honeypots and {high_risk_count} high-risk candidates.")
    print(f"Selected exactly {len(safe_candidates)} safe candidates for ranking.")

    # 6. Check if we have 100 candidates
    if len(safe_candidates) < 100:
        print(f"Warning: Only found {len(safe_candidates)} safe candidates. Filling with remainder.")
        # If we fall short, fill with previously filtered (but non-honeypot) candidates to meet spec
        for c_record in scored_candidates:
            cid = c_record["candidate_id"]
            if cid not in [s["candidate_id"] for s in safe_candidates]:
                # Make sure it's not a hard honeypot
                cand = candidate_profiles.get(cid)
                if cand and not evaluate_candidate_risk(cand)["honeypot_flag"]:
                    safe_candidates.append(c_record)
                    if len(safe_candidates) >= 100:
                        break

    # 7. Write to CSV with reasoning and deterministic rank tie-breaks
    print(f"\n[Step 6] Saving final top 100 submission to: {output_csv}...")
    
    # Sort again to ensure strictly non-increasing score order and alphabetical tie-breaks
    safe_candidates.sort(key=lambda x: (-x["final_score"], x["candidate_id"]))
    
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank, cand_record in enumerate(safe_candidates[:100], 1):
            cid = cand_record["candidate_id"]
            score = cand_record["final_score"]
            cand = candidate_profiles.get(cid)
            reason = build_candidate_reasoning_v2(cand, rank, parsed_jd)
            writer.writerow([cid, rank, f"{score:.6f}", reason])
            
    print("CSV generated successfully.")
    print(f"Total pipeline execution time: {time.time() - start_time:.2f} seconds.")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argus AI Candidate Discovery and Ranking CLI")
    parser.add_argument("--candidates", type=str, default="./data/candidates.jsonl", help="Path to candidates jsonl dataset")
    parser.add_argument("--jd", type=str, default="./data/job_description.docx", help="Path to Job Description docx")
    parser.add_argument("--out", type=str, default="./submission.csv", help="Output path for submission CSV")
    
    args = parser.parse_args()
    
    # Run the orchestrator
    run_ranking_pipeline(args.candidates, args.jd, args.out)
