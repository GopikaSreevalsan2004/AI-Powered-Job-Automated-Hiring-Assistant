from typing import List, Dict
from parsers.experience_parser import ExperienceParser
from utils.experience_analyzer import ExperienceAnalyzer
from scoring.experience_scorer import ExperienceScorer

class ExperienceEngine:
    """
    Coordinates the parsing, analysis, and scoring of candidate experience.
    """
    def __init__(self):
        self.parser = ExperienceParser()
        self.analyzer = ExperienceAnalyzer()
        self.scorer = ExperienceScorer()

    def process_experience_text(self, text: str, job_requirements: Dict = None) -> Dict:
        """
        Full pipeline: Parse -> Analyze -> Score
        """
        # 1. Parse
        raw_experiences = self.parser.parse_experience_block(text)
        
        # Normalize dates for analyzer and scorer
        processed_experiences = []
        for exp in raw_experiences:
            exp['start_dt'] = self.parser.normalize_dates(exp.get('start_date'))
            exp['end_dt'] = self.parser.normalize_dates(exp.get('end_date'))
            processed_experiences.append(exp)
            
        # 2. Analyze (calculate total exp, gaps, overlaps)
        analysis = self.analyzer.analyze_experience(processed_experiences)
        
        # 3. Score relevance to target role (if requirements provided)
        if job_requirements:
            ranked_experiences = self.scorer.rank_experiences(processed_experiences, job_requirements)
        else:
            ranked_experiences = processed_experiences

        return {
            "structured_experiences": ranked_experiences,
            "analysis": analysis
        }
