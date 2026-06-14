import os
import csv
import json
import gzip
import time
import hashlib
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from loguru import logger

from backend.app.core.settings import settings
from backend.app.core.startup import lifespan
from backend.app.core.model_registry import ModelRegistry
from backend.app.core.cache_manager import CacheManager
from backend.app.core.metrics import metrics_collector
from backend.app.core.health import router as health_router
from backend.app.core.metrics import router as metrics_router
from backend.app.core.exception_handlers import (
    register_exception_handlers,
    InvalidJobDescriptionError,
    EmptyRetrievalError,
    CSVProcessingError,
)

from backend.app.jd_parser.parser_engine import JDParserEngine
from backend.app.signals.final_score import BusinessScorer
from backend.app.honeypots.gatekeeper import evaluate_candidate_risk
from backend.app.reasoning_v2.reason_builder_v2 import build_candidate_reasoning_v2

app = FastAPI(
    title="Argus AI - Candidate Discovery Engine",
    description="Intelligent search and recommendation backend for the Redrob candidate pool.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configurations for React frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Health and Metrics routers
app.include_router(health_router)
app.include_router(metrics_router)

# Register custom global exception handlers
register_exception_handlers(app)


class SearchRequest(BaseModel):
    job_description: str


def get_raw_candidate_profile(candidate_id: str) -> Dict[str, Any]:
    """Helper to retrieve a raw candidate JSON profile by ID (Sync I/O)."""
    if not os.path.exists(settings.CANDIDATES_PATH):
        raise FileNotFoundError(
            f"Candidates dataset not found at: {settings.CANDIDATES_PATH}"
        )

    if settings.CANDIDATES_PATH.endswith(".gz"):
        open_func = gzip.open
        mode = "rt"
    else:
        open_func = open
        mode = "r"

    with open_func(settings.CANDIDATES_PATH, mode, encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            cand = json.loads(line_str)
            if cand.get("candidate_id") == candidate_id:
                return cand
    return {}


def process_candidates_pipeline(
    scored: List[Dict[str, Any]], target_ids: set, parsed_jd: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Heavy synchronous pipeline processing: raw profile stream, gatekeeping, and reasoning creation."""
    safe_candidates = []
    candidate_profiles = {}

    if not os.path.exists(settings.CANDIDATES_PATH):
        raise FileNotFoundError(
            f"Candidates dataset not found at: {settings.CANDIDATES_PATH}"
        )

    if settings.CANDIDATES_PATH.endswith(".gz"):
        open_func = gzip.open
        mode = "rt"
    else:
        open_func = open
        mode = "r"

    with open_func(settings.CANDIDATES_PATH, mode, encoding="utf-8") as f:
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

        # Add reasoning using the Reasoning V2 builder
        c_record["reasoning"] = build_candidate_reasoning_v2(
            cand, len(safe_candidates) + 1, parsed_jd
        )
        safe_candidates.append(c_record)

        if len(safe_candidates) >= 50:  # Return top 50 in search UI
            break

    return safe_candidates


@app.post("/api/search")
async def run_search(request: SearchRequest):
    """
    Accepts a Job Description, queries lexical and semantic search engines,
    reranks results using Cross-Encoder, computes final business score, filters candidates,
    and returns the top recommendations. Utilizes background threadpool and caching.
    """
    start_time = time.time()

    # Validation
    if not request.job_description.strip():
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise InvalidJobDescriptionError("Job Description is empty.")

    # Caching check
    jd_hash = hashlib.sha256(request.job_description.encode("utf-8")).hexdigest()
    cache_key = f"search:jd:{jd_hash}"
    cache = CacheManager()

    try:
        cached_results = await cache.get(cache_key)
        if cached_results is not None:
            metrics_collector.record_cache_hit()
            logger.info(f"[API] Cache hit for search request hash: {jd_hash}")
            metrics_collector.record_request(time.time() - start_time, success=True)
            return cached_results
    except Exception as e:
        logger.error(f"[API] Cache read failure: {e}")

    metrics_collector.record_cache_miss()
    logger.info(
        f"[API] Cache miss. Initiating search pipeline for request hash: {jd_hash}"
    )

    temp_dir = os.path.join(settings.BASE_DIR, "data")
    temp_jd_path = os.path.join(temp_dir, f"temp_job_description_{jd_hash}.txt")
    try:
        # Save temp job description (I/O block) — using absolute BASE_DIR path
        def write_temp_jd():
            os.makedirs(temp_dir, exist_ok=True)
            with open(temp_jd_path, "w", encoding="utf-8") as f:
                f.write(request.job_description)

        await run_in_threadpool(write_temp_jd)

        # 1. Parse JD
        parser = JDParserEngine()
        parsed_jd = await run_in_threadpool(parser.parse, temp_jd_path)

        query_parts = []
        if parsed_jd.get("titles"):
            query_parts.extend(parsed_jd["titles"])
        if parsed_jd.get("must_have_skills"):
            query_parts.extend(parsed_jd["must_have_skills"])
        if parsed_jd.get("nice_to_have_skills"):
            query_parts.extend(parsed_jd["nice_to_have_skills"])
        query_text = " ".join(query_parts)

        if not query_text.strip():
            raise InvalidJobDescriptionError(
                "Unable to extract valid search criteria from Job Description."
            )

        # Retrieve singleton warmed services from ModelRegistry
        registry = ModelRegistry()
        hybrid_searcher = registry.hybrid_searcher
        reranking_manager = registry.reranking_manager

        # 2. Hybrid Retrieval (lexical + semantic)
        logger.info(f"[API] Performing hybrid retrieval for: {query_text[:60]}...")
        ret_start = time.time()
        retrieved = await run_in_threadpool(
            hybrid_searcher.search,
            query_text,
            top_k_branch=settings.TOP_K_BRANCH,
            final_top_n=settings.FINAL_TOP_N,
            k_rrf=settings.RRF_K,
        )
        metrics_collector.record_inference(time.time() - ret_start)

        if not retrieved:
            raise EmptyRetrievalError("No matching candidates found for the query.")

        # 3. Cross-Encoder Reranking
        logger.info(f"[API] Reranking {len(retrieved)} retrieved candidates...")
        rank_start = time.time()
        candidate_ids = [cid for cid, _ in retrieved]
        reranked = await run_in_threadpool(
            reranking_manager.rerank, query_text, candidate_ids, top_n=settings.RERANK_N
        )
        metrics_collector.record_inference(time.time() - rank_start)
        logger.info(f"[RANKING] Successfully reranked top {len(reranked)} candidates.")

        # 4. Business Signal Scoring
        business_scorer = BusinessScorer(candidates_file=settings.CANDIDATES_PATH)
        scored = await run_in_threadpool(
            business_scorer.score_candidates, reranked, top_n=settings.RERANK_N
        )

        # 5. Gatekeeper & Honeypot Filtering, Reasoning Creation
        target_ids = set([c["candidate_id"] for c in scored])
        safe_candidates = await run_in_threadpool(
            process_candidates_pipeline, scored, target_ids, parsed_jd
        )

        results = {"success": True, "results": safe_candidates}

        # Cache final results
        try:
            await cache.set(cache_key, results)
        except Exception as e:
            logger.error(f"[API] Cache write failure: {e}")

        metrics_collector.record_request(time.time() - start_time, success=True)
        return results

    except (InvalidJobDescriptionError, EmptyRetrievalError) as e:
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise e
    except Exception as e:
        metrics_collector.record_request(time.time() - start_time, success=False)
        logger.error(f"[API] Internal error during candidate search: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        def clean_temp():
            if os.path.exists(temp_jd_path):
                os.remove(temp_jd_path)

        await run_in_threadpool(clean_temp)


@app.get("/api/candidate/{cid}")
async def get_candidate_details(cid: str):
    """Fetches full candidate details from the candidate pool (Async with cache)."""
    start_time = time.time()
    cache_key = f"candidate:cid:{cid}"
    cache = CacheManager()

    try:
        cached_profile = await cache.get(cache_key)
        if cached_profile is not None:
            metrics_collector.record_cache_hit()
            metrics_collector.record_request(time.time() - start_time, success=True)
            return cached_profile
    except Exception as e:
        logger.error(f"[API] Cache read failure: {e}")

    metrics_collector.record_cache_miss()
    try:
        cand = await run_in_threadpool(get_raw_candidate_profile, cid)
        if not cand:
            metrics_collector.record_request(time.time() - start_time, success=False)
            raise HTTPException(status_code=404, detail="Candidate not found.")

        try:
            await cache.set(cache_key, cand)
        except Exception as e:
            logger.error(f"[API] Cache write failure: {e}")

        metrics_collector.record_request(time.time() - start_time, success=True)
        return cand
    except HTTPException as e:
        raise e
    except Exception as e:
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise HTTPException(status_code=500, detail=str(e))


def load_submission_rankings() -> List[Dict[str, Any]]:
    """Heavy synchronous loading and merging of generated rankings and profile details."""
    if not os.path.exists(settings.SUBMISSION_PATH):
        raise CSVProcessingError("Submission rankings file has not been generated yet.")

    rankings = []
    target_ids = []

    # 1. Read submission CSV
    with open(settings.SUBMISSION_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rankings.append(
                {
                    "candidate_id": row["candidate_id"],
                    "rank": int(row["rank"]),
                    "score": float(row["score"]),
                    "reasoning": row["reasoning"],
                }
            )
            target_ids.append(row["candidate_id"])

    # 2. Load basic profile info for rendering
    target_set = set(target_ids)
    candidate_profiles = {}

    if not os.path.exists(settings.CANDIDATES_PATH):
        raise FileNotFoundError(
            f"Candidates file not found at {settings.CANDIDATES_PATH}"
        )

    if settings.CANDIDATES_PATH.endswith(".gz"):
        open_func = gzip.open
        mode = "rt"
    else:
        open_func = open
        mode = "r"

    with open_func(settings.CANDIDATES_PATH, mode, encoding="utf-8") as f:
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
                    "notice_period": signals.get("notice_period_days", 0),
                }
                if len(candidate_profiles) >= len(target_set):
                    break

    # Merge details
    for row in rankings:
        cid = row["candidate_id"]
        info = candidate_profiles.get(cid, {})
        row.update(info)

    return rankings


@app.get("/api/rankings")
async def get_submission_rankings():
    """Reads the generated submission.csv and returns the ranked list with profile attributes."""
    start_time = time.time()
    cache_key = "rankings:all"
    cache = CacheManager()

    try:
        cached_rankings = await cache.get(cache_key)
        if cached_rankings is not None:
            metrics_collector.record_cache_hit()
            metrics_collector.record_request(time.time() - start_time, success=True)
            return cached_rankings
    except Exception as e:
        logger.error(f"[API] Cache read failure: {e}")

    metrics_collector.record_cache_miss()
    try:
        rankings = await run_in_threadpool(load_submission_rankings)
        try:
            # Cache for 60 seconds to support real-time generation updates
            await cache.set(cache_key, rankings, ttl=60)
        except Exception as e:
            logger.error(f"[API] Cache write failure: {e}")

        metrics_collector.record_request(time.time() - start_time, success=True)
        return rankings
    except CSVProcessingError as e:
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics")
async def get_analytics_distribution():
    """Generates distribution analytics over the top 100 candidates."""
    start_time = time.time()
    cache_key = "analytics:all"
    cache = CacheManager()

    try:
        cached_analytics = await cache.get(cache_key)
        if cached_analytics is not None:
            metrics_collector.record_cache_hit()
            metrics_collector.record_request(time.time() - start_time, success=True)
            return cached_analytics
    except Exception as e:
        logger.error(f"[API] Cache read failure: {e}")

    metrics_collector.record_cache_miss()
    try:
        rankings = await get_submission_rankings()

        exp_bins = {"0-4 yrs": 0, "5-9 yrs": 0, "10+ yrs": 0}
        notice_bins = {"<30 days": 0, "30-60 days": 0, "61-90 days": 0, ">90 days": 0}
        locations = {}

        total_match = 0.0

        for c in rankings:
            # Experience
            exp = c.get("experience", 0.0)
            if exp < 5.0:
                exp_bins["0-4 yrs"] += 1
            elif exp <= 9.0:
                exp_bins["5-9 yrs"] += 1
            else:
                exp_bins["10+ yrs"] += 1

            # Notice Period
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

        analytics_result = {
            "kpis": {
                "total_candidates": len(rankings),
                "average_match_score": total_match / len(rankings) if rankings else 0.0,
                "top_locations": [
                    {"city": city, "count": count} for city, count in sorted_locs
                ],
            },
            "distributions": {
                "experience": [{"range": k, "count": v} for k, v in exp_bins.items()],
                "notice_period": [
                    {"timeline": k, "count": v} for k, v in notice_bins.items()
                ],
                "locations": [
                    {"name": city, "value": count} for city, count in sorted_locs
                ],
            },
        }

        try:
            # Cache for 60 seconds
            await cache.set(cache_key, analytics_result, ttl=60)
        except Exception as e:
            logger.error(f"[API] Cache write failure: {e}")

        metrics_collector.record_request(time.time() - start_time, success=True)
        return analytics_result
    except Exception as e:
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/submission")
async def download_submission_file():
    """Serves the generated submission.csv directly as a file download (Async checks)."""
    start_time = time.time()

    def verify_file_exists():
        return os.path.exists(settings.SUBMISSION_PATH)

    exists = await run_in_threadpool(verify_file_exists)
    if not exists:
        metrics_collector.record_request(time.time() - start_time, success=False)
        raise HTTPException(
            status_code=404, detail="Submission file has not been generated yet."
        )

    metrics_collector.record_request(time.time() - start_time, success=True)
    return FileResponse(
        path=settings.SUBMISSION_PATH, filename="submission.csv", media_type="text/csv"
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
