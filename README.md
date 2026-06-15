# Argus AI: Intelligent Candidate Discovery & Ranking Engine

Argus AI is a production-grade, high-performance candidate sourcing and search engine. It transforms talent acquisition by moving beyond simple keyword matching into semantic discovery. 

By combining **Hybrid Retrieval** (BM25 + FAISS Dense Vector search), **ONNX-optimized Cross-Encoder reranking**, custom **Sigmoid-scaled business scoring**, and a **zero-tolerance Honeypot Gatekeeper**, Argus AI sorts through a database of **100,000 candidates** to recommend the top 100 safe and qualified profiles for technical roles in under a second.

---

## 🚀 Hackathon Quick Start (Step-by-Step)

Follow these steps to set up the environment, run the ML pipeline, and launch the interactive Web SaaS dashboard.

### Prerequisites
* **Python**: Version `3.11` or `3.12` installed.
* **Node.js**: Version `18` or higher installed.

---

### Step 1: Clone and Navigate to the Project
Open your terminal and enter the project directory:
```bash
cd "ARGUS AI"
```

---

### Step 2: Set Up the Backend Environment
Create a virtual environment, activate it, and install all required dependencies:

**For Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**For macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Initialize the Database and Pre-Compute Search Indices
To run candidate retrieval at scale, we initialize the SQLite database and pre-compile the lexical and dense vector indices.

1. **Seed and Migrate SQLite Candidate Database**:
   ```bash
   python -c "from backend.app.database.migration import DatabaseMigrator; migrator = DatabaseMigrator(); migrator.migrate('data/candidates.jsonl')"
   ```

2. **Generate Dense Vector Embeddings** (computes and L2-normalizes 100k candidate embeddings on CPU):
   ```bash
   python -m backend.app.retrieval.embedding_generator
   ```

3. **Build the FAISS Index** (creates flat inner product search index for cosine similarity):
   ```bash
   python -m backend.app.retrieval.faiss_index
   ```

4. **Build the BM25 Lexical Index**:
   ```bash
   # Windows PowerShell
   $env:PYTHONPATH="."
   python -m backend.app.retrieval.bm25_index

   # macOS/Linux
   PYTHONPATH=. python -m backend.app.retrieval.bm25_index
   ```

---

### Step 4: Run the Candidate Ranking Pipeline (CLI Orchestrator)
Execute the end-to-end ML pipeline directly using the CLI orchestrator. This parses the target job description, performs hybrid retrieval, reranks with the Cross-Encoder model, scales scores, filters fraudulent candidates, and compiles the final `submission.csv` list:
```bash
python rank.py --candidates ./data/candidates.jsonl --jd ./data/job_description.docx --out ./submission.csv
```
The output `submission.csv` will contain exactly the top 100 safe and sorted candidates.

---

### Step 5: Start the Web SaaS Application
Launch the backend REST APIs and the interactive React recruiter dashboard.

