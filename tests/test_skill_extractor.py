import pytest
import os
import json
from ats_engine.skill_extractor import SkillExtractionEngine

@pytest.fixture
def test_dictionary_path(tmp_path):
    dict_content = {
        "Tech": {
            "Programming Languages": ["Python", "Java"],
            "Frameworks & Libraries": ["React", "Spring Boot"]
        },
        "Synonyms": {
            "PY": "Python",
            "ReactJS": "React"
        },
        "Stacks": {
            "MERN": ["MongoDB", "Express", "React", "Node.js"]
        }
    }
    path = tmp_path / "skill_dictionary.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dict_content, f)
    return str(path)

@pytest.fixture
def extractor(test_dictionary_path):
    return SkillExtractionEngine(dictionary_path=test_dictionary_path)

def test_extract_exact_match(extractor):
    text = "I have 5 years of experience in Python and Java."
    skills = extractor.extract_skills(text)
    names = [s["name"] for s in skills]
    assert "Python" in names
    assert "Java" in names

def test_extract_synonym(extractor):
    text = "Extensive knowledge of PY and ReactJS."
    skills = extractor.extract_skills(text)
    names = [s["name"] for s in skills]
    assert "Python" in names
    assert "React" in names

def test_extract_stack(extractor):
    text = "Fullstack developer using MERN stack."
    skills = extractor.extract_skills(text)
    names = [s["name"] for s in skills]
    # MERN stack expansion adds React (which is known in the test dict)
    assert "React" in names

def test_confidence_scoring(extractor):
    text = "Python Python Python Java"
    skills = extractor.extract_skills(text)
    
    python_skill = next((s for s in skills if s["name"] == "Python"), None)
    java_skill = next((s for s in skills if s["name"] == "Java"), None)
    
    assert python_skill is not None
    assert java_skill is not None
    # Python is mentioned multiple times, it should have higher confidence
    assert python_skill["confidence_score"] > java_skill["confidence_score"]

def test_fuzzy_matching(extractor):
    text = "Expirience with Pyton."
    skills = extractor.extract_skills(text)
    names = [s["name"] for s in skills]
    # Pyton should map to Python
    assert "Python" in names
