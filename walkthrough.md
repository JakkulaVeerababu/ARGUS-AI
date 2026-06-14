# Argus AI Production Delivery Walkthrough

Argus AI is now a fully functional, production-ready, intelligent candidate discovery and ranking system. We transitioned the project from raw datasets to an end-to-end ML pipeline integrated with a FastAPI backend, a React + Vite dashboard, automated testing, containerization, and logging utilities.

---

## 1. System Pipeline & Execution

The architecture operates in a multi-stage retrieval and reranking layout:

![System Architecture Diagram](file:///c:/Users/LENOVO/Desktop/ARGUS%20AI/docs/architecture.png)

### 1.1 Pre-computation Phase
- **Embedding Generation**: Streams and processes all 100,000 candidate profiles from `candidates.jsonl`, generating dense 384-dimensional embeddings on CPU using the `all-MiniLM-L6-v2` model. The normalized vectors are saved to `artifacts/candidate_embeddings.npy` along with candidate ID mappings in `artifacts/candidate_ids.pkl`.
- **FAISS Indexing**: Builds the FAISS Index (`artifacts/faiss_index.bin`) using a Flat Inner Product index (`IndexFlatIP`) matching unit vectors for rapid cosine similarity lookups in **0.19 seconds**.

### 1.2 Pipeline Execution
We executed the master ranking orchestrator (`rank.py`):
```bash
$env:PYTHONPATH="."; .\.venv\Scripts\python.exe rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
```

**Execution Log Output Summary:**
- **Job Description Parsing**: Parsed and extracted keywords (e.g. `ai engineer`, `faiss`, `machine learning`, `peft`, `qlora`, `xgboost`).
- **Hybrid Retrieval**: Retrieved candidate documents through lexical search (BM25) and semantic search (FAISS Index), combining rankings using Reciprocal Rank Fusion (RRF, $k=60$) to obtain the top 300 candidates.
- **Cross-Encoder Reranking**: Processed 300 candidate pairs through `cross-encoder/ms-marco-MiniLM-L-6-v2` on CPU to narrow down to the top 200 candidates.
- **Business Scoring**: Applied multipliers (experience, role, location target matching, recruiter response rate, GitHub activity, notice period, profile completeness) scaling CE score logits through a Sigmoid activation.
- **Honeypot Gatekeeper**: Scanned the top candidates to eliminate invalid profiles. Filtered **3 honeypots** with logical violations (`Salary min > max`):
  - `CAND_0066376`
  - `CAND_0051004`
  - `CAND_0029367`
- **Output**: Wrote exactly 100 verified, safe, and sorted candidate rows to `submission.csv` with a final pipeline run-time of **55.35 seconds**.

---

## 2. Validation & Compliance

### 2.1 Challenge Rule Validation
We copied and validated `submission.csv` using the challenge's strict validator script (`data/validate_submission.py`):
```bash
$env:PYTHONPATH="."; .\.venv\Scripts\python.exe ./data/validate_submission.py ./submission.csv
```
> [!NOTE]
> **Output:** `Submission is valid.`
> The CSV conforms strictly to:
> - Exactly 100 candidate data rows
> - Correct columns: `candidate_id,rank,score,reasoning`
> - Strictly non-increasing score order by rank
> - Deterministic tie-breaking (equal scores broken by candidate ID alphabetically ascending)
> - Real, factual explanation reasoning under 40-80 words constraints

### 2.2 Automated Test Suite
We wrote 14 test cases under the `tests/` directory covering:
- **Lexical/BM25 Indexing & RRF Fusion**
- **Sigmoid Logit Mapping & Business Scoring Pipeline**
- **Reasoning Template Engine Length Limits**
- **Honeypots Checks (Salary, timeline anomalies, expert skills)**
- **Tie-breakers & Format constraints**

**Pytest Run Result:**
```bash
$env:PYTHONPATH="."; .\.venv\Scripts\pytest.exe
======================= 14 passed, 2 warnings in 18.40s =======================
```
All unit tests pass successfully!

---

## 3. Web SaaS Dashboard Integration

The FastAPI backend and React frontend are configured and running locally:
- **Backend API**: Port `8000` serves endpoints `/health`, `/api/search`, `/api/candidate/{id}`, `/api/rankings`, and `/api/analytics`.
- **Frontend App**: Port `5173` runs the Vite dashboard built in premium Stripe/Ashby clean white SaaS style (using Tailwind CSS v4, Lucide React, and Recharts).

### Dashboard Interfaces:

#### Recruiter Dashboard Overview
Displays overview stats (Total Candidate Pool size, match indicators, regional locations, notice period timelines):
![Recruiter Dashboard Overview](file:///c:/Users/LENOVO/Desktop/ARGUS%20AI/docs/screenshots/dashboard.png)

#### Search Engine Query Matcher
Pasting Job Description and executing the real-time Cross-Encoder ranking:
![Search Engine Query Matcher](file:///c:/Users/LENOVO/Desktop/ARGUS%20AI/docs/screenshots/search.png)

#### Top 100 Rankings explorer
Exploring the Top 100 list with explainability matches:
![Top 100 Rankings explorer](file:///c:/Users/LENOVO/Desktop/ARGUS%20AI/docs/screenshots/rankings.png)

#### Analytics & Distributions Visualizer
Recharts graphs detailing experience bands, notice timelines, and candidate locations:
![Analytics & Distributions Visualizer](file:///c:/Users/LENOVO/Desktop/ARGUS%20AI/docs/screenshots/analytics.png)

### To explore the live application:
1. Open your browser to: [http://localhost:5173/](http://localhost:5173/)
2. Navigate to **Search Engine** to paste custom JDs and see real-time Cross-Encoder score distributions and deterministic reasons.
3. Check **Top 100 Rankings** to view metrics and download the submission file.
4. Open **Analytics** to view live Recharts histograms of experience bands, notice periods, and candidate locations.

---

## 4. Productionization Assets Created
- `docker/Dockerfile`: Multi-stage Python 3.12 build configuring model cache directories.
- `docker/docker-compose.yml`: Mounts logs, artifacts, and caching volumes.
- `.github/workflows/ci.yml`: GitHub Actions pipeline verifying formatting, lint rules (ruff), test runs, and container packaging.
- `backend/app/utils/logger.py`: Configures structured file log handlers (`logs/api.log`, `logs/ranking.log`, `logs/errors.log`) using `loguru`.
