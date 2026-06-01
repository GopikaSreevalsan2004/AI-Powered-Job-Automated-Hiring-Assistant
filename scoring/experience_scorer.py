import re
from typing import List, Dict
from fuzzywuzzy import fuzz

class ExperienceScorer:
    """
    Scores the relevance of professional experience against specific job requirements.
    Provides detailed role-to-role similarity logic and requirement analysis.
    """
    def __init__(self):
        # Weights for the final relevance score
        self.title_weight = 0.45
        self.skill_weight = 0.40
        self.duration_weight = 0.15
        
        # Seniority levels for mapping
        self.seniority_levels = {
            'junior': 1, 'entry': 1, 'associate': 1, 'intern': 0,
            'mid': 2, '': 2, # Default level
            'senior': 3, 'sr': 3, 'lead': 4, 'principal': 5, 
            'staff': 5, 'manager': 6, 'director': 7, 'vp': 8, 'head': 8
        }

    def _extract_seniority(self, title: str) -> int:
        """Extracts a numerical seniority level from a job title."""
        title_lower = title.lower()
        for level_str, level_val in sorted(self.seniority_levels.items(), key=lambda x: len(x[0]), reverse=True):
            if level_str and re.search(rf'\b{level_str}\b', title_lower):
                return level_val
        return self.seniority_levels['']

    def _clean_title(self, title: str) -> str:
        """Removes seniority words to compare base roles."""
        cleaned = title.lower()
        for level_str in self.seniority_levels.keys():
            if level_str:
                cleaned = re.sub(rf'\b{level_str}\b', '', cleaned)
        # Remove extra spaces
        return re.sub(r'\s+', ' ', cleaned).strip()

    def calculate_role_similarity(self, role1: str, role2: str) -> float:
        """
        Computes role-to-role similarity using fuzzy matching on base titles 
        and factoring in seniority alignment.
        """
        if not role1 or not role2:
            return 0.0
            
        # 1. Base title similarity (e.g. "Software Engineer" vs "Software Developer")
        base_role1 = self._clean_title(role1)
        base_role2 = self._clean_title(role2)
        
        # Using token set ratio to handle order differences ("Engineer Software" vs "Software Engineer")
        base_sim = fuzz.token_set_ratio(base_role1, base_role2) / 100.0
        
        # 2. Seniority alignment
        sen1 = self._extract_seniority(role1)
        sen2 = self._extract_seniority(role2)
        
        # Calculate penalty for seniority mismatch (max penalty 0.2)
        sen_diff = abs(sen1 - sen2)
        sen_penalty = min(sen_diff * 0.05, 0.2)
        
        # Final similarity score (bounded between 0 and 1)
        final_sim = max(0.0, base_sim - sen_penalty)
        return final_sim

    def score_relevance(self, experience: Dict, job_requirements: Dict) -> Dict:
        """
        Scores a single role entry against job requirements.
        Returns a detailed scoring breakdown.
        """
        target_role = job_requirements.get('target_role', '')
        candidate_role = experience.get('role', '')
        
        # 1. Title Score
        title_score = self.calculate_role_similarity(candidate_role, target_role)
        
        # 2. Skills Score
        exp_desc = experience.get('description', '').lower()
        req_skills = job_requirements.get('required_skills', [])
        
        skill_hits = 0
        matched_skills = []
        for skill in req_skills:
            # Use word boundaries to avoid partial matches (e.g. "C" in "Mac")
            if re.search(rf'\b{re.escape(skill.lower())}\b', exp_desc):
                skill_hits += 1
                matched_skills.append(skill)
                
        skill_score = (skill_hits / len(req_skills)) if req_skills else 0.5
            
        # 3. Duration Score
        start_dt = experience.get('start_dt')
        end_dt = experience.get('end_dt')
        duration_score = 0.0
        months = 0
        
        if start_dt and end_dt:
            # Ensure they are date/datetime objects
            if isinstance(start_dt, str):
                from datetime import datetime
                try:
                    start_dt = datetime.strptime(start_dt, "%Y-%m-%d").date()
                except: pass
            if isinstance(end_dt, str):
                from datetime import datetime
                try:
                    end_dt = datetime.strptime(end_dt, "%Y-%m-%d").date()
                except: pass
                
            try:
                months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
                months = max(0, months)
            except (AttributeError, TypeError):
                months = 0
            
            # Dynamic duration scoring based on requirements, default to max at 3 years (36 months)
            target_months = job_requirements.get('required_experience_months', 36)
            duration_score = min(months / target_months, 1.0) if target_months > 0 else 1.0
            
        # 4. Total Score Calculation
        total_score = (title_score * self.title_weight) + \
                      (skill_score * self.skill_weight) + \
                      (duration_score * self.duration_weight)
                      
        return {
            'total_score': round(total_score, 2),
            'title_score': round(title_score, 2),
            'skill_score': round(skill_score, 2),
            'duration_score': round(duration_score, 2),
            'matched_skills': matched_skills,
            'duration_months': months
        }

    def rank_experiences(self, experiences: List[Dict], job_requirements: Dict) -> List[Dict]:
        """
        Ranks a candidate's experiences based on relevance score.
        Injects the scoring details directly into the experience dictionaries.
        """
        for exp in experiences:
            score_details = self.score_relevance(exp, job_requirements)
            exp['relevance_score'] = score_details['total_score']
            exp['scoring_details'] = score_details
            
        return sorted(experiences, key=lambda x: x.get('relevance_score', 0), reverse=True)

