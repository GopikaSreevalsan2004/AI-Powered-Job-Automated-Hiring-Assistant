# Bias Reduction & Fairness Documentation

This document outlines the strategies implemented in the ATS Scoring Engine to improve fairness, reduce subconscious bias, and standardize resume evaluation.

## 1. Anonymization (PII Masking)
To prevent affinity bias and demographic stereotyping, the engine supports a "Blind Review" mode:
- **Candidate IDs**: Names are replaced with hashed IDs (e.g., `CANDIDATE-A1B2C3D4`).
- **PII Scrubbing**: Contact details (emails, phone numbers) are masked using regex patterns.
- **Attribute Neutrality**: Recruiters see skills and experience without being influenced by non-essential personal attributes.

## 2. Reducing Keyword Over-dependence
Traditional ATS systems rely on exact keyword matches, which penalizes candidates who use synonyms or different phrasing.
- **Semantic Similarity**: We use TF-IDF with N-grams and Cosine Similarity to capture the *meaning* of experiences rather than just exact words.
- **Lemmatization**: Stems words (e.g., "managing" to "manage") to ensure credit is given for the underlying skill regardless of tense.

## 3. Scoring Normalization
To prevent "Hard Grading" bias (where a difficult JD results in no candidates qualifying):
- **Pool-Relative Normalization**: Scores are normalized relative to the current applicant pool.
- **Multi-Dimensional Weighting**: Final scores are a weighted average of Skills (40%), Experience (30%), Education (10%), and Semantic Fit (20%), preventing a single missing attribute from unfairly disqualifying a candidate.

## 4. Bias Indicators
The engine scans for non-inclusive language:
- **Gendered Terms**: Flags terms like "Chairman" or "Waitress" and recommends gender-neutral alternatives.
- **Age Indicators**: Flags specific age-related keywords to encourage age-agnostic evaluation.

## 5. Standardization
Every resume is converted into the same structured JSON format (Skill, Experience, Education) before evaluation, ensuring that candidates are judged on content rather than formatting or visual design.
