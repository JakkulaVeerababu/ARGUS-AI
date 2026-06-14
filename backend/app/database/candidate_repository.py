"""
Purpose: Candidate repository encapsulating all relational database queries.
Inputs:
    - manager: Optional[SQLiteManager] (shared manager singleton reference)
Outputs:
    - CandidateRepository instance exposing fetch methods
Complexity: O(1) primary key queries, O(S + H + C) related table joins.
Production Concerns: SQL Injection prevention (use parameterized queries); re-assembling structured JSON format accurately.
Future Improvements: Add caching layers (e.g. redis or local memory dictionary) for highly frequent lookups.
"""
from typing import List, Dict, Any, Optional
from backend.app.database.sqlite_manager import SQLiteManager

class CandidateRepository:
    def __init__(self, manager: Optional[SQLiteManager] = None):
        self.db = manager or SQLiteManager()

    def fetch_skills(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Retrieves candidate skills."""
        rows = self.db.execute_read(
            "SELECT name, proficiency, duration_months FROM skills WHERE candidate_id = ?",
            (candidate_id,)
        )
        return [dict(r) for r in rows]

    def fetch_history(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Retrieves candidate career history."""
        rows = self.db.execute_read(
            "SELECT title, company, start_date, end_date, duration_months, description FROM career_history WHERE candidate_id = ?",
            (candidate_id,)
        )
        return [dict(r) for r in rows]

    def fetch_certifications(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Retrieves candidate certifications."""
        rows = self.db.execute_read(
            "SELECT name, issuer, issue_date FROM certifications WHERE candidate_id = ?",
            (candidate_id,)
        )
        return [dict(r) for r in rows]

    def fetch_by_id(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches a single candidate record by primary key and reconstructs
        the nested candidate profile structure.
        """
        rows = self.db.execute_read(
            "SELECT * FROM candidates WHERE candidate_id = ?",
            (candidate_id,)
        )
        if not rows:
            return None
            
        row = rows[0]
        cand = dict(row)
        
        # Assemble standard profile segment
        profile = {
            "anonymized_name": cand.get("anonymized_name", ""),
            "current_title": cand.get("current_title", ""),
            "years_of_experience": cand.get("years_of_experience", 0.0),
            "location": cand.get("location", ""),
            "current_company": cand.get("current_company", ""),
            "current_industry": cand.get("current_industry", ""),
            "headline": cand.get("headline", ""),
            "summary": cand.get("summary", "")
        }
        
        # Assemble platform signals
        redrob_signals = {
            "profile_completeness_score": cand.get("profile_completeness_score", 100.0),
            "notice_period_days": cand.get("notice_period_days", 0),
            "github_activity_score": cand.get("github_activity_score", 0.0),
            "recruiter_response_rate": cand.get("recruiter_response_rate", 0.0),
            "offer_acceptance_rate": cand.get("offer_acceptance_rate", 0.0),
            "interview_completion_rate": cand.get("interview_completion_rate", 0.0),
            "open_to_work": bool(cand.get("open_to_work", 0)),
            "is_remote": bool(cand.get("is_remote", 0)),
            "willing_to_relocate": bool(cand.get("willing_to_relocate", 0)),
            "last_active_date": cand.get("last_active_date", "2026-06-14")
        }
        
        # Fetch related sub-records
        skills = self.fetch_skills(candidate_id)
        career = self.fetch_history(candidate_id)
        certifications = self.fetch_certifications(candidate_id)
        
        return {
            "candidate_id": candidate_id,
            "profile": profile,
            "skills": skills,
            "career_history": career,
            "certifications": certifications,
            "redrob_signals": redrob_signals,
            "document_text": cand.get("document_text", "")
        }

    def fetch_many(self, candidate_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Batch retrieves multiple candidate profiles by list of IDs.
        Maintains order compatibility where possible.
        """
        if not candidate_ids:
            return []
            
        placeholders = ",".join("?" for _ in candidate_ids)
        rows = self.db.execute_read(
            f"SELECT candidate_id FROM candidates WHERE candidate_id IN ({placeholders})",
            tuple(candidate_ids)
        )
        
        found_set = set(row["candidate_id"] for row in rows)
        
        # Rebuild records sequentially using the order of requested IDs
        results = []
        for cid in candidate_ids:
            if cid in found_set:
                cand = self.fetch_by_id(cid)
                if cand:
                    results.append(cand)
                    
        return results
