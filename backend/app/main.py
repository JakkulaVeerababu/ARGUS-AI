import os
import csv
import json
import gzip
import time
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.app.jd_parser.parser_engine import JDParserEngine
from backend.app.retrieval.hybrid_search import HybridSearcher
from backend.app.ranking.reranker import CrossEncoderRerankingManager
from backend.app.signals.final_score import BusinessScorer
from backend.app.honeypots.gatekeeper import evaluate_candidate_risk
from backend.app.reasoning.reason_builder import build_candidate_reasoning

app = FastAPI(
    title="Argus AI - Candidate Discovery Engine",
    description="Intelligent search and recommendation backend for the Redrob candidate pool.",
    version="1.0.0"
)

# CORS configurations for React frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CANDIDATES_PATH = os.path.abspath("./data/candidates.jsonl")
SUBMISSION_PATH = os.path.abspath("./submission.csv")

class SearchRequest(BaseModel):
    job_description: str

def get_raw_candidate_profile(candidate_id: str) -> Dict[str, Any]:
    """Helper to retrieve a raw candidate JSON profile by ID."""
    if not os.path.exists(CANDIDATES_PATH):
        raise FileNotFoundError("Candidates dataset not found.")
        
    if CANDIDATES_PATH.endswith(".gz"):
        open_func = gzip.open
        mode = "rt"
    else:
        open_func = open
        mode = "r"
        
    with open_func(CANDIDATES_PATH, mode, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            cand = json.loads(line_str)
            if cand.get("candidate_id") == candidate_id:
                return cand
    return {}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "argus-ai-backend"}

@app.post("/api/search")
def run_search(request: SearchRequest):
    """
    Accepts a Job Description string, writes it to a temporary file,
    runs the full parsing, hybrid retrieval, cross-encoder, business scoring,
    and gatekeeper pipeline, and returns the top recommendations.
    """
    temp_jd_path = os.path.abspath("./data/temp_job_description.txt")
    try:
        # Save temp job description
        with open(temp_jd_path, "w", encoding="utf-8") as f:
            f.write(request.job_description)
            
        # 1. Parse JD
        parser = JDParserEngine()
        parsed_jd = parser.parse(temp_jd_path)
        
        query_parts = []
        if parsed_jd.get("titles"):
            query_parts.extend(parsed_jd["titles"])
        if parsed_jd.get("must_have_skills"):
            query_parts.extend(parsed_jd["must_have_skills"])
        if parsed_jd.get("nice_to_have_skills"):
            query_parts.extend(parsed_jd["nice_to_have_skills"])
        query_text = " ".join(query_parts)
        
        if not query_text.strip():
            raise HTTPException(status_code=400, detail="Unable to extract search criteria from Job Description.")
            
        # 2. Hybrid Retrieval
        hybrid_searcher = HybridSearcher()
        retrieved = hybrid_searcher.search(query_text, top_k_branch=1000, final_top_n=300)
        
        # 3. Cross-Encoder Reranking
        reranking_manager = CrossEncoderRerankingManager(candidates_file=CANDIDATES_PATH)
        candidate_ids = [cid for cid, _ in retrieved]
        reranked = reranking_manager.rerank(query_text, candidate_ids, top_n=200)
        
        # 4. Business Signal Scoring
        business_scorer = BusinessScorer(candidates_file=CANDIDATES_PATH)
        scored = business_scorer.score_candidates(reranked, top_n=200)
        
        # 5. Gatekeeper & Honeypot Filtering
        safe_candidates = []
        target_ids = set([c["candidate_id"] for c in scored])
        
        # Load raw dictionaries
        candidate_profiles = {}
        if CANDIDATES_PATH.endswith(".gz"):
            open_func = gzip.open
            mode = "rt"
        else:
            open_func = open
            mode = "r"
            
        with open_func(CANDIDATES_PATH, mode, encoding="utf-8") as f:
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
                        
        for c_record in scored:
            cid = c_record["candidate_id"]
            cand = candidate_profiles.get(cid)
            if not cand:
                continue
                
            risk_res = evaluate_candidate_risk(cand)
            if risk_res["honeypot_flag"] or risk_res["risk_score"] > 0.5:
                continue
                
            # Add reasoning
            c_record["reasoning"] = build_candidate_reasoning(cand, len(safe_candidates) + 1)
            safe_candidates.append(c_record)
            
            if len(safe_candidates) >= 50:  # Return top 50 in search UI
                break
                
        return {"success": True, "results": safe_candidates}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_jd_path):
            os.remove(temp_jd_path)

