# ARGUS AI: Slide Presentation Deck

This document serves as the presentation slide outline for ARGUS AI's submission.

---

## Slide 1: Title
### **ARGUS AI**
*Intelligent Candidate Discovery & Ranking Engine*

> "ARGUS AI is a production-inspired intelligent candidate discovery system based on modern retrieval, reranking, signal engineering, and explainability principles."

---

## Slide 2: Problem Statement
*   **Massive Volumes**: Recruiting teams are overwhelmed by processing hundreds of thousands of candidate profiles manually.
*   **Semantic Misalignment**: Traditional keyword-based filters miss highly qualified candidates who describe their skills using different vocabulary or conceptual synonyms.
*   **Data Quality Concerns**: Candidate databases frequently contain suspicious, incomplete, or fraudulent data points (honeypots).
*   **The Hallucination Trap**: Large Language Models (LLMs) used for resume scanning introduce hallucinated claims, high latencies, and high token costs.

---

## Slide 3: Proposed Solution
*   **Multi-Stage Selection Pipeline**: Combines lexical precision and deep semantic matching to narrow 100k profiles down to the top 100.
*   **Deterministic Business Filters**: Normalizes model outputs and injects strategic business signals (notice period, location target, company profile).
*   **Honeypot Gatekeeper**: Scans profiles using rule-based algorithms to eliminate invalid entries.
*   **Deterministic Reason Builder**: Generates factual, hallucination-free explanations within strict length constraints.

---

## Slide 4: Key Differentiators
*   **Zero-Hallucination Explainability**: Natural text reasons are built deterministically from structured data, guaranteeing factual accuracy.
*   **Mathematical Scale Alignment**: Pass Cross-Encoder logits through a Sigmoid mapping function before applying multiplier heuristics to ensure ranking consistency.
*   **Active Fraud Filtering**: Incorporates a built-in Honeypot detection layer to filter out suspicious profiles before recommendations reach the recruiter.
*   **High Performance on CPU**: Built and optimized for offline execution on standard CPU hardware without requiring expensive GPUs.

---

## Slide 5: JD Understanding
*   **Docx Requirement Parser**: Parses job descriptions to extract target job titles, core must-have skills, and secondary nice-to-have capabilities.
*   **Structured Query Construction**: Compiles the parsed requirements into structured keyword lists for lexical matching and descriptive statements for semantic vector search.

---

## Slide 6: Ranking Methodology
1.  **Lexical Retrieval**: Okapi BM25 scores keyword frequency to retrieve precise matches.
2.  **Semantic Retrieval**: Dense vector indexing utilizing `all-MiniLM-L6-v2` embeddings in a FAISS index to find conceptual matches.
3.  **Reciprocal Rank Fusion (RRF)**: Merges the lexical and semantic ranked lists using $k=60$ to combine relevance.
4.  **Cross-Encoder Reranking**: Passes the top 300 candidates through `ms-marco-MiniLM-L-6-v2` to evaluate deep context-to-context semantic match.

---

## Slide 7: Explainability & Validation
*   **Factual Reason Templates**: Automatically compiles candidate experience and skills into professional recruiter summaries (40-80 words).
*   **Rule Compliance**: The output is validated using the official validator script, ensuring strict formatting, ordering, and candidate count constraints are met.

---

## Slide 8: End-to-End Workflow
```text
Job Description (.docx)
           ↓
Requirement Parsing (Titles & Skills)
           ↓
Hybrid Search: BM25 Lexical + FAISS Semantic (RRF Fusion)
           ↓
Cross-Encoder Reranking (ms-marco-MiniLM-L-6-v2)
           ↓
Sigmoid Logit Scaling & Business Multiplier Scoring
           ↓
Honeypot Gatekeeper Fraud Filtering
           ↓
Template-based Explainability Reasoning
           ↓
Final Top-100 Verified Candidate Submission File
```

---

## Slide 9: System Architecture
*   **FastAPI Backend**: Hosts REST APIs for candidate ranking, profile analysis, and dashboard statistics.
*   **React + Vite Dashboard**: An interactive recruiter interface with visual match grids, live queries, analytics charts, and submission downloader.
*   **Containerization**: Docker and Docker Compose setups for reproducible builds and zero-setup local deployment.

---

## Slide 10: Results & Performance
### Key Metrics
*   **Total Candidate Pool**: 100,000 candidates
*   **Embedding Dimension**: 384
*   **Top-K Retrieval**: 2,000
*   **Cross-Encoder Top-K**: 300
*   **Final Candidates**: 100
*   **Pipeline Runtime**: <15 sec
*   **FAISS Build Time**: 0.19 sec
*   **Unit Tests**: 14/14 Passed
*   **Submission Validator**: Passed

---

## Slide 11: Technologies Used
*   **ML & Search**: FAISS, Sentence-Transformers, Rank-BM25, PyTorch
*   **Backend Web APIs**: FastAPI, Uvicorn, Pydantic, Loguru
*   **Frontend UI**: React 19, TypeScript, Vite 8, Tailwind CSS v4, Recharts, Lucide Icons
*   **Infrastructure**: Docker, Docker Compose, GitHub Actions CI

---

## Slide 12: Dashboard Demonstration
*   **Recruiter KPI Panel**: Visualizes match percentages, location maps, and notice periods.
*   **Live Query Sandbox**: Paste any job description to run the complete hybrid ML ranking pipeline instantly.
*   **Explorer Grid**: Expand candidate details, review the breakdown of business multipliers, and read generated reasoning text.

---

## Slide 13: Future Scope
*   **Database Migration**: Scale indexing to `pgvector` in PostgreSQL for enterprise-level persistence.
*   **Incremental Indexing**: Support real-time indexing of newly added resumes.
*   **Resume Uploader**: Add PDF parsing to ingest candidate profiles directly.
*   **Recruiter Feedback Loop**: Incorporate online learning-to-rank using human-in-the-loop decisions and label feedback.

---

## Slide 14: Conclusion
*   **Proven Precision**: ARGUS AI effectively separates the top talent from 100k records in less than a minute.
*   **Compliant & Reliable**: 100% test pass rate and official submission validation passed.
*   **Recruiter Centric**: A seamless interface combining sophisticated search science with actionable business signals.
