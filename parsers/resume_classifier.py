import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ResumeSectionClassifier:
    """
    Classifies raw text lines from a resume into standard sections:
    Personal Info, Summary, Experience, Education, Skills, Projects, Certifications.
    """

    SECTIONS = [
        "Personal Info", 
        "Summary", 
        "Experience", 
        "Education", 
        "Skills", 
        "Projects", 
        "Certifications",
        "Unknown"
    ]

    # Rule-based dictionary mapping normalized headings to exact categories
    RULE_BASED_MAPPING = {
        "Personal Info": [
            "contact", "contact info", "contact information", "personal details", 
            "personal data"
        ],
        "Summary": [
            "summary", "professional summary", "executive summary", "profile", 
            "about me", "objective", "career objective"
        ],
        "Experience": [
            "experience", "work experience", "professional experience", 
            "employment history", "work history", "career history"
        ],
        "Education": [
            "education", "academic background", "academic qualifications", 
            "educational background", "degrees"
        ],
        "Skills": [
            "skills", "technical skills", "core competencies", "technologies", 
            "areas of expertise", "it skills"
        ],
        "Projects": [
            "projects", "personal projects", "academic projects", 
            "key projects", "portfolio"
        ],
        "Certifications": [
            "certifications", "certificates", "licenses", 
            "certifications & training"
        ]
    }

    # NLP Training corpus representing the thematic nature of a section.
    # Used when a standalone header doesn't exactly match rules above, but
    # acts as an ambiguous transition.
    NLP_CORPUS = {
        "Summary": [
            "driven professional with years of experience", 
            "track record of success in leading teams",
            "highly motivated software engineer passionate about algorithms",
            "results oriented manager proven ability"
        ],
        "Experience": [
            "worked as a lead engineer managing deployment",
            "developed implemented optimized solutions",
            "managed a team of five improved latency metrics",
            "years of experience in development marketing sales"
        ],
        "Education": [
            "bachelor of science master degree phd university college",
            "graduated coursework gpa thesis dissertation",
            "studied computer science business administration"
        ],
        "Skills": [
            "python java c++ sql kubernetes aws fluent in spanish",
            "machine learning data analysis project management agile",
            "proficiency expert intermediate basic familiar tools"
        ],
        "Projects": [
            "built a full stack web application clone github",
            "designed mockups for a new application",
            "implemented a neural network for image classification dataset"
        ],
        "Certifications": [
            "certified aws solutions architect obtained credential",
            "cisco ccna scrum master pmp certification",
            "coursera edx udemy google certificate"
        ]
    }

    def __init__(self):
        # Build inverse mapping for rules
        self.exact_headers = {}
        for category, keywords in self.RULE_BASED_MAPPING.items():
            for kw in keywords:
                self.exact_headers[kw] = category
                
        # Initialize NLP Vectorizer and fit on corpus
        # Create a document for each category joining its corpus strings
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        
        self.categories_nlp = ["Summary", "Experience", "Education", "Skills", "Projects", "Certifications"]
        corpus_docs = []
        for cat in self.categories_nlp:
            combined_text = " ".join(self.NLP_CORPUS[cat])
            corpus_docs.append(combined_text)
            
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_docs)

    def is_likely_header(self, line: str) -> bool:
        """Heuristics to determine if a line acts as a section header."""
        cleaned = line.strip()
        # A header is usually short (e.g. less than 50 chars)
        if not cleaned or len(cleaned) > 50:
            return False
            
        words = cleaned.split()
        
        if len(words) > 5:
            return False
            
        # Often title cased or entirely upper cased
        if cleaned.istitle() or cleaned.isupper():
            return True
            
        # Often ends with colon
        if cleaned.endswith(':'):
            return True
            
        # If it's 1-3 words, high chance of being a header if it doesn't end with sentence punctuation
        if len(words) <= 3 and not cleaned[-1] in {'.', ',', ';'}:
            return True
            
        return False

    def get_rule_based_section(self, line: str) -> str:
        """Returns the section name if line matches our exact dictionary."""
        normalized = re.sub(r'[^a-zA-Z\s]', '', line).strip().lower()
        if normalized in self.exact_headers:
            return self.exact_headers[normalized]
        return ""

    def get_nlp_based_section(self, line: str, threshold: float = 0.15) -> str:
        """Uses Cosine Similarity of TF-IDF to guess section if rule fails."""
        vec = self.vectorizer.transform([line])
        similarities = cosine_similarity(vec, self.tfidf_matrix).flatten()
        best_idx = similarities.argmax()
        
        if similarities[best_idx] >= threshold:
            return self.categories_nlp[best_idx]
        return ""

    def classify_lines(self, text: str) -> List[Dict[str, str]]:
        """
        Takes raw multi-line resume text.
        Classifies each block, returning a list of dicts:
        [{"label": "Summary", "text": "I am a ..."}, ...]
        """
        lines = text.split('\n')
        
        # We start by assuming the top of the resume is Personal Info
        current_section = "Personal Info"
        section_blocks = []
        current_block_lines = []
        
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
                
            # If line is likely a header, we check it
            if self.is_likely_header(trimmed):
                # 1. Rule Based Match
                new_section = self.get_rule_based_section(trimmed)
                
                # 2. NLP Based Match (if rule based failed)
                if not new_section:
                    # Perhaps they wrote "My Awesome Projects"
                    nlp_section = self.get_nlp_based_section(trimmed, threshold=0.2)
                    if nlp_section:
                        new_section = nlp_section
                
                # If we detected a state change
                if new_section and new_section != current_section:
                    # Save the accumulated block
                    if current_block_lines:
                        section_blocks.append({
                            "label": current_section,
                            "text": "\n".join(current_block_lines)
                        })
                        current_block_lines = []
                    current_section = new_section
                    # Skip adding the header text itself to the content block 
                    # (or we could add it, but usually standard parsers strip it)
                    continue

            # Check if heavy signal words alter the state despite no clear header
            # E.g., we suddenly see deep text about "years of experience". We only want to do
            # this if the block size is substantial or we are currently in "Unknown" state
            if len(trimmed.split()) > 10 and current_section == "Personal Info":
                # We transitioned out of Personal Info header without an explicit Summary/Experience header
                nlp_section = self.get_nlp_based_section(trimmed, threshold=0.25)
                if nlp_section:
                    if current_block_lines:
                        section_blocks.append({
                            "label": current_section,
                            "text": "\n".join(current_block_lines)
                        })
                        current_block_lines = []
                    current_section = nlp_section
                    
            current_block_lines.append(trimmed)

        # Append trailing block
        if current_block_lines:
             section_blocks.append({
                 "label": current_section,
                 "text": "\n".join(current_block_lines)
             })
             
        # Optional: post-processing to merge continuous blocks of the same label
        merged_blocks = []
        for block in section_blocks:
            if not merged_blocks:
                merged_blocks.append(block)
            else:
                if merged_blocks[-1]["label"] == block["label"]:
                    merged_blocks[-1]["text"] += "\n" + block["text"]
                else:
                    merged_blocks.append(block)
                    
        return merged_blocks
