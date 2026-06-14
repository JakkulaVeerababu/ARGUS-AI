"""
Purpose: Virtual index manager using SQLite FTS5 for O(log N) BM25 full-text search.
Inputs:
    - manager: Optional[SQLiteManager] (shared database connection singleton)
Outputs:
    - FTSIndexManager instance exposing search queries
Complexity: O(log N) search retrieval.
Production Concerns: Escaping special MATCH syntax parameters to prevent database query failures; negating SQLite's native bm25() score (since lower is better by default in FTS5).
Future Improvements: Support custom term weights and phrase proximity matching (e.g. using NEAR/5 operators).
"""
import re
from typing import List, Tuple, Optional
from backend.app.database.sqlite_manager import SQLiteManager

class FTSIndexManager:
    def __init__(self, manager: Optional[SQLiteManager] = None):
        self.db = manager or SQLiteManager()

    def clean_query_term(self, term: str) -> str:
        """Sanitizes query term to prevent MATCH parsing syntax errors."""
        # Remove non-alphanumeric chars
        return re.sub(r"[^\w\s]", "", term).strip()

    def search(self, query: str, limit: int = 1000) -> List[Tuple[str, float]]:
        """
        Queries the FTS5 virtual table using MATCH operator.
        Uses FTS5's built-in bm25() function.
        Negates bm25() so that higher score represents higher relevancy.
        Returns:
            - A list of tuples: (candidate_id, negated_bm25_score)
        """
        # Split terms and sanitize
        raw_words = query.split()
        sanitized_words = []
        for word in raw_words:
            cleaned = self.clean_query_term(word)
            if cleaned:
                sanitized_words.append(cleaned)
                
        if not sanitized_words:
            return []
            
        # Join words with OR operator to match lexical search behavior
        match_expression = " OR ".join(sanitized_words)
        
        sql = """
            SELECT candidate_id, -bm25(candidate_fts) as fts_score 
            FROM candidate_fts 
            WHERE candidate_fts MATCH ? 
            ORDER BY fts_score DESC 
            LIMIT ?
        """
        
        rows = self.db.execute_read(sql, (match_expression, limit))
        return [(row["candidate_id"], float(row["fts_score"])) for row in rows]
