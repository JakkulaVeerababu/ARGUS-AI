"""
Unit tests for the SQLite + FTS5 database and search layer.
"""

import os
import json
import pytest
from backend.app.database.sqlite_manager import SQLiteManager
from backend.app.business.schema import JDRequirementsSchema
from backend.app.database.migration import DatabaseMigrator
from backend.app.database.candidate_repository import CandidateRepository
from backend.app.database.fts_index import FTSIndexManager
from backend.app.database.query_builder import build_fts_query
from backend.app.retrieval.hybrid_search import HybridSearcher
from backend.app.retrieval.semantic_search import SemanticSearch

TEST_DB_PATH = os.path.abspath("./data/test_argus_ai.db")
TEST_JSONL_PATH = os.path.abspath("./data/test_candidates.jsonl")


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    # Ensure test JSONL exists with dummy candidate profiles
    os.makedirs(os.path.dirname(TEST_JSONL_PATH), exist_ok=True)

    test_cand = {
        "candidate_id": "CAND_TEST_01",
        "profile": {
            "anonymized_name": "Test Candidate 1",
            "current_title": "Senior Machine Learning Engineer",
            "years_of_experience": 8.0,
            "location": "Bangalore, India",
            "current_company": "Flipkart",
            "current_industry": "E-Commerce",
            "headline": "ML Specialist",
            "summary": "Building vector search pipelines",
        },
        "skills": [
            {"name": "Python", "proficiency": "expert", "duration_months": 48},
            {"name": "FAISS", "proficiency": "expert", "duration_months": 12},
        ],
        "career_history": [
            {
                "title": "ML Engineer",
                "company": "Flipkart",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "duration_months": 48,
                "description": "Implemented search engines using vector search",
            }
        ],
        "certifications": [
            {"name": "AWS ML Specialty", "issuer": "Amazon", "issue_date": "2022-01-01"}
        ],
        "redrob_signals": {
            "profile_completeness_score": 95.0,
            "notice_period_days": 30,
            "github_activity_score": 75.0,
            "recruiter_response_rate": 0.85,
            "offer_acceptance_rate": 0.90,
            "interview_completion_rate": 0.95,
            "open_to_work": True,
            "is_remote": False,
            "willing_to_relocate": True,
            "last_active_date": "2026-06-01",
        },
    }

    with open(TEST_JSONL_PATH, "w", encoding="utf-8") as f:
        f.write(json.dumps(test_cand) + "\n")

    # Run database migration to test DB
    migrator = DatabaseMigrator(TEST_DB_PATH)
    migrator.migrate(TEST_JSONL_PATH, batch_size=5)

    yield

    # Cleanup files
    migrator.manager.close()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass

    if os.path.exists(TEST_JSONL_PATH):
        try:
            os.remove(TEST_JSONL_PATH)
        except Exception:
            pass



def test_sqlite_singleton_connection():
    # SQLiteManager should be a Singleton
    m1 = SQLiteManager(TEST_DB_PATH)
    m2 = SQLiteManager(TEST_DB_PATH)
    assert m1 is m2
    assert m1.get_connection() is m2.get_connection()


def test_candidate_repository():
    repo = CandidateRepository(SQLiteManager(TEST_DB_PATH))
    cand = repo.fetch_by_id("CAND_TEST_01")

    assert cand is not None
    assert cand["candidate_id"] == "CAND_TEST_01"
    assert cand["profile"]["anonymized_name"] == "Test Candidate 1"
    assert cand["profile"]["current_title"] == "Senior Machine Learning Engineer"
    assert cand["profile"]["years_of_experience"] == 8.0

    # Verify relations
    assert len(cand["skills"]) == 2
    assert cand["skills"][0]["name"] == "Python"
    assert len(cand["career_history"]) == 1
    assert cand["career_history"][0]["company"] == "Flipkart"
    assert len(cand["certifications"]) == 1
    assert cand["certifications"][0]["issuer"] == "Amazon"

    # Verify signals
    assert cand["redrob_signals"]["notice_period_days"] == 30
    assert cand["redrob_signals"]["open_to_work"] is True


def test_fts_index_search():
    fts = FTSIndexManager(SQLiteManager(TEST_DB_PATH))

    # Search matching keyword
    results = fts.search("vector search pipelines")
    assert len(results) == 1
    assert results[0][0] == "CAND_TEST_01"
    assert results[0][1] > -999.0  # Negated BM25 score

    # Search non-matching keyword
    no_results = fts.search("nonexistent_keyword")
    assert len(no_results) == 0


def test_query_builder():
    jd = JDRequirementsSchema(
        must_have_skills=["Python", "FAISS"],
        nice_to_have_skills=["Machine Learning"],
        locations=["Bangalore"],
        titles=["Engineer"],
        companies=["Flipkart"],
    )

    query = build_fts_query(jd)
    assert "Python" in query
    assert "FAISS" in query
    assert "Bangalore" in query
    assert "Flipkart" in query


def test_hybrid_search_integration(monkeypatch):
    # Mock SemanticSearch query so we don't load SentenceTransformer in tests
    def mock_search(self, query, top_k=1000):
        return [("CAND_TEST_01", 0.85)]

    monkeypatch.setattr(SemanticSearch, "search", mock_search)

    # Also patch load_resources to prevent model loading latency
    def mock_load_resources(self):
        self.candidate_ids = ["CAND_TEST_01"]

    monkeypatch.setattr(SemanticSearch, "load_resources", mock_load_resources)

    # Create hybrid searcher
    searcher = HybridSearcher(faiss_path=os.path.abspath("./artifacts/faiss_index.bin"))

    results = searcher.search("Senior ML Engineer Python", top_k_branch=10)
    assert len(results) == 1
    assert results[0][0] == "CAND_TEST_01"
    assert results[0][1] > 0.0  # RRF score