@app.get("/api/candidate/{cid}")
def get_candidate_details(cid: str):
    """Fetches full candidate details from the candidate pool."""
    try:
        cand = get_raw_candidate_profile(cid)
        if not cand:
            raise HTTPException(status_code=404, detail="Candidate not found.")
        return cand
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/rankings")
def get_submission_rankings():
    """Reads the generated submission.csv and returns the ranked profile list."""
    if not os.path.exists(SUBMISSION_PATH):
        raise HTTPException(status_code=404, detail="Submission rankings file has not been generated yet.")
        
    rankings = []
    target_ids = []
    
    # 1. Read submission CSV
    with open(SUBMISSION_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rankings.append({
                "candidate_id": row["candidate_id"],
                "rank": int(row["rank"]),
                "score": float(row["score"]),
                "reasoning": row["reasoning"]
            })
            target_ids.append(row["candidate_id"])
            
    # 2. Load basic profile info for rendering
    target_set = set(target_ids)
    candidate_profiles = {}
    
    if CANDIDATES_PATH.endswith(".gz"):
        open_func = gzip.open
        mode = "rt"
    else:
        open_func = open
        mode = "r"
        
    with open_func(CANDIDATES_PATH, mode, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            cand = json.loads(line_str)
            cid = cand.get("candidate_id")
            if cid in target_set:
                profile = cand.get("profile", {})
                signals = cand.get("redrob_signals", {})
                candidate_profiles[cid] = {
                    "name": profile.get("anonymized_name", ""),
                    "title": profile.get("current_title", ""),
                    "experience": profile.get("years_of_experience", 0.0),
                    "location": profile.get("location", ""),
                    "github_score": signals.get("github_activity_score", -1.0),
                    "response_rate": signals.get("recruiter_response_rate", 0.0),
                    "notice_period": signals.get("notice_period_days", 0)
                }
                if len(candidate_profiles) >= len(target_set):
                    break
                    
    # Merge
    for row in rankings:
        cid = row["candidate_id"]
        info = candidate_profiles.get(cid, {})
        row.update(info)
        
    return rankings

@app.get("/api/analytics")
def get_analytics_distribution():
    """Generates distribution analytics over the top 100 candidates."""
    rankings = get_submission_rankings()
    
    exp_bins = {"0-4 yrs": 0, "5-9 yrs": 0, "10+ yrs": 0}
    notice_bins = {"<30 days": 0, "30-60 days": 0, "61-90 days": 0, ">90 days": 0}
    locations = {}
    
    total_match = 0.0
    total_completeness = 0.0
    open_to_work_count = 0
    
    for c in rankings:
        # Experience
        exp = c.get("experience", 0.0)
        if exp < 5.0:
            exp_bins["0-4 yrs"] += 1
        elif exp <= 9.0:
            exp_bins["5-9 yrs"] += 1
        else:
            exp_bins["10+ yrs"] += 1
            
        # Notice
        notice = c.get("notice_period", 0)
        if notice < 30:
            notice_bins["<30 days"] += 1
        elif notice <= 60:
            notice_bins["30-60 days"] += 1
        elif notice <= 90:
            notice_bins["61-90 days"] += 1
        else:
            notice_bins[">90 days"] += 1
            
        # Location
        loc = c.get("location", "Unknown")
        city = loc.split(",")[0].strip().title()
        locations[city] = locations.get(city, 0) + 1
        
        # Match Score
        total_match += c.get("score", 0.0)
        
    # Top 5 locations
    sorted_locs = sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "kpis": {
            "total_candidates": len(rankings),
            "average_match_score": total_match / len(rankings) if rankings else 0.0,
            "top_locations": [{"city": city, "count": count} for city, count in sorted_locs]
        },
        "distributions": {
            "experience": [{"range": k, "count": v} for k, v in exp_bins.items()],
            "notice_period": [{"timeline": k, "count": v} for k, v in notice_bins.items()],
            "locations": [{"name": city, "value": count} for city, count in sorted_locs]
        }
    }

@app.get("/api/submission")
def download_submission_file():
    """Serves the generated submission.csv directly as a file download."""
    if not os.path.exists(SUBMISSION_PATH):
        raise HTTPException(status_code=404, detail="Submission file has not been generated yet.")
    return FileResponse(path=SUBMISSION_PATH, filename="submission.csv", media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
