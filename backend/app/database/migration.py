"""
Purpose: Data migration module to parse raw JSONL files and ingest records into SQLite in transactions of batch size 1000.
Inputs:
    - candidates_path: str (path to candidates.jsonl)
    - db_path: Optional[str] (sqlite database path)
Outputs:
    - Relational tables and FTS virtual indexes populated.
Complexity: O(N) where N is candidate pool size.
Production Concerns: Memory footprint (stream JSONL, do not load entire file in RAM); transaction optimization (bulk inserts inside transactions).
Future Improvements: Support parallel processing or bulk COPY imports for large databases.
"""

import os
import json
import gzip
import time
from typing import Optional, Any

from backend.app.database.sqlite_manager import SQLiteManager
from backend.app.preprocessing.document_builder import build_candidate_document


class DatabaseMigrator:
    def __init__(self, db_path: Optional[str] = None):
        self.manager = SQLiteManager(db_path)
        self.conn = self.manager.get_connection()

    def initialize_schema(self):
        """Loads and executes schema.sql to set up tables and indices."""
        schema_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "schema.sql")
        )
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema SQL file not found at: {schema_path}")

        print(f"Reading schema from: {schema_path}")
        with open(schema_path, "r", encoding="utf-8") as f:
            sql = f.read()

        # Execute schema script
        self.conn.executescript(sql)
        self.conn.commit()
        print("Database schema initialized successfully.")

    def stream_jsonl(self, filepath: str) -> Any:
        """Memory-safe generator streaming JSON lines."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source JSONL file not found at: {filepath}")

        if filepath.endswith(".gz"):
            open_func = gzip.open
            mode = "rt"
        else:
            open_func = open
            mode = "r"

        with open_func(filepath, mode, encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                yield json.loads(line_str)

    def migrate(self, jsonl_path: str, batch_size: int = 1000):
        """Runs the batch database migration process."""
        print(f"Starting data migration from: {jsonl_path}...")
        start_time = time.time()

        # Initialize target structures
        self.initialize_schema()

        # Clear existing data to allow clean re-runs
        print("Clearing old candidate records...")
        self.conn.execute("DELETE FROM candidates;")
        self.conn.execute("DELETE FROM candidate_fts;")
        self.conn.commit()

        # Ingestion lists
        candidates_batch = []
        skills_batch = []
        history_batch = []
        certs_batch = []
        fts_batch = []

        total_migrated = 0

        # SQL insert statements
        insert_cand_sql = """
            INSERT INTO candidates (
                candidate_id, anonymized_name, current_title, years_of_experience, location,
                current_company, current_industry, headline, summary, profile_completeness_score,
                notice_period_days, github_activity_score, recruiter_response_rate, offer_acceptance_rate,
                interview_completion_rate, open_to_work, is_remote, willing_to_relocate, last_active_date, document_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        insert_skill_sql = "INSERT INTO skills (candidate_id, name, proficiency, duration_months) VALUES (?, ?, ?, ?)"

        insert_history_sql = """
            INSERT INTO career_history (candidate_id, title, company, start_date, end_date, duration_months, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        insert_cert_sql = "INSERT INTO certifications (candidate_id, name, issuer, issue_date) VALUES (?, ?, ?, ?)"

        insert_fts_sql = (
            "INSERT INTO candidate_fts (candidate_id, document_text) VALUES (?, ?)"
        )

        for cand in self.stream_jsonl(jsonl_path):
            cid = cand.get("candidate_id")
            profile = cand.get("profile", {})
            signals = cand.get("redrob_signals", {})

            # Reconstruct document text representation
            doc_text = build_candidate_document(cand)

            # Map core candidate values
            cand_tuple = (
                cid,
                profile.get("anonymized_name", ""),
                profile.get("current_title", ""),
                profile.get("years_of_experience", 0.0),
                profile.get("location", ""),
                profile.get("current_company", ""),
                profile.get("current_industry", ""),
                profile.get("headline", ""),
                profile.get("summary", ""),
                signals.get("profile_completeness_score", 100.0),
                signals.get("notice_period_days", 0),
                signals.get("github_activity_score", 0.0),
                signals.get("recruiter_response_rate", 0.0),
                signals.get("offer_acceptance_rate", 0.0),
                signals.get("interview_completion_rate", 0.0),
                1 if signals.get("open_to_work", False) else 0,
                1 if signals.get("is_remote", False) else 0,
                1 if signals.get("willing_to_relocate", False) else 0,
                signals.get("last_active_date", "2026-06-14"),
                doc_text,
            )

            candidates_batch.append(cand_tuple)
            fts_batch.append((cid, doc_text))

            # Map skills list
            for s in cand.get("skills", []):
                skills_batch.append(
                    (
                        cid,
                        s.get("name", ""),
                        s.get("proficiency", ""),
                        s.get("duration_months", 0),
                    )
                )

            # Map career history
            for job in cand.get("career_history", []):
                history_batch.append(
                    (
                        cid,
                        job.get("title", ""),
                        job.get("company", ""),
                        job.get("start_date", ""),
                        job.get("end_date", ""),
                        job.get("duration_months", 0),
                        job.get("description", ""),
                    )
                )

            # Map certifications
            for c in cand.get("certifications", []):
                certs_batch.append(
                    (
                        cid,
                        c.get("name", ""),
                        c.get("issuer", ""),
                        c.get("issue_date", ""),
                    )
                )

            # Execute database commits when batch threshold is reached
            if len(candidates_batch) >= batch_size:
                self._execute_batch(
                    insert_cand_sql,
                    candidates_batch,
                    insert_skill_sql,
                    skills_batch,
                    insert_history_sql,
                    history_batch,
                    insert_cert_sql,
                    certs_batch,
                    insert_fts_sql,
                    fts_batch,
                )
                total_migrated += len(candidates_batch)
                print(f"  Ingested {total_migrated} candidates...")

                # Reset buffers
                candidates_batch.clear()
                skills_batch.clear()
                history_batch.clear()
                certs_batch.clear()
                fts_batch.clear()

        # Ingest remainder records
        if candidates_batch:
            self._execute_batch(
                insert_cand_sql,
                candidates_batch,
                insert_skill_sql,
                skills_batch,
                insert_history_sql,
                history_batch,
                insert_cert_sql,
                certs_batch,
                insert_fts_sql,
                fts_batch,
            )
            total_migrated += len(candidates_batch)

        print(
            f"Data migration finished. Ingested total: {total_migrated} profiles in {time.time() - start_time:.2f} seconds."
        )

    def _execute_batch(
        self,
        cand_sql,
        cand_list,
        skill_sql,
        skill_list,
        hist_sql,
        hist_list,
        cert_sql,
        cert_list,
        fts_sql,
        fts_list,
    ):
        """Internal helper to execute SQL lists under single transaction block."""
        # Using context manager auto-begins transaction
        with self.conn:
            cursor = self.conn.cursor()
            cursor.executemany(cand_sql, cand_list)
            if skill_list:
                cursor.executemany(skill_sql, skill_list)
            if hist_list:
                cursor.executemany(hist_sql, hist_list)
            if cert_list:
                cursor.executemany(cert_sql, cert_list)
            cursor.executemany(fts_sql, fts_list)
