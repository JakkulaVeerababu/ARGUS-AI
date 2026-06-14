# Recruitment Interview & Defense Notes

This document provides a set of questions and answers to prepare you to defend the system design decisions of Argus AI during presentations and technical reviews.

---

## 1. Why BM25 for Lexical Search?
- **Keywords Accuracy**: In technical recruiting, exact abbreviations and terms are critical. A candidate who lists `PEFT` or `Qlora` must match the job description.
- **Out of Vocabulary (OOV)**: Dense embedding models map words to fixed vector vocabularies and can miss rare technical jargon. BM25 indexes exactly the words written.
- **Efficiency**: BM25 calculations over 100k records take less than a second, serving as an efficient first-stage filter.

## 2. Why FAISS for Semantic Search?
- **Speed & Scale**: Indexing and querying 100k high-dimensional vectors in python can be slow. FAISS compiles vectors and searches them using optimized C++ threads.
- **L2 Normalized Flat Inner Product**: We pre-normalize the candidate embeddings. The inner product match calculated by `IndexFlatIP` matches **Cosine Similarity** exactly, eliminating scale differences.

## 3. Why all-MiniLM-L6-v2 for Embeddings?
- **Speed & Size**: Large models (like `E5` or `BGE`) have high latency and memory footprints on CPU. `all-MiniLM-L6-v2` is compact (120 MB), runs fast, and produces high quality embeddings.
- **Context Window**: It supports up to 256 tokens, which is ideal for representing parsed candidate profiles.

## 4. Why Cross-Encoder for Reranking?
- **Semantic Interaction**: Bi-encoders (like the sentence embedding model) generate independent embeddings for the query and document, comparing them via cosine similarity. While extremely fast, they miss word-to-word interactions between the query and candidate profile.
- **Attention Over Query-Document**: The Cross-Encoder evaluates the concatenated `(query, document)` string in a single transformer pass. This enables full cross-attention between words, resulting in more accurate ranking.

## 5. Why Sigmoid scaling on Cross-Encoder logits?
- **Logit Range**: Cross-encoder scores are unbounded logits (negative to positive). Multiplying raw logits directly by positive business signals can reverse the scoring logic (e.g. multiplying a worse logit of `-5.0` by a multiplier of `1.0` vs a penalty multiplier of `0.5`).
- **Mathematical Consistency**: Scaling logits via a Sigmoid maps them to `(0, 1)` bounds. This ensures business multipliers (e.g. location, notice period) act consistently.

## 6. Why no GPT/LLM for explainability reasoning?
- **No Hallucinations**: LLMs can invent candidate claims not present in the profile data. Our deterministic template engine compiles reasoning strictly from profile facts.
- **Speed & Cost**: Running LLM APIs for 100 candidates is slow and expensive. The template engine compiles reasons in **milliseconds**.
- **Offline Reliability**: The pipeline runs completely offline.

## 7. Why no XGBoost or Machine Learning for Business Scoring?
- **No Labeled Training Data**: Traditional ML models require high quality labeled pairs (e.g. recruiter yes/no decisions) to train.
- **Heuristic Multipliers**: Standard recruiting criteria (notice period, location, open-to-work status) are well suited for deterministic business multipliers.

## 8. Why implement a Honeypot Gatekeeper?
- **Data Quality**: Candidate databases contain fraudulent profiles.
- **Gatekeeper Rules**: Enforcing rules (salary expected min > max, timeline anomalies, expert skills with 0 duration) catches anomalies upfront. This filters out invalid data, ensuring high-quality recommendations.
