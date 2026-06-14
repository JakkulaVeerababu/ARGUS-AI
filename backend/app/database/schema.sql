-- schema.sql
-- SQLite database initialization schema for ARGUS AI candidate storage.

-- 1. Candidates Core Profile Table
CREATE TABLE IF NOT EXISTS candidates (
    candidate_id TEXT PRIMARY KEY,
    anonymized_name TEXT,
    current_title TEXT,
    years_of_experience REAL,
    location TEXT,
    current_company TEXT,
    current_industry TEXT,
    headline TEXT,
    summary TEXT,
    profile_completeness_score REAL,
    notice_period_days INTEGER,
    github_activity_score REAL,
    recruiter_response_rate REAL,
    offer_acceptance_rate REAL,
    interview_completion_rate REAL,
    open_to_work INTEGER,
    is_remote INTEGER,
    willing_to_relocate INTEGER,
    last_active_date TEXT,
    document_text TEXT
);

-- 2. Skills Table
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT,
    name TEXT,
    proficiency TEXT,
    duration_months INTEGER,
    FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

-- 3. Career History Table
CREATE TABLE IF NOT EXISTS career_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT,
    title TEXT,
    company TEXT,
    start_date TEXT,
    end_date TEXT,
    duration_months INTEGER,
    description TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

-- 4. Certifications Table
CREATE TABLE IF NOT EXISTS certifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT,
    name TEXT,
    issuer TEXT,
    issue_date TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id) ON DELETE CASCADE
);

-- 5. Full-Text Search Virtual Table (FTS5)
CREATE VIRTUAL TABLE IF NOT EXISTS candidate_fts USING fts5(
    candidate_id UNINDEXED,
    document_text
);

-- 6. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_skills_candidate ON skills(candidate_id);
CREATE INDEX IF NOT EXISTS idx_history_candidate ON career_history(candidate_id);
CREATE INDEX IF NOT EXISTS idx_certs_candidate ON certifications(candidate_id);
