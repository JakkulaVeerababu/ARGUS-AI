# Argus AI: Intelligent Candidate Discovery & Ranking Engine

Argus AI is a production-grade talent acquisition search engine. It transforms candidate sourcing from simple keyword matching into an active, semantic discovery platform. 

By utilizing Hybrid Retrieval (BM25 + FAISS Dense Vector search), Cross-Encoder reranking, custom business scoring heuristics, and a zero-tolerance honeypot validation gateway, Argus AI generates explainable recommendations for complex technical roles.

---

## 1. System Pipeline Architecture

The ranking and selection engine progresses through a series of stages to narrow down a 100k candidate database into the top 100 safe profiles:

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

---

## 2. Technical Stack

### Backend Sourcing Engine
- **Language**: Python 3.11 / 3.12
- **APIs**: FastAPI, Uvicorn, Pydantic
- **Lexical Search**: `rank-bm25` (Okapi BM25 algorithm)
- **Vector Search**: `faiss-cpu` (L2 Normalized flat inner product matching)
- **Transformers**: `sentence-transformers==2.7.0`, `transformers==4.40.0` (all-MiniLM-L6-v2 & cross-encoder/ms-marco-MiniLM-L-6-v2)
- **Utilities**: `loguru` (structured JSON logging), `pytest` (test automation), `pandas`, `numpy`

### Frontend Recruiter Dashboard
- **Framework**: React 19 (TypeScript, Vite 8)
- **Styling**: Tailwind CSS v4, Lucide React (Stripe-inspired clean white SaaS design)
- **Data Visualizations**: Recharts (distribution analysis)
- **APIs Integration**: TanStack Query (@tanstack/react-query), vanilla fetch client

---

## 3. Folder Directory Structure

```txt
argus-ai/
├── backend/
│   └── app/
│       ├── api/            # API endpoints & routing configurations
│       ├── honeypots/      # Fraudulent profile filter gateways
│       ├── jd_parser/      # Docx requirements parser engine
│       ├── ranking/        # Cross-encoder transformer scripts
│       ├── reasoning/      # Explainability reasoning templates
│       ├── retrieval/      # BM25 & FAISS vector search indices
│       ├── signals/        # Business logic scoring & multipliers
│       ├── utils/          # Logger.py & custom format parsers
│       └── main.py         # FastAPI root server module
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable layout blocks
│   │   ├── pages/          # Search, Rankings, and Analytics views
│   │   ├── services/       # API call handlers for FastAPI
│   │   ├── types/          # TS Interfaces definitions
│   │   ├── App.tsx         # Tabbed main layout framework
│   │   └── index.css       # Tailwind v4 imports
│   └── package.json        # Frontend library mappings
├── artifacts/              # Pre-computed indices (BM25, FAISS, Embeddings)
├── data/                   # Candidate dataset pool & job descriptions
├── docs/                   # Visual screenshots & architectural assets
├── tests/                  # Pytest unit testing modules
├── docker/                 # Containerization setup (Dockerfile & docker-compose.yml)
├── rank.py                 # Master ranking CLI orchestrator
└── submission.csv          # Final top-100 compliant output
```

---

## 4. Setup & Running Instructions

### 4.1 Backend Environment Setup
Create a virtual environment, activate it, and install required libraries:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```

### 4.2 Run Pre-computations (Index Creation)
1. **BM25 Lexical Index**:
   ```bash
   $env:PYTHONPATH="."
   python -m backend.app.retrieval.bm25_index
   ```
2. **Dense Vector Embeddings** (computes and L2-normalizes 100k candidate embeddings on CPU):
   ```bash
   python -m backend.app.retrieval.embedding_generator
   ```
3. **FAISS Vector Index**:
   ```bash
   python -m backend.app.retrieval.faiss_index
   ```

### 4.3 Run the Candidate Ranking Pipeline CLI
Execute the end-to-end pipeline to compile `submission.csv`:
```bash
python rank.py --candidates ./data/candidates.jsonl --jd ./data/job_description.docx --out ./submission.csv
```

### 4.4 Run Verification Tests
Verify all retrieval, ranking, explanation, and honeypot rules:
```bash
$env:PYTHONPATH="."
pytest tests/
```

### 4.5 Start the Web Application Servers
To launch the backend API server and frontend dashboard locally:
1. **Start FastAPI Backend (Port 8000)**:
   ```bash
   $env:PYTHONPATH="."
   python backend/app/main.py
   ```
2. **Start React Frontend (Port 5173)**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 5. Recruitment Interview & Defend Q&As

### Q1: Why BM25 + FAISS Hybrid Search instead of a single search index?
- **Lexical Search (BM25)** matches precise keywords (e.g. `C++`, `PEFT`, `Qlora`) which dense embedding models might overlook due to vocabulary abstraction.
- **Dense Vector Search (FAISS)** matches semantic intent and concepts (e.g. "building search pipelines" matches candidate statements about "information retrieval and vector search").
- **Reciprocal Rank Fusion (RRF)** merges their scores without requiring scale calibration, pulling candidates that excel in both lexical and semantic domains to the top.

### Q2: Why use a Cross-Encoder for reranking?
- Bi-encoders (like the sentence embedding model) generate independent embeddings for the query and document, comparing them via cosine similarity. While extremely fast, they miss word-to-word interactions between the query and candidate profile.
- A **Cross-Encoder** feeds the query and candidate text *together* into the attention layers of the transformer, computing a deep token-level match. This produces a highly accurate relevancy score.

### Q3: Why scale Cross-Encoder scores through a Sigmoid function before business logic?
- Cross-encoder output scores are raw logits that can range from negative values (highly irrelevant) to positive values (highly relevant). 
- If we multiply raw negative logits by positive business signals (e.g. Pune location matching factor of `1.0`), we reverse the scoring logic (a worse logit of `-5.0` becomes `-5.0`, whereas a better logit of `-2.0` becomes `-2.0`, but multiplication with penalties changes relation orders).
- Passing logits through a **Sigmoid function** maps them onto a strict positive `(0, 1)` range, ensuring business multipliers consistently reward and penalize candidates.

### Q4: Why use a deterministic Template Engine for reasoning instead of a Generative LLM?
- **Hallucination Risk**: Large Language Models (LLMs) can invent facts (e.g. claim a candidate worked at a company or has years of experience not present in the JSON profile).
- **Reproduction**: Recruiter pipelines require deterministic outputs. Running the pipeline twice must output identical reasoning.
- **Constraint Compliance**: The challenge mandates natural, factual descriptions strictly within the **40-80 words** range. Pre-configured logic guarantees word limits are never violated.

### Q5: Why is Honeypot Filtering critical?
- Candidate pools often contain invalid, fraudulent, or highly suspicious profiles (such as claims of `expert` skills with `0 months` duration, certifications dated in the future, or salary minimums exceeding their maximums).
- Excluding these upfront prevents spam from entering the recruiter review list and guarantees high candidate quality.

---

## 6. Execution Performance Metrics
- **Pool Size**: 100,000 candidates
- **Embedding Dimensions**: 384 (using all-MiniLM-L6-v2)
- **Pipeline Latency**: **55.35 seconds** (incorporating full Cross-Encoder reranking and gatekeeper validations)
- **FAISS Build Time**: **0.19 seconds**
- **Honeypot Filter Rate**: 100% (0% fraud rate allowed in the final selected pool)
- **Validation**: Pass (fully compliant with challenge schemas and ordering rules)
