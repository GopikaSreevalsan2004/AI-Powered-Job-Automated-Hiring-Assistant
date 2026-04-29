from typing import List, Dict
from fuzzywuzzy import fuzz

class ExperienceScorer:
    """
    Scores the relevance of professional experience against specific job requirements.
    """
    def __init__(self):
        self.title_weight = 0.5
        self.skill_weight = 0.4
        self.duration_weight = 0.1

    def calculate_role_similarity(self, role1: str, role2: str) -> float:
        """
        Computes role-to-role similarity using fuzzy matching.
        """
        if not role1 or not role2:
            return 0.0
        return fuzz.token_sort_ratio(role1.lower(), role2.lower()) / 100.0

    def score_relevance(self, experience: Dict, job_requirements: Dict) -> float:
        """
        Scores a single role entry against job requirements.
        """
        target_role = job_requirements.get('target_role', '')
        title_score = self.calculate_role_similarity(experience.get('role', ''), target_role)
        
        exp_desc = experience.get('description', '').lower()
        req_skills = job_requirements.get('required_skills', [])
        
        skill_hits = sum(1 for skill in req_skills if skill.lower() in exp_desc)
        skill_score = (skill_hits / len(req_skills)) if req_skills else 0.5
            
        start_dt = experience.get('start_dt')
        end_dt = experience.get('end_dt')
        duration_score = 0.0
        if start_dt and end_dt:
            months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
            duration_score = min(months / 24, 1.0) # Cap at 2 years
            
        total_score = (title_score * self.title_weight) + (skill_score * self.skill_weight) + (duration_score * self.duration_weight)
        return round(total_score, 2)

    def rank_experiences(self, experiences: List[Dict], job_requirements: Dict) -> List[Dict]:
        """
        Ranks a candidate's experiences based on relevance score.
        """
        for exp in experiences:
            exp['relevance_score'] = self.score_relevance(exp, job_requirements)
            
        return sorted(experiences, key=lambda x: x.get('relevance_score', 0), reverse=True)
