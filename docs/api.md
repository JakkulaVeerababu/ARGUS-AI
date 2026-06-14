# FastAPI Backend API Documentation

The backend service is built using FastAPI and run via Uvicorn on port `8000`.

## Base URL
```text
http://localhost:8000
```

---

## Endpoints

### 1. Health Check
Checks if the API server and all module dependencies are online and functioning.

- **URL**: `/health`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "status": "healthy",
    "service": "argus-ai-backend"
  }
  ```

### 2. Search & Rank Candidates
Accepts a raw job description string, writes it to a temporary file, executes the full hybrid ranking and gatekeeper pipeline, and returns the top 50 safe recommendations.

- **URL**: `/api/search`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "job_description": "Job description text goes here..."
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "results": [
      {
        "candidate_id": "CAND_0000001",
        "candidate_name": "Anonymized Candidate 1",
        "current_title": "Senior ML Engineer",
        "years_of_experience": 8.0,
        "location": "Bangalore, India",
        "cross_encoder_score": 1.25,
        "sigmoid_ce_score": 0.777,
        "multipliers": {
          "experience": 1.0,
          "role": 1.0,
          "location": 1.0,
          "engagement": 1.0,
          "github": 1.0,
          "notice": 1.0,
          "profile_quality": 1.0
        },
        "final_score": 0.777,
        "reasoning": "Senior ML Engineer with 8.0 years of experience..."
      }
    ]
  }
  ```

### 3. Get Candidate Detail Profile
Retrieves the full parsed JSON profile of a candidate from the database pool.

- **URL**: `/api/candidate/{candidate_id}`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "candidate_id": "CAND_0000001",
    "profile": {
      "anonymized_name": "Anonymized Candidate 1",
      "current_title": "Senior ML Engineer",
      "years_of_experience": 8.0,
      "location": "Bangalore"
    },
    "skills": [
      {"name": "Python", "proficiency": "expert", "duration_months": 48}
    ],
    "career_history": [
      {"company": "Flipkart", "title": "ML Engineer", "start_date": "2020-01-01", "end_date": "2024-01-01"}
    ],
    "redrob_signals": {
      "profile_completeness_score": 95,
      "notice_period_days": 30,
      "github_activity_score": 75
    }
  }
  ```

### 4. Get Current Top 100 Rankings
Reads the pre-computed `submission.csv` rankings file and returns the list of candidates mapped with profile names and locations.

- **URL**: `/api/rankings`
- **Method**: `GET`
- **Response**:
  ```json
  [
    {
      "candidate_id": "CAND_0000001",
      "rank": 1,
      "score": 0.952,
      "reasoning": "...",
      "name": "...",
      "title": "...",
      "experience": 8.0,
      "location": "...",
      "github_score": 75.0,
      "response_rate": 0.90,
      "notice_period": 30
    }
  ]
  ```

### 5. Get Analytics Stats
Aggregates candidate statistics (experience distributions, notice period bands, regional cities) for the dashboard visualizations.

- **URL**: `/api/analytics`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "kpis": {
      "total_candidates": 100,
      "average_match_score": 0.885,
      "top_locations": [{"city": "Bangalore", "count": 42}]
    },
    "distributions": {
      "experience": [{"range": "5-9 yrs", "count": 78}],
      "notice_period": [{"timeline": "<30 days", "count": 60}],
      "locations": [{"name": "Bangalore", "value": 42}]
    }
  }
  ```

### 6. Download Submission CSV File
Returns the final generated `submission.csv` directly as a download file.

- **URL**: `/api/submission`
- **Method**: `GET`
- **Response**: File response (`text/csv` download of `submission.csv`).