1. **Start FastAPI Backend (Port 8000)**:
   ```bash
   # Windows PowerShell
   $env:PYTHONPATH="."
   python backend/app/main.py

   # macOS/Linux
   PYTHONPATH=. python backend/app/main.py
   ```
   *Verify backend is healthy by visiting: [http://localhost:8000/health](http://localhost:8000/health)*

2. **Start React Frontend (Port 5173)**:
   Open a new terminal window/tab:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Open your browser and navigate to: [http://localhost:5173/](http://localhost:5173/)*

---

### Step 6: Run Verification Tests
Verify all retrieval, ranking, scoring, explanation, database, and honeypot rules using the test suite:
```bash
# Windows PowerShell
$env:PYTHONPATH="."
pytest tests/ -v

# macOS/Linux
PYTHONPATH=. pytest tests/ -v
```

---

## 🎨 System Architecture Pipeline

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

## 🛠️ Technical Stack

### Backend Sourcing Engine
* **Language**: Python 3.11 / 3.12
* **APIs**: FastAPI, Uvicorn, Pydantic (v2)
* **Lexical Search**: `rank-bm25` (Okapi BM25 algorithm)
* **Vector Search**: `faiss-cpu` (L2 Normalized flat inner product matching)
* **Transformers**: `sentence-transformers==2.7.0`, `transformers==4.57.6` (`all-MiniLM-L6-v2` & `cross-encoder/ms-marco-MiniLM-L-6-v2`)
* **Model Optimizations**: ONNX Runtime, Hugging Face `optimum`, thread-safe batch scheduler
* **Utilities**: `loguru` (structured JSON logging), `pytest` (test automation), `pandas`, `numpy`

### Frontend Recruiter Dashboard
* **Framework**: React 19 (TypeScript, Vite 8)
* **Styling**: Tailwind CSS v4, Lucide React (Stripe-inspired clean white SaaS design)
* **Data Visualizations**: Recharts (distribution analysis)
* **APIs Integration**: TanStack Query (`@tanstack/react-query`), native fetch client

---

## 📈 Execution Performance Metrics (CPU Benchmarks)
* **Pool Size**: 100,000 candidates
* **Embedding Dimensions**: 384 (using `all-MiniLM-L6-v2`)
* **Pipeline Latency**: **55.35 seconds** (incorporating full Cross-Encoder reranking and gatekeeper validations)
* **FAISS Build Time**: **0.19 seconds**
* **Model Inference Latency** (Reranking limit CPU benchmark):
  * **Top 150**: `0.27s`
  * **Top 200 (Default)**: `0.55s` (Optimal sweet spot between precision and sub-second API response)
  * **Top 300**: `0.86s`
* **Honeypot Filter Rate**: 100% (0% fraud rate allowed in the final selected pool)

---

## 📖 Recruitment Defend Q&As (For Judges & Reviewers)

### Q1: Why BM25 + FAISS Hybrid Search instead of a single search index?
* **Lexical Search (BM25)** matches precise keywords (e.g. `C++`, `PEFT`, `Qlora`) which dense embedding models might overlook due to vocabulary abstraction.
* **Dense Vector Search (FAISS)** matches semantic intent and concepts (e.g. "building search pipelines" matches candidate statements about "information retrieval and vector search").
* **Reciprocal Rank Fusion (RRF)** merges their scores without requiring scale calibration, pulling candidates that excel in both lexical and semantic domains to the top.

### Q2: Why use a Cross-Encoder for reranking?
* Bi-encoders (like the sentence embedding model) generate independent embeddings for the query and document, comparing them via cosine similarity. While extremely fast, they miss word-to-word interactions between the query and candidate profile.
* A **Cross-Encoder** feeds the query and candidate text *together* into the attention layers of the transformer, computing a deep token-level match. This produces a highly accurate relevancy score.

### Q3: Why scale Cross-Encoder scores through a Sigmoid function before business logic?
* Cross-encoder output scores are raw logits that can range from negative values (highly irrelevant) to positive values (highly relevant). 
* If we multiply raw negative logits by positive business signals (e.g. Pune location matching factor of `1.0`), we reverse the scoring logic (a worse logit of `-5.0` becomes `-5.0`, whereas a better logit of `-2.0` becomes `-2.0`, but multiplication with penalties changes relation orders).
* Passing logits through a **Sigmoid function** maps them onto a strict positive `(0, 1)` range, ensuring business multipliers consistently reward and penalize candidates.

### Q4: Why use a deterministic Template Engine for reasoning instead of a Generative LLM?
* **Hallucination Risk**: Large Language Models (LLMs) can invent facts (e.g. claim a candidate worked at a company or has years of experience not present in the JSON profile).
* **Reproduction**: Recruiter pipelines require deterministic outputs. Running the pipeline twice must output identical reasoning.
* **Constraint Compliance**: The challenge mandates natural, factual descriptions strictly within the **40-80 words** range. Pre-configured logic guarantees word limits are never violated.

### Q5: Why is Honeypot Filtering critical?
* Candidate pools often contain invalid, fraudulent, or highly suspicious profiles (such as claims of `expert` skills with `0 months` duration, certifications dated in the future, or salary minimums exceeding their maximums).
* Excluding these upfront prevents spam from entering the recruiter review list and guarantees high candidate quality.
