# Semantic Matching Accuracy Report

This report evaluates the performance of the Deep Semantic Matching Engine.

## Method
- **Vectorization:** TF-IDF with Unigrams and Bigrams.
- **Similarity Measure:** Cosine Similarity.
- **Dimensions:** Skills Overlap (45%) and Experience Context (55%).

## Top Matches per Job Description
### Job: Big Data Engineer
| Resume | Total Score | Match Level | Skill Sim | Exp Sim |
|--------|-------------|-------------|-----------|---------|
| Resume_1_Arjun_Mehta.pdf | 0.1006 | Low Match | 0.1058 | 0.0964 |
| Resume_4_Elena_Rodriguez.pdf | 0.0571 | Low Match | 0.0633 | 0.0520 |
| Resume_3_Li_Wei.pdf | 0.0550 | Low Match | 0.1065 | 0.0129 |

### Job: Senior Big Data Engineer
| Resume | Total Score | Match Level | Skill Sim | Exp Sim |
|--------|-------------|-------------|-----------|---------|
| Resume_2_Sarah_Jenkins.pdf | 0.0714 | Low Match | 0.0233 | 0.1109 |
| Resume_8_Julian_Vane.pdf | 0.0225 | Low Match | 0.0000 | 0.0410 |
| Resume_10_Dr._Helena_Vance.pdf | 0.0195 | Low Match | 0.0000 | 0.0355 |

### Job: Lead Big Data Engineer
| Resume | Total Score | Match Level | Skill Sim | Exp Sim |
|--------|-------------|-------------|-----------|---------|
| Resume_8_Julian_Vane.pdf | 0.0502 | Low Match | 0.0402 | 0.0583 |
| Resume_2_Sarah_Jenkins.pdf | 0.0399 | Low Match | 0.0461 | 0.0347 |
| Resume_10_Dr._Helena_Vance.pdf | 0.0332 | Low Match | 0.0000 | 0.0604 |

### Job: Principal Big Data Engineer
| Resume | Total Score | Match Level | Skill Sim | Exp Sim |
|--------|-------------|-------------|-----------|---------|
| Resume_2_Sarah_Jenkins.pdf | 0.0439 | Low Match | 0.0395 | 0.0476 |
| Resume1.pdf | 0.0094 | Low Match | 0.0020 | 0.0154 |
| Resume_1_Arjun_Mehta.pdf | 0.0058 | Low Match | 0.0000 | 0.0106 |

### Job: Junior Big Data Engineer
| Resume | Total Score | Match Level | Skill Sim | Exp Sim |
|--------|-------------|-------------|-----------|---------|
| Resume_1_Arjun_Mehta.pdf | 0.0350 | Low Match | 0.0516 | 0.0215 |
| Resume_5_David_Chen.pdf | 0.0263 | Low Match | 0.0403 | 0.0150 |
| Resume_2_Sarah_Jenkins.pdf | 0.0260 | Low Match | 0.0048 | 0.0434 |

## Scoring Distribution
- **Mean Score:** 0.0163
- **Max Score:** 0.1006
- **Min Score:** 0.0000

## Tuning & Threshold Validation
- **Excellent Match (> 0.6):** High semantic alignment across both skills and experience.
- **Good Match (0.4 - 0.6):** Strong skills or experience alignment.
- **Potential Match (0.2 - 0.4):** Some keyword overlap but weak contextual alignment.
