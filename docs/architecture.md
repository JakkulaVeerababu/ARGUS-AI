# System Architecture

The architecture of Argus AI is built around a multi-stage search, retrieval, reranking, and scoring pipeline. This structure balances speed and semantic accuracy, enabling scalable searches over a pool of 100,000 candidates.

## Architecture Diagram

```text
       Job Description (.docx)
                  ↓
       Requirement Extraction (Titles, Must-Have Skills, Nice-To-Have Skills)
                  ↓
   ┌──────────────┴──────────────┐
   ▼                             ▼
BM25 Lexical Search        FAISS Semantic Search (all-MiniLM-L6-v2 Embeddings)
[Retrieves Top 1,000]       [Retrieves Top 1,000]
   ▲                             ▲
   └──────────────┬──────────────┘
                  ▼
      Reciprocal Rank Fusion (RRF, k=60)
         [Combines into Top 2,000]
                  ▼
       Cross-Encoder Reranking (ms-marco-MiniLM-L-6-v2)
          [Computes Top 300 Candidate Pairs]
                  ▼
        Business Signals Scoring Heuristics (Sigmoid scaled logits)
             [Filters down to Top 200]
                  ▼
        Honeypot Gatekeeper (Salary, timeline, expert skill duration checks)
             [Eliminates fraudulent profiles]
                  ▼
          Reason Builder (Fact-based explainability templates)
                  ▼
           submission.csv (Top 100 Safe Candidates)
                  ↓
        FastAPI APIs ◄──► React Shadcn Dashboard
```

## Architectural Components

### 1. Requirements Parser
- **Technology**: `docx2txt` / regex extraction
- Parses the uploaded `.docx` Job Description to extract the target job titles, must-have skills, and nice-to-have skills, building a robust query representation.

### 2. Lexical & Semantic Retrieval Branches
- **Lexical Branch**: Okapi BM25 index matching keyword tokens. Excellent for hard search constraints like specific frameworks and programming languages.
- **Semantic Branch**: L2 Normalized flat inner product FAISS index over `all-MiniLM-L6-v2` dense embeddings. Excellent for matching broad concept associations.

### 3. Reciprocal Rank Fusion (RRF)
- Combines the ranked lists of the lexical and semantic branches using an RRF constant ($k=60$). This pushes candidates that rank high in both lists to the top without needing score calibration.

### 4. Cross-Encoder Rerank
- **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Re-scores the top 300 retrieved candidate profiles by feeding query-document sequences directly into the transformer attention blocks, capturing token-to-token semantic alignment.

### 5. Heuristic Business Scorer
- Normalizes Cross-Encoder logit scores to positive `(0, 1)` ranges using a Sigmoid function, and applies multiplier weights for candidate experience, location, platform response rates, and GitHub activity.

### 6. Fraud & Honeypot Gatekeeper
- Validates profile statistics (salary parameters, work timeline consistency, expert skill duration limits, future certifications) to filter out fraudulent data points.

### 7. Reasoning template & Submission
- Compiles natural, deterministic, fact-based explainability text for recruiter review, selecting exactly 100 final candidate rows sorted by score and tie-broken by candidate ID ascending.
