import json
import logging
from typing import List, Dict, Tuple
import re

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

try:
    from fuzzywuzzy import fuzz
    HAS_FUZZY = True
except ImportError:
    HAS_FUZZY = False

from utils.synonym_mapper import SynonymMapper


class SkillExtractionEngine:
    """
    NLP-based extraction engine to identify, normalize, and score skills from text.
    Handles exact matches, synonyms, spelling variations, and skill stack expansions.
    """

    def __init__(self, dictionary_path: str = "data/skill_dictionary.json", logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        
        self.nlp = None
        if HAS_SPACY:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning("Spacy model 'en_core_web_sm' not found. Falling back to regex extraction.")
        else:
            self.logger.warning("spacy not installed. Falling back to regex extraction.")
            
        self._load_dictionary(dictionary_path)
        self.synonym_mapper = SynonymMapper(dictionary_path)

    def _load_dictionary(self, path: str):
        self.known_skills = {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.dictionary = json.load(f)
            
            # Flatten taxonomy for quick lookup
            for major_category, sub_categories in self.dictionary.items():
                if major_category in ["Synonyms", "Stacks"]:
                    continue
                for sub_category, skills in sub_categories.items():
                    # Map to the specific schema category: Technical, Soft, Tool, Domain Knowledge
                    schema_category = "Domain Knowledge"
                    if major_category == "Tech":
                        schema_category = "Technical"
                    elif major_category == "Business":
                        if sub_category == "Soft Skills":
                            schema_category = "Soft"
                        else:
                            schema_category = "Domain Knowledge"
                    elif major_category == "Creative":
                        if sub_category == "Design":
                            schema_category = "Tool"
                        else:
                            schema_category = "Technical"
                            
                    for skill in skills:
                        self.known_skills[skill.lower()] = {
                            "name": skill,
                            "category": schema_category
                        }
        except Exception as e:
            self.logger.error(f"Failed to load skill dictionary from {path}: {e}")
            self.dictionary = {}

    def extract_skills(self, text: str) -> List[Dict]:
        """
        Main entry point for extracting and scoring skills from text.
        """
        if not text:
            return []
            
        raw_skills = self._extract_raw_entities(text)
        expanded_skills = self._expand_stacks(raw_skills)
        normalized_skills = self._normalize_skills(expanded_skills)
        scored_skills = self._score_and_deduplicate(normalized_skills, text)
        
        return scored_skills

    def _extract_raw_entities(self, text: str) -> List[str]:
        raw_skills = []
        
        # 1. Spacy Named Entity Recognition
        if self.nlp:
            self.nlp.max_length = 500000 
            doc = self.nlp(text)
            # ORG, PRODUCT and WORK_OF_ART often contain tech stacks/tools
            for ent in doc.ents:
                if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART", "PERSON"]:
                    raw_skills.append(ent.text)
            
            # Extract noun chunks for potential compound skills (e.g. Machine Learning)
            for chunk in doc.noun_chunks:
                # Filter out chunks that are too long or just start with articles
                text_chunk = chunk.text.strip()
                if 1 < len(text_chunk.split()) <= 4:
                    raw_skills.append(text_chunk)
                
        # 2. Pattern-based extraction (e.g. "Expertise in X", "Experience with Y")
        patterns = [
            r'(?:expertise|proficiency|knowledge|experience|using|with|in)\s+([^,.;\n(]+)',
            r'([^,.;\n(]+)\s+(?:expertise|proficiency|knowledge|experience|skill|skills)'
        ]
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                phrase = match.group(1).strip()
                if phrase:
                    # Further split if there are bullets or special chars
                    sub_parts = re.split(r'[,•|;]|\band\b', phrase)
                    raw_skills.extend([p.strip() for p in sub_parts if p.strip()])
            
        # 3. Simple split by commas, newlines, bullets to find distinct phrases
        tokens = re.split(r'[,•\n|;]|\band\b', text)
        raw_skills.extend([t.strip() for t in tokens if t.strip()])
        
        # 4. Add individual words to catch single-word skills (like Python, Java)
        # Using a regex that allows for symbols common in tech (C++, .NET, C#)
        words = re.findall(r'\b[A-Za-z0-9+#.]+\b', text)
        raw_skills.extend(words)

        # Filter out obvious non-skills and structural items
        stop_words = {
            "and", "the", "with", "used", "working", "experience", "skills", 
            "knowledge", "fluent", "proficient", "basic", "intermediate", "expert",
            "years", "months", "demonstrated", "strong", "excellent", "good",
            "highly", "results", "proven", "track", "record", "ability", "to"
        }
        
        valid_raw = []
        for s in raw_skills:
            # Clean up punctuation at start/end
            clean_s = re.sub(r'^[^\w+#.]+|[^\w+#.]+$', '', s).strip()
            
            # Filter by length and content
            if 1 < len(clean_s) < 50 and clean_s.lower() not in stop_words:
                # Check for junk like numbers
                if not re.match(r'^\d+$', clean_s):
                    valid_raw.append(clean_s)
                
        return valid_raw

    def _expand_stacks(self, skills: List[str]) -> List[str]:
        expanded = []
        stacks = self.dictionary.get("Stacks", {})
        
        for skill in skills:
            upper_skill = skill.upper()
            if upper_skill in stacks:
                expanded.extend(stacks[upper_skill])
                expanded.append(skill) # keep the stack name as well
            else:
                expanded.append(skill)
        return expanded

    def _normalize_skills(self, skills: List[str]) -> List[Tuple[str, str, float]]:
        """
        Normalizes skills, resolves synonyms, corrects spelling via fuzzy matching (if possible).
        Returns tuples of (original, normalized, confidence).
        We only keep skills that map to known taxonomy with high confidence, 
        plus a few exact high-confidence unknown nouns.
        """
        normalized = []
        
        for skill in set(skills): # Deduplicate first for performance
            # 1. Check exact synonym match
            norm = self.synonym_mapper.normalize_skill(skill)
            if norm.lower() != skill.lower() and norm.lower() in self.known_skills:
                # Was mapped via synonym, very confident
                normalized.append((skill, self.known_skills[norm.lower()]["name"], 0.90))
                continue
                
            # 2. Check exact match in known skills
            if norm.lower() in self.known_skills:
                normalized.append((skill, self.known_skills[norm.lower()]["name"], 0.90))
                continue
                
            # 3. Fuzzy match spelling variations against known skills
            if HAS_FUZZY:
                best_match = None
                highest_score = 0
                for known_lower, known_data in self.known_skills.items():
                    # Quick length check to avoid comparing very different strings
                    if abs(len(norm) - len(known_lower)) > 4:
                        continue
                        
                    score = fuzz.ratio(norm.lower(), known_lower)
                    if score > highest_score:
                        highest_score = score
                        best_match = known_data["name"]
                        if highest_score == 100:
                            break
                
                # Threshold for fuzzy match
                if highest_score >= 85:
                    confidence = highest_score / 100.0
                    normalized.append((skill, best_match, confidence))
                    continue
                    
        return normalized

    def _score_and_deduplicate(self, normalized_skills: List[Tuple[str, str, float]], text: str) -> List[Dict]:
        """
        Groups by normalized skill, picks max confidence, determines category,
        and adds contextual boosting and level detection.
        """
        deduped = {}
        text_lower = text.lower()
        
        # Keywords for proficiency detection
        level_patterns = {
            "Expert": [r"expert", r"advanced", r"senior", r"lead", r"architect", r"guru", r"master"],
            "Intermediate": [r"intermediate", r"proficient", r"solid", r"good", r"experienced"],
            "Beginner": [r"basic", r"beginner", r"introductory", r"exposure", r"junior", r"familiar"]
        }
        
        for original, norm, base_conf in normalized_skills:
            # 1. Frequency calculation for boosting
            # Escaping for regex safety
            pattern = r'\b' + re.escape(original.lower()) + r'\b'
            mentions = re.findall(pattern, text_lower)
            count = len(mentions)
            
            # Contextual signal: if the skill is mentioned multiple times, boost confidence
            # Mentions boost: 1 mention = +0, 2 = +0.05, 3+ = +0.10
            context_boost = 0.0
            if count > 2:
                context_boost = 0.10
            elif count > 1:
                context_boost = 0.05
                
            final_conf = min(1.0, base_conf + context_boost)
            
            # 2. Level Detection (Contextual)
            # Look at a window of text around the first mention of the original term
            found_level = "Intermediate" # Default
            match_idx = text_lower.find(original.lower())
            if match_idx != -1:
                # Look 50 chars before and after
                window = text_lower[max(0, match_idx-50) : min(len(text_lower), match_idx+50)]
                for level, keywords in level_patterns.items():
                    for kw in keywords:
                        if re.search(r'\b' + kw + r'\b', window):
                            found_level = level
                            break
                    if found_level != "Intermediate":
                        break

            # 3. Aggregation and Category assignment
            if norm not in deduped or final_conf > deduped[norm]["confidence_score"]:
                category = "Technical" # Default
                for k, v in self.known_skills.items():
                    if v["name"].lower() == norm.lower():
                        category = v["category"]
                        break
                        
                deduped[norm] = {
                    "name": norm,
                    "confidence_score": round(final_conf, 2),
                    "category": category,
                    "level": found_level,
                    "mentions": count
                }
            else:
                # Update level if a more "specific" level is found with this mention
                # (Simple logic: take the first one found or highest confidence one)
                pass
                
        return sorted(list(deduped.values()), key=lambda x: x["confidence_score"], reverse=True)
