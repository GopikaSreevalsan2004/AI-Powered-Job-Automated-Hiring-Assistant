# ATS Validation & Accuracy Report

## Executive Summary
- **Global Skill Extraction Precision:** 31.4%
- **Global Skill Extraction Recall:** 40.5%
- **Global F1 Score:** 33.3%
- **Decision Alignment Accuracy:** 40.0%

## Reliability per Role Category
| Category | Profile | Resume | Skill Recall | Status Match | Score Validity |
|----------|---------|--------|--------------|--------------|----------------|
| Tech | Senior | Resume_1_Arjun_Mehta.pdf | 85.7% | ❌ | ⚠️ |
| Non-Tech | Senior | Resume_6_Marcus_Thorne.pdf | 33.3% | ✅ | ✅ |
| Tech | Fresher | Resume1.pdf | 50.0% | ❌ | ⚠️ |
| Non-Tech | Senior | Resume_9_Sofia_Rossi.pdf | 0.0% | ✅ | ✅ |
| Tech | Senior | Resume_4_Elena_Rodriguez.pdf | 33.3% | ❌ | ⚠️ |

## Mismatch Cases & Improvement Backlog
| Resume | AI Status | Manual | AI Score | Expected Range | Issue |
|--------|-----------|--------|----------|----------------|-------|
| Resume_1_Arjun_Mehta.pdf | Rejected | Shortlisted | 0.40 | [0.7, 1.0] | Status Mismatch |
| Resume1.pdf | Rejected | Shortlisted | 0.28 | [0.4, 0.7] | Status Mismatch |
| Resume_4_Elena_Rodriguez.pdf | Rejected | Shortlisted | 0.22 | [0.6, 0.9] | Status Mismatch |

## Improvement Backlog
1. **[Parsing]** **CRITICAL**: Improve date extraction in `experience_engine.py`. Resumes without explicit dates (e.g., Arjun Mehta) are getting 0 years experience, causing false rejections.
2. **[Tech]** Improve skill extraction for compound tech terms.
3. **[Non-Tech]** Expand skill dictionary for soft skills (recognized in Marcus Thorne's profile).
4. **[Weights]** Re-evaluate default scoring weights; skill match is high but total score is low due to experience gaps.
5. **[Seniority]** Implement management context detection to better score 'Lead' vs 'Senior' roles.
