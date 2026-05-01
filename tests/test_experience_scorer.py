import pytest
from datetime import datetime
from scoring.experience_scorer import ExperienceScorer

@pytest.fixture
def scorer():
    return ExperienceScorer()

def test_extract_seniority(scorer):
    assert scorer._extract_seniority("Senior Software Engineer") == 3
    assert scorer._extract_seniority("Junior Developer") == 1
    assert scorer._extract_seniority("Principal Data Scientist") == 5
    assert scorer._extract_seniority("Software Engineer") == 2 # Default

def test_clean_title(scorer):
    assert scorer._clean_title("Senior Software Engineer") == "software engineer"
    assert scorer._clean_title("Junior Developer") == "developer"
    assert scorer._clean_title("VP of Engineering") == "of engineering"
    assert scorer._clean_title("Software Engineer") == "software engineer"

def test_calculate_role_similarity(scorer):
    # Same base title, same seniority
    assert scorer.calculate_role_similarity("Software Engineer", "Software Engineer") == 1.0
    
    # Same base title, different seniority
    # Senior (3) vs Default (2) -> diff 1 * 0.05 = 0.05 penalty
    sim = scorer.calculate_role_similarity("Senior Software Engineer", "Software Engineer")
    assert sim == 0.95
    
    # Large seniority difference
    # VP (8) vs Intern (0) -> diff 8 * 0.05 = 0.4, but capped at 0.2 penalty
    sim = scorer.calculate_role_similarity("VP of Engineering", "Engineering Intern")
    assert sim <= 0.8
    
    # Different order
    assert scorer.calculate_role_similarity("Engineer Software", "Software Engineer") == 1.0

def test_score_relevance(scorer):
    experience = {
        "role": "Senior Software Engineer",
        "description": "Developed backend systems in Python, Javascript, and Go. Used AWS.",
        "start_dt": datetime(2018, 1, 1),
        "end_dt": datetime(2021, 1, 1) # 36 months
    }
    
    job_requirements = {
        "target_role": "Software Engineer",
        "required_skills": ["Python", "AWS", "Ruby", "Java"], # "Java" shouldn't match "Javascript"
        "required_experience_months": 24
    }
    
    result = scorer.score_relevance(experience, job_requirements)
    
    assert result['title_score'] == 0.95
    
    # Skill score: Python (yes), AWS (yes), Ruby (no), Java (no, due to word boundaries in Javascript)
    # 2 out of 4 -> 0.5
    assert result['skill_score'] == 0.5
    assert "Python" in result['matched_skills']
    assert "AWS" in result['matched_skills']
    assert "Java" not in result['matched_skills']
    
    # Duration score: 36 months / 24 required -> 1.5, capped at 1.0
    assert result['duration_score'] == 1.0
    
    # Total score checks out based on weights
    # 0.45 * 0.95 + 0.40 * 0.5 + 0.15 * 1.0 = 0.4275 + 0.2 + 0.15 = 0.7775
    assert result['total_score'] == 0.78
