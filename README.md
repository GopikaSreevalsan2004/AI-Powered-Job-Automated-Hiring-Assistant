# AI Project Setup

## Overview
This repository contains the architecture and implementation for an AI-powered Application Tracking and Screening System.

## 📚 Documentation
For detailed technical information, architecture diagrams, and developer guides, please refer to:

-   [Architecture Overview](docs/ARCHITECTURE.md) - System design and component diagrams.
-   [Scoring Logic & Explainability](docs/SCORING_LOGIC.md) - Detailed breakdown of how candidates are evaluated.
-   [Developer Guide](docs/DEVELOPER_GUIDE.md) - Setup, contributing, and troubleshooting.
-   [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Common issues and resolutions.
-   [API Specification](docs/ats_api_spec.md) - REST API endpoints and data contracts.

## Project Structure
- `api/`         - FastAPI REST API implementation.
- `parsers/`     - Modules for extracting information from documents (e.g., PDF, DOCX parsers).
- `ats_engine/`  - Core engine for managing applications and basic ATS functionalities.
- `screening_ai/`- AI models and scripts for initial candidate profile screening.
- `models/`      - Pydantic and data models for profiles and JDs.
- `utils/`       - Reusable utilities (e.g., logging, config loading, fairness module).
- `tests/`       - Unit and integration tests.

## Setting Up
Refer to the [Developer Guide](docs/DEVELOPER_GUIDE.md) for detailed setup instructions.

## Coding Standards
- Follow PEP 8 guidelines for Python code.
- Write docstrings for all classes and functions.
- Ensure all logic has corresponding tests in the `tests/` directory.

## Testing
Run tests using `pytest` from the root directory:
```bash
pytest
```
