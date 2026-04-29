from typing import List, Dict
from fuzzywuzzy import fuzz
import numpy as np

class ExperienceScorer:
    def __init__(self):
        # Weighting factors
        self.title_weight = 0.5
        self.description_weight = 0.3
        self.duration_weight = 0.2

    def calculate_role_similarity(self, role1: str, role2: str) -> float:
        """
        Computes similarity between two job titles.
        """
        if not role1 or not role2:
            return 0.0
        
        # Use fuzzy matching for titles
        return fuzz.token_sort_ratio(role1.lower(), role2.lower()) / 100.0

    def score_relevance(self, experience: Dict, job_requirements: Dict) -> float:
        """
        Scores a single experience entry against job requirements.
        """
        # 1. Title Relevance
        target_title = job_requirements.get('target_role', '')
        title_score = self.calculate_role_similarity(experience.get('role', ''), target_title)
        
        # 2. Skill Relevance (if skills are provided in exp and JD)
        exp_description = experience.get('description', '').lower()
        req_skills = job_requirements.get('required_skills', [])
        
        skill_hits = 0
        if req_skills:
            for skill in req_skills:
                if skill.lower() in exp_description:
                    skill_hits += 1
            skill_score = skill_hits / len(req_skills) if req_skills else 0
        else:
            skill_score = 0.5 # Neutral if no skills provided
            
        # 3. Duration Relevance
        # If the role was held for a long time, it might be more relevant
        # This is a simplified heuristic
        start_dt = experience.get('start_dt')
        end_dt = experience.get('end_dt')
        duration_score = 0.0
        if start_dt and end_dt:
            months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
            duration_score = min(months / 24, 1.0) # Cap at 2 years for max duration score
            
        # Combined Score
        total_score = (title_score * 0.5) + (skill_score * 0.4) + (duration_score * 0.1)
        return round(total_score, 2)

    def rank_experiences(self, experiences: List[Dict], job_requirements: Dict) -> List[Dict]:
        """
        Ranks experiences based on relevance to job requirements.
        """
        for exp in experiences:
            exp['relevance_score'] = self.score_relevance(exp, job_requirements)
            
        return sorted(experiences, key=lambda x: x['relevance_score'], reverse=True)
