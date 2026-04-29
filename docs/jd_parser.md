# Job Description Parser Module

The Job Description (JD) Parser module is an intelligent text-processing pipeline designed to extract structured features from raw job descriptions. 
It helps convert free-form text from employer job postings into a robust `JobRequirementProfile`, which is inherently AI-readable for downstream ATS matching, scoring, and analytics tasks.

## Key Features

1. **Text Normalization**: Cleans inconsistent white-space and special characters (like bullets) using the standard `TextCleaner`.
2. **Synonym Detection Framework**: Normalizes specific software stack terms (e.g., mapping `ML` to `Machine Learning` or `SWE` to `Software Engineer`) to ensure apples-to-apples comparisons between resumes and JDs.
3. **Structured Extraction**: Extracts Years of Experience Requirements via Heuristics, distinguishes between exact `education` mentions and generic `skills_required`.
4. **Strong Typing via Models**: Uses Python dataclasses (`models/job_models.py`) to enforce shape and types before serialization to JSON schemas.

## Usage File locations

- **Models**: `models/job_models.py`
- **Parser Core**: `parsers/jd_parser.py`
- **Mapper Utility**: `utils/synonym_mapper.py`

## Quick Start Example

You can easily ingest any text-based JD using the parser:

```python
from parsers.jd_parser import JDParser
import json

raw_jd_text = \"\"\"
2. Senior Machine Learning Engineer
Job Summary
We need a seasoned engineer to build models.
Required Skills
• Python
• ML
• Deep Learning
Qualifications
• 5-7 years experience
• Master's degree preferred
\"\"\"

parser = JDParser()
profile = parser.parse(raw_jd_text, filename="02_Senior_ML_Engineer.txt")

print(json.dumps(profile.to_dict(), indent=2))
```

## Adding New Synonyms
If the AI-matching accuracy drops for certain specialized roles, you can quickly add new rules to `utils/synonym_mapper.py` directly under the `SKILL_SYNONYMS` or `ROLE_SYNONYMS` dictionaries.
This allows simple mapping rules to handle vast amounts of variability without retraining a model.
