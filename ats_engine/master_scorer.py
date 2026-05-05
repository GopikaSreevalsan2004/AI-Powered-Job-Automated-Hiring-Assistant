from typing import Dict, List, Any, Optional
import json

class MasterScorer:
    """
    Transparent, explainable candidate scoring framework that aggregates
    multiple scoring dimensions into a final candidate profile.
    """
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default weights - total must be 1.0
        self.weights = weights or {
            "skill_match": 0.30,
            "experience_relevance": 0.35,
            "education_alignment": 0.15,
            "semantic_similarity": 0.20
        }
        self._validate_weights()

    def _validate_weights(self):
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            # Normalize if they don't add up to 1
            for k in self.weights:
                self.weights[k] /= total

    def calculate_candidate_score(self, 
                                 skills_data: List[Dict], 
                                 experience_data: Dict, 
                                 education_data: Dict, 
                                 semantic_data: Dict,
                                 jd_requirements: Dict) -> Dict[str, Any]:
        """
        Generates a final explainable score for a candidate.
        Handles missing data gracefully by providing explanations.
        """
        
        # 1. Dimension: Skill Match
        # We calculate this as the ratio of required skills found in the resume
        req_skills = [s.lower() for s in jd_requirements.get("required_skills", [])]
        found_skills = [s.get("name", "").lower() for s in skills_data]
        
        skill_score = 0.0
        skill_explanation = "No required skills found."
        if req_skills:
            matches = [s for s in req_skills if any(s in f for f in found_skills)]
            skill_score = len(matches) / len(req_skills)
            skill_explanation = f"Matched {len(matches)} out of {len(req_skills)} required skills."
        elif found_skills:
            skill_score = 0.5 # Neutral if no requirements specified
            skill_explanation = "No specific skills required by JD; candidate has professional skills listed."
        
        # 2. Dimension: Experience Relevance
        # Taken from the best experience entry's score
        exp_score = experience_data.get("analysis", {}).get("total_experience_years", 0) / 10 # Normalize loosely
        # Better: use the relevance_score from the structured_experiences if available
        exps = experience_data.get("structured_experiences", [])
        best_exp_score = max([e.get("relevance_score", 0) for e in exps]) if exps else 0.0
        exp_explanation = f"Best experience entry relevance: {best_exp_score:.2f}." if exps else "No professional experience detected."
        
        # 3. Dimension: Education Alignment
        # Taken from the StructuredAcademicProfile's total_academic_score
        edu_score = education_data.get("relevance_scoring", {}).get("total_academic_score", 0)
        edu_explanation = f"Academic alignment score: {edu_score:.2f}." if edu_score > 0 else "Education does not match requirements or was not found."
        
        # 4. Dimension: Semantic Similarity
        sem_score = semantic_data.get("total_score", 0)
        sem_explanation = f"Contextual semantic overlap: {sem_score:.2f}."
        
        # Final Weighted Score
        weighted_score = (
            (skill_score * self.weights["skill_match"]) +
            (best_exp_score * self.weights["experience_relevance"]) +
            (edu_score * self.weights["education_alignment"]) +
            (sem_score * self.weights["semantic_similarity"])
        )
        
        return {
            "final_score": round(weighted_score, 4),
            "score_breakdown": {
                "skill_match": {
                    "score": round(skill_score, 4),
                    "weight": self.weights["skill_match"],
                    "contribution": round(skill_score * self.weights["skill_match"], 4),
                    "explanation": skill_explanation
                },
                "experience_relevance": {
                    "score": round(best_exp_score, 4),
                    "weight": self.weights["experience_relevance"],
                    "contribution": round(best_exp_score * self.weights["experience_relevance"], 4),
                    "explanation": exp_explanation
                },
                "education_alignment": {
                    "score": round(edu_score, 4),
                    "weight": self.weights["education_alignment"],
                    "contribution": round(edu_score * self.weights["education_alignment"], 4),
                    "explanation": edu_explanation
                },
                "semantic_similarity": {
                    "score": round(sem_score, 4),
                    "weight": self.weights["semantic_similarity"],
                    "contribution": round(sem_score * self.weights["semantic_similarity"], 4),
                    "explanation": sem_explanation
                }
            },
            "status": "Incomplete Data" if (not exps or not found_skills) else "Complete Profile"
        }

    def generate_explanation_text(self, scoring_output: Dict) -> str:
        """Converts structured scoring output into a human-readable explanation."""
        breakdown = scoring_output["score_breakdown"]
        text = f"Candidate scored {scoring_output['final_score']*100:.1f}/100. "
        
        reasons = []
        if breakdown["experience_relevance"]["score"] > 0.5:
            reasons.append("Strong professional experience match")
        if breakdown["skill_match"]["score"] > 0.7:
            reasons.append("Excellent technical skill alignment")
        if breakdown["education_alignment"]["score"] > 0.7:
            reasons.append("Highly relevant academic background")
            
        if reasons:
            text += "Strengths include: " + ", ".join(reasons) + ". "
        
        weaknesses = []
        if breakdown["skill_match"]["score"] < 0.3:
            weaknesses.append("Missing core technical skills")
        if breakdown["experience_relevance"]["score"] < 0.2:
            weaknesses.append("Minimal relevant work history")
            
        if weaknesses:
            text += "Areas for concern: " + ", ".join(weaknesses) + "."
            
        return text
