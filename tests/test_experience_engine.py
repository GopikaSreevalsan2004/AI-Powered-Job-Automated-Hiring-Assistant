import pytest
from ats_engine.experience_engine import ExperienceEngine

def test_experience_pipeline():
    engine = ExperienceEngine()
    sample_text = """
    Software Engineer | Google
    Jan 2020 - Present
    Developed scalable microservices using Python and Go.
    
    Junior Developer | Startup Inc.
    Jun 2018 - Dec 2019
    Built frontend features with React.
    """
    
    requirements = {
        "target_role": "Software Engineer",
        "required_skills": ["Python", "React"]
    }
    
    result = engine.process_experience_text(sample_text, requirements)
    
    assert len(result['structured_experiences']) == 2
    assert result['analysis']['total_experience_months'] > 0
    assert result['structured_experiences'][0]['role'] == "Software Engineer"
    assert result['structured_experiences'][0]['relevance_score'] > 0.5

def test_gaps_detection():
    engine = ExperienceEngine()
    sample_text = """
    Role A | Company A
    Jan 2020 - Dec 2020
    
    Role B | Company B
    Jun 2021 - Dec 2021
    """
    
    result = engine.process_experience_text(sample_text)
    gaps = result['analysis']['gaps']
    
    assert len(gaps) == 1
    assert gaps[0]['duration_months'] >= 5

def test_overlap_detection():
    engine = ExperienceEngine()
    sample_text = """
    Role A | Company A
    Jan 2020 - Dec 2020
    
    Role B | Company B
    Oct 2020 - Mar 2021
    """
    
    result = engine.process_experience_text(sample_text)
    overlaps = result['analysis']['overlaps']
    
    assert len(overlaps) == 1
    assert overlaps[0]['overlap_months'] >= 2
