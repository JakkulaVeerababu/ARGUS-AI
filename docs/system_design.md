# System Design & Implementation Choices

Argus AI balances mathematical ranking precision with real-world business requirements. This document outlines the rationale behind our design and technical architecture.

---

## 1. Hybrid Retrieval Architecture
Our hybrid search combines lexical and semantic search to achieve high recall and precision.

### 1.1 Lexical Branch: Okapi BM25
- **Why**: BM25 computes TF-IDF representations of keyword tokens. In recruitment, exact matches are critical. A candidate who knows `PEFT` or `Qlora` must be ranked above one who knows generic "machine learning models".
- **Implementation**: The corpus vocabulary is tokenized using alphanumeric regular expressions. We fit a `rank-bm25` index on the preprocessed 100k candidate profiles and serialize it to `artifacts/bm25_index.pkl`.

### 1.2 Semantic Branch: Dense Vector Embeddings (FAISS)
- **Why**: Recruiter queries contain conceptual terms like "fine-tuning LLMs" or "retrieval strategies". These terms are semantically similar to statements like "adapting transformer models" or "FAISS search indices".
- **Implementation**: We stream candidates and generate dense embeddings using `all-MiniLM-L6-v2`. L2-normalized embeddings are added to a FAISS Flat Inner Product index (`IndexFlatIP`). The inner product calculated matches **Cosine Similarity** exactly, eliminating scale discrepancies.

### 1.3 Fusion: Reciprocal Rank Fusion (RRF)
- **Why**: Lexical and semantic search output raw scores in different ranges (BM25 output is unbounded, while Cosine Similarity is constrained to `[-1, 1]`). Standard linear combination requires parameter tuning.
- **Implementation**: RRF assigns a score based solely on the candidate's rank in each list, using a constant parameter ($k=60$). This ensures balanced relevance combination without parameter tuning.

---

## 2. Re-Ranking Layer: Cross-Encoder
- **Why**: Bi-Encoder models (used in initial retrieval) compute query and document representations independently. They fail to capture word-level semantic alignment.
- **Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2` is fed the concatenated `(query, document)` string. It uses self-attention to evaluate full semantic matches, producing a cross-encoder score.
- **Latency Control**: To limit runtime, we only rerank the top 300 candidates. Reranking on CPU completes in **15.13 seconds**.

---

## 3. Signal Engineering & Scoring Heuristics
- **Sigmoid Scaling**: Cross-encoder scores are logits (e.g. `[-10, 10]`). We scale logits to `(0, 1)` bounds using a Sigmoid function before multiplying factors. This keeps multipliers mathematically consistent and preserves relative rank orders.
- **Multiplier Factors**: We apply multipliers to align rankings with target recruiter parameters:
  - NCR/Bangalore/Pune/Mumbai location proximity
  - Product company focus over service companies
  - Open-to-work and notice period timelines
  - GitHub open source commit history
  - Profile data completeness

---

## 4. Gatekeeper Gateway
- **Why**: Candidate pools contain fraudulent entries. Excluding these ensures high quality recommendations.
- **Rules**: We enforce rules to catch anomalies:
  - Expected salary minimum exceeds maximum.
  - Claimed duration of a role exceeds start and end dates.
  - Claims of "expert" skills with 0 months duration.
  - Future certifications (> 2026).

---

## 5. Explainability Layer
- **Why**: Large Language Models (LLMs) are slow, expensive, offline-incompatible, and prone to hallucinations.
- **Implementation**: We use a deterministic template-based reasoning engine. It compiles candidate statistics into natural sentences. It guarantees factual accuracy and adheres to the **40-80 words** limit.
