# ATS Scoring Logic & Explainability

This document details the scoring methodology used by the ATS to evaluate candidates against job descriptions.

## 1. Weighted Scoring Framework

The `MasterScorer` aggregates four primary dimensions into a single final score (0.0 to 1.0).

### Default Weights
| Dimension | Default Weight | Description |
| :--- | :---: | :--- |
| **Skill Match** | 30% (`0.30`) | Alignment of technical and soft skills. |
| **Experience Relevance** | 35% (`0.35`) | Match of career history, tenure, and role seniority. |
| **Education Alignment** | 15% (`0.15`) | Relevance of degrees, institutions, and field of study. |
| **Semantic Similarity** | 20% (`0.20`) | Contextual similarity between resume content and JD. |

> [!NOTE]
> Weights can be customized per-request via the API to prioritize specific hiring criteria (e.g., weighing education more for entry-level roles).

## 2. Dimension Breakdown

### 2.1 Skill Match Calculation
-   **Method**: Ratio of required JD skills found in the candidate's profile.
-   **Logic**: 
    -   If JD required skills are provided: `Matches Found / Total Required`.
    -   If no required skills are in JD: Returns a neutral `0.5` if any skills are listed on the resume.
-   **Source**: `ats_engine/skill_extractor.py` and `ats_engine/master_scorer.py`.

### 2.2 Experience Relevance
-   **Method**: Evaluates structured experience entries.
-   **Logic**: 
    -   Extracts `relevance_score` for each job entry based on role titles and descriptions.
    -   The `final_score` uses the `max()` relevance found across all entries (representing the candidate's "peak" relevance).
-   **Source**: `ats_engine/experience_engine.py`.

### 2.3 Education Alignment
-   **Method**: Scoring based on degree level (PhD > Masters > Bachelors) and field relevance.
-   **Logic**: Uses the `total_academic_score` from the `StructuredAcademicProfile`.
-   **Source**: `ats_engine/education_engine.py`.

### 2.4 Semantic Similarity
-   **Method**: Contextual overlap beyond simple keyword matching.
-   **Logic**: Compares the embedding/vector representation of the Resume text against the JD text.
-   **Source**: `ats_engine/semantic_engine.py`.

## 3. Shortlisting Zones

The `ShortlistingEngine` categorizes candidates based on their `final_score`:

| Zone | Threshold | Action |
| :--- | :--- | :--- |
| **🎯 Shortlisted** | >= 0.60 | Highly recommended for immediate interview. |
| **🔍 Needs Review** | 0.30 - 0.59 | Potential match; requires manual recruiter review. |
| **❌ Auto-Rejected** | < 0.30 | Low alignment; filtered out to save recruiter time. |

## 4. Explainability & Bias Mitigation

### 4.1 AI Explanations
The system generates human-readable justifications for every score:
- **Strengths**: "Excellent technical skill alignment", "Strong professional experience match".
- **Weaknesses**: "Missing core technical skills", "Minimal relevant work history".

### 4.2 Fairness Module
The `utils/fairness_module.py` runs post-scoring checks to ensure:
-   **Anonymization**: Option to redact PII (Name, Age, Gender) before scoring.
-   **Impact Analysis**: Validating that scoring distributions don't unfairly penalize specific educational backgrounds or non-traditional career paths.

## 5. Improving Scores
Candidates or recruiters can improve match scores by:
1.  **Refining JD**: Ensuring "Required Skills" are clearly listed for the `Skill Match` engine.
2.  **Structuring Resumes**: Using clear headings (Experience, Education, Skills) to help the `ResumeClassifier` segment data correctly.
