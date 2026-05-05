import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Any, Optional

class SemanticEngine:
    """
    Handles deep semantic matching between resumes and job descriptions.
    Uses TF-IDF vectorization with n-grams to capture contextual meaning
    and Cosine Similarity for scoring.
    """
    
    def __init__(self, corpus: Optional[List[str]] = None):
        """
        Initializes the engine. If a corpus is provided, the vectorizer is fitted immediately.
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
            
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2), # Capture bi-grams for semantic context
            max_features=10000,
            min_df=1 # In a small corpus, we don't want to ignore rare but important words
        )
        self.is_fitted = False
        if corpus:
            self.fit(corpus)

    def fit(self, corpus: List[str]):
        """Fits the vectorizer on a broad corpus of resumes and JDs."""
        if not corpus:
            return
        
        # Lemmatize corpus for better fitting
        lemmatized_corpus = [self._preprocess(text) for text in corpus]
        self.vectorizer.fit(lemmatized_corpus)
        self.is_fitted = True

    def _preprocess(self, text: str) -> str:
        """Lemmatizes and cleans text for semantic matching."""
        if not text or not self.nlp:
            return text or ""
        
        doc = self.nlp(text.lower())
        # Keep only alphanumeric and lemmatize
        tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
        return " ".join(tokens)

    def calculate_similarity(self, resume_data: Dict[str, Any], jd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates similarity scores across multiple semantic dimensions.
        """
        if not self.is_fitted:
            # Fallback fit if not fitted (though not ideal)
            all_text = self._extract_resume_text(resume_data) + " " + self._extract_jd_text(jd_data)
            self.fit([all_text])

        # 1. Extract texts
        resume_skills_text = self._extract_resume_skills(resume_data)
        jd_skills_text = self._extract_jd_skills(jd_data)
        
        resume_exp_text = self._extract_resume_experience(resume_data)
        jd_exp_text = self._extract_jd_experience(jd_data)
        
        # 2. Transform to vectors
        # Preprocess first
        resume_skills_text = self._preprocess(resume_skills_text)
        jd_skills_text = self._preprocess(jd_skills_text)
        resume_exp_text = self._preprocess(resume_exp_text)
        jd_exp_text = self._preprocess(jd_exp_text)

        res_skill_vec = self.vectorizer.transform([resume_skills_text])
        jd_skill_vec = self.vectorizer.transform([jd_skills_text])
        
        res_exp_vec = self.vectorizer.transform([resume_exp_text])
        jd_exp_vec = self.vectorizer.transform([jd_exp_text])
        
        # 3. Calculate Cosine Similarity
        skill_sim = cosine_similarity(res_skill_vec, jd_skill_vec)[0][0]
        exp_sim = cosine_similarity(res_exp_vec, jd_exp_vec)[0][0]
        
        # 4. Overall score (weighted)
        # Skills are crucial, but experience summary provides the 'deep' context
        weights = {
            "skills": 0.45,
            "experience": 0.55
        }
        
        total_score = (skill_sim * weights["skills"]) + (exp_sim * weights["experience"])
        
        return {
            "total_score": round(float(total_score), 4),
            "dimensions": {
                "skill_semantic_overlap": round(float(skill_sim), 4),
                "experience_semantic_overlap": round(float(exp_sim), 4)
            },
            "match_level": self._get_match_level(total_score)
        }

    def _extract_resume_skills(self, data: Dict) -> str:
        # data might be from structured_experiences or skills extractor
        skills = data.get("skills", [])
        if isinstance(skills, list):
            # Handle list of dicts or list of strings
            return " ".join([s if isinstance(s, str) else s.get("name", "") for s in skills])
        return ""

    def _extract_jd_skills(self, data: Dict) -> str:
        req = data.get("skills_required", [])
        pref = data.get("skills_preferred", [])
        return " ".join([s.get("name", "") for s in req + pref])

    def _extract_resume_experience(self, data: Dict) -> str:
        exps = data.get("structured_experiences", [])
        return " ".join([e.get("description", "") for e in exps])

    def _extract_jd_experience(self, data: Dict) -> str:
        summary = data.get("summary", "")
        resp = " ".join(data.get("responsibilities", []))
        return summary + " " + resp

    def _extract_resume_text(self, data: Dict) -> str:
        return self._extract_resume_skills(data) + " " + self._extract_resume_experience(data)

    def _extract_jd_text(self, data: Dict) -> str:
        return self._extract_jd_skills(data) + " " + self._extract_jd_experience(data)

    def _get_match_level(self, score: float) -> str:
        if score > 0.6: return "Excellent Match"
        if score > 0.4: return "Good Match"
        if score > 0.2: return "Potential Match"
        return "Low Match"

    @staticmethod
    def build_corpus(resume_files: List[Dict], jd_files: List[Dict]) -> List[str]:
        """Static helper to build a corpus from loaded data."""
        corpus = []
        for res in resume_files:
            # Basic text extraction for fitting
            skills = " ".join([s if isinstance(s, str) else s.get("name", "") for s in res.get("skills", [])])
            exps = " ".join([e.get("description", "") for e in res.get("structured_experiences", [])])
            corpus.append(skills + " " + exps)
        
        for jd in jd_files:
            skills = " ".join([s.get("name", "") for s in jd.get("skills_required", []) + jd.get("skills_preferred", [])])
            summary = jd.get("summary", "") + " " + " ".join(jd.get("responsibilities", []))
            corpus.append(skills + " " + summary)
        
        return corpus
