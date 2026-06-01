# ATS Developer Guide

Welcome to the ATS Development Guide! This document provides everything you need to know to set up, maintain, and extend the system.

## 1. Getting Started

### Prerequisites
- Python 3.9+
- Virtual Environment (recommended)

### Environment Setup
1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd Zecpath
    ```
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 2. Project Structure

-   `/api`: FastAPI routes, schemas, and job tracking logic.
-   `/ats_engine`: Core intelligence engines (MasterScorer, ShortlistingEngine).
-   `/parsers`: File extraction parsers for resumes and JDs.
-   `/models`: Pydantic and Dataclass models for data consistency.
-   `/utils`: Shared logic (Text cleaning, synonym mapping, fairness).
-   `/tests`: Unit and integration tests.

## 3. Extending the System

### Adding a New Scoring Dimension
To add a new scoring metric (e.g., "Culture Fit" or "Language Proficiency"):
1.  Create a new engine in `ats_engine/` (e.g., `culture_engine.py`).
2.  Implement a `calculate_score` method returning a float between 0 and 1.
3.  Update `ats_engine/master_scorer.py`:
    -   Add the new dimension to `DEFAULT_WEIGHTS`.
    -   Integrate the call in `calculate_candidate_score`.
    -   Add an explanation logic in `generate_explanation_text`.

### Adding Support for New File Formats
1.  Create a new parser in `parsers/` (e.g., `txt_parser.py`).
2.  Implement the text extraction logic.
3.  Update the file ingestion logic in the API to handle the extension.

## 4. Troubleshooting
For common issues, missing data errors, and API integration problems, please refer to the [Troubleshooting Guide](TROUBLESHOOTING.md).

## 5. Running Tests
We use `pytest` for testing.
```bash
pytest tests/
```
To run specific tests:
```bash
pytest tests/test_scoring.py
```

## 6. Contribution Guidelines
1.  Create a feature branch.
2.  Ensure all Pydantic models are updated if you change data structures.
3.  Add unit tests for new logic.
4.  Update documentation in `/docs` if scoring weights or API contracts change.
