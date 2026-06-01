# ATS API Specification & Integration Plan

This document outlines the design for the ATS AI REST API, enabling backend systems to integrate resume parsing, scoring, and shortlisting capabilities.

## 1. API Architecture Overview
The API is designed using **FastAPI** to provide high-performance, asynchronous endpoints with automatic OpenAPI documentation.

### Core Technology Stack
- **Framework**: FastAPI
- **Validation**: Pydantic (v2)
- **Async Execution**: FastAPI BackgroundTasks (for simple jobs) or Redis/Celery (for production scale)
- **Documentation**: Swagger UI / ReDoc

## 2. API Endpoints

### 2.1 Resume Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/resumes/upload` | Upload a resume (PDF/DOCX) for asynchronous parsing. |
| `GET` | `/api/v1/resumes/{resume_id}` | Retrieve parsed resume data. |
| `GET` | `/api/v1/jobs/{job_id}` | Check status and results of an async parsing/scoring job. |

### 2.2 Intelligence Services
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/parse` | Synchronous parsing of raw text. |
| `POST` | `/api/v1/score` | Score a single resume against a specific Job Description. |
| `POST` | `/api/v1/shortlist` | Rank multiple resumes against a Job Description. |

---

## 3. Request/Response Contracts

### 3.1 Resume Upload
**Request:** `multipart/form-data`
- `file`: Resume file (PDF/DOCX)

**Response (202 Accepted):**
```json
{
  "job_id": "job_550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Resume upload successful. Parsing started.",
  "check_status_url": "/api/v1/jobs/job_550e8400-e29b-41d4-a716-446655440000"
}
```

### 3.2 Scoring Engine
**Request:** `POST /api/v1/score`
```json
{
  "resume_data": { ... structured resume json ... },
  "jd_data": { ... structured jd json ... },
  "weights": {
    "skills": 0.5,
    "experience": 0.3,
    "education": 0.2
  }
}
```

**Response (200 OK):**
```json
{
  "match_score": 85.5,
  "breakdown": {
    "skill_match": 90,
    "experience_relevance": 80,
    "education_alignment": 85
  },
  "missing_critical_skills": ["Kubernetes", "GraphQL"],
  "recommendation": "Highly Recommended"
}
```

---

## 4. Async Job Handling Flow
1. **Submit**: Client sends a request to a long-running endpoint (Upload/Scoring).
2. **Ack**: API validates input, generates a `job_id`, persists it to a state store (e.g., SQLite/Redis), and returns `202 Accepted`.
3. **Process**: A background worker picks up the job and updates the state.
4. **Poll**: Client polls `/api/v1/jobs/{job_id}` periodically.
5. **Complete**: When status is `completed`, the response includes the final payload.

## 5. Error & Logging Standards

### Error Schema
All errors follow a standard structure:
```json
{
  "error": {
    "type": "ValidationException",
    "message": "The uploaded file exceeds the 10MB limit.",
    "code": "FILE_TOO_LARGE",
    "trace_id": "req_abc123"
  }
}
```

### HTTP Status Codes
- `200 OK`: Successful sync operation.
- `202 Accepted`: Async job started.
- `400 Bad Request`: Input validation failed.
- `401 Unauthorized`: Missing or invalid API Key.
- `422 Unprocessable Entity`: Valid JSON but logically invalid data.
- `500 Internal Server Error`: Unhandled backend exception.

## 6. Implementation Steps
1. [ ] Create `api/` directory structure.
2. [ ] Define Pydantic models in `api/schemas.py`.
3. [ ] Implement Core API logic in `api/main.py`.
4. [ ] Integrate `ats_engine` modules into API routes.
5. [ ] Implement `JobTracker` for async status management.
6. [ ] Add `logging` middleware for request/response tracking.
