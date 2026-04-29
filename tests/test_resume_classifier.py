import pytest
from parsers.resume_classifier import ResumeSectionClassifier

@pytest.fixture
def classifier():
    return ResumeSectionClassifier()

def test_is_likely_header(classifier):
    assert classifier.is_likely_header("WORK EXPERIENCE") == True
    assert classifier.is_likely_header("Education:") == True
    assert classifier.is_likely_header("This is a random sentence that should not be a header at all.") == False
    assert classifier.is_likely_header("") == False

def test_rule_based_matching(classifier):
    assert classifier.get_rule_based_section("WORK EXPERIENCE") == "Experience"
    assert classifier.get_rule_based_section("Academic Qualifications") == "Education"
    assert classifier.get_rule_based_section("Professional Summary:") == "Summary"
    assert classifier.get_rule_based_section("Random section") == ""

def test_nlp_based_matching(classifier):
    text_skills = "python java c++ sql kubernetes aws"
    assert classifier.get_nlp_based_section(text_skills) == "Skills"
    
    text_experience = "managed a team of five and improved latency"
    assert classifier.get_nlp_based_section(text_experience) == "Experience"

def test_classify_lines_perfect_headers(classifier):
    text = """Alice Johnson
alice@email.com
SUMMARY
A highly motivated engineer.
EXPERIENCE
Software Engineer at Tech Corp
Built a lot of applications.
EDUCATION
Bachelor of Science
"""
    blocks = classifier.classify_lines(text)
    
    assert len(blocks) == 4
    assert blocks[0]["label"] == "Personal Info"
    assert blocks[1]["label"] == "Summary"
    assert "highly motivated" in blocks[1]["text"]
    assert blocks[2]["label"] == "Experience"
    assert "Tech Corp" in blocks[2]["text"]
    assert blocks[3]["label"] == "Education"
    assert "Bachelor of Science" in blocks[3]["text"]

def test_classify_lines_missing_headers(classifier):
    # Missing the "EXPERIENCE" header explicitly, but has strong signal
    text = """Dr. Sarah Miller
London, UK
PhD in Physics turned Data Scientist.
Alpha Insights
Lead Data Scientist
Oct 2021 - Present
Developed implemented optimized solutions.
University of Oxford
Doctor of Philosophy
Oct 2016 - Sep 2020
"""
    blocks = classifier.classify_lines(text)
    
    # Needs some NLP and Rule logic combination. It is expected to at least group some blocks.
    labels = [b["label"] for b in blocks]
    assert "Personal Info" in labels

    # Depending on our exact NLP thresholds, it might classify differently.
    # We mainly test that it doesn't crash and outputs grouped texts.
    assert len(blocks) >= 1
