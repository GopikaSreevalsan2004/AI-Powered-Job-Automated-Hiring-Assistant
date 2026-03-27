# AI Project Setup

## Overview
This repository contains the architecture and implementation for an AI-powered Application Tracking and Screening System.

## Project Structure
- `data/`        - Storage for datasets, raw resumes, and processed information.
- `parsers/`     - Modules for extracting information from documents (e.g., PDF, DOCX parsers).
- `ats_engine/`  - Core engine for managing applications and basic ATS functionalities.
- `screening_ai/`- AI models and scripts for initial candidate profile screening against job descriptions.
- `interview_ai/`- Tools and models for conducting or analyzing AI-driven interviews.
- `scoring/`     - Logic for evaluating and ranking candidates.
- `utils/`       - Reusable utilities (e.g., logging, config loading, text processing helpers).
- `tests/`       - Unit and integration tests to ensure system stability.

## Setting Up
1. Initialize the virtual environment: `python -m venv venv`
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
3. Install dependencies: `pip install -r requirements.txt`

## Coding Standards
- Follow PEP 8 guidelines for Python code.
- Write docstrings for all classes and functions.
- Ensure all logic has corresponding tests in the `tests/` directory.

## Testing
Run tests using `pytest` from the root directory:
```bash
pytest
```
