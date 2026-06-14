# Retrieval & Ranking Pipeline

This document explains the candidate retrieval and ranking pipeline stages and parameters.

## Pipeline Parameters

- **Candidate Pool**: 100,000 profiles
- **Lexical/Semantic Top-K**: 1,000 candidates each
- **RRF Combined Top-N**: 2,000 candidates
- **RRF Constant ($k$)**: 60
- **Cross-Encoder Top-N**: 300 candidates
- **Scored Candidates**: 200 candidates
- **Final Selection**: 100 candidates

---

## Stages Description

### 1. Requirements Extraction
- The orchestrator extracts raw text from the Job Description file.
- It parses requirement clauses (titles, must-have skills, nice-to-have skills) to construct a structured search query.

### 2. Lexical Branch (BM25)
- Tokenizes candidate profiles and query strings.
- Scores candidates using the Okapi BM25 ranking algorithm, returning a ranked list of candidate IDs and their BM25 scores.

### 3. Semantic Branch (FAISS)
- Encodes candidate profiles into 384-dimensional dense vectors using the `all-MiniLM-L6-v2` SentenceTransformer model on CPU.
- During search, the query is embedded and matched against the populated Flat Inner Product index (`IndexFlatIP`) using FAISS. Since vectors are L2-normalized, the inner product matches Cosine Similarity.

### 4. Reciprocal Rank Fusion (RRF)
- Merges the lexical ranking list and the semantic ranking list.
- RRF score formula:
  $$RRF(d) = \sum_{m \in M} \frac{1}{k + r_m(d)}$$
  Where $M$ is the set of search branches (BM25 and FAISS), and $r_m(d)$ is the rank of candidate $d$ in search branch $m$.

### 5. Cross-Encoder Reranking
- Reranks the top 300 candidates.
- Generates query-document text pairs and scores them using the `cross-encoder/ms-marco-MiniLM-L-6-v2` transformer model on CPU.
- Employs self-attention to evaluate full semantic matches, producing a cross-encoder logit score.

### 6. Heuristic Heuristics & Business Multipliers
- Scales logits using a Sigmoid function to ensure they are strictly positive bounds `(0, 1)`.
- Calculates individual signal multipliers:
  - **Experience Multiplier**: 1.0 (ideal: 5-9 years), 0.8 (close: 3-4 or 10-12 years), 0.5 (far).
  - **Role Multiplier**: Penalizes IT outsourcing service roles to prioritize product-focused AI/ML experience.
  - **Location Multiplier**: 1.0 for NCR/Bangalore/Pune/Mumbai, 0.9 for relocatable candidates, 0.6 otherwise.
  - **Notice Period Multiplier**: Rewards immediate and short notice periods (e.g. 15-30 days).
  - **GitHub Activity Multiplier**: Multiplier based on verified open source commits.
  - **Profile Completeness Multiplier**: Reward candidates with detailed profile fields.
- Calculates final score: $Sigmoid(CE) \times \prod Factors$.

### 7. Gatekeeper Gateway
- Performs rule checks to remove honeypot profiles:
  - Salary expected min > max
  - claimed duration of role > elapsed start-end dates
  - Claimed expert proficiency in 5+ skills with 0 months duration
  - Certifications dated in the future (> 2026)
- Evaluates soft risk factors. If `risk_score > 0.5`, candidate is excluded.
- Selects the top 100 safe candidates.
