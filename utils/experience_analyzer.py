from datetime import datetime
from typing import List, Dict
import pandas as pd

class ExperienceAnalyzer:
    @staticmethod
    def calculate_duration_months(start_date: datetime, end_date: datetime) -> int:
        if not start_date or not end_date:
            return 0
        return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)

    def analyze_experience(self, experiences: List[Dict]) -> Dict:
        """
        Analyzes a list of experience objects.
        """
        if not experiences:
            return {
                "total_experience_months": 0,
                "gaps": [],
                "overlaps": []
            }

        # Sort experiences by start date
        sorted_exp = sorted(experiences, key=lambda x: x.get('start_dt') or datetime.min)
        
        total_months = 0
        gaps = []
        overlaps = []
        
        last_end_date = None
        
        for i, exp in enumerate(sorted_exp):
            start_dt = exp.get('start_dt')
            end_dt = exp.get('end_dt')
            
            if not start_dt or not end_dt:
                continue
                
            duration = self.calculate_duration_months(start_dt, end_dt)
            total_months += duration
            
            if last_end_date:
                if start_dt > last_end_date:
                    # Gap detected
                    gap_months = self.calculate_duration_months(last_end_date, start_dt)
                    if gap_months > 1: # Ignore minor gaps
                        gaps.append({
                            "after_company": sorted_exp[i-1].get('company'),
                            "before_company": exp.get('company'),
                            "duration_months": gap_months
                        })
                elif start_dt < last_end_date:
                    # Overlap detected
                    overlap_months = self.calculate_duration_months(start_dt, last_end_date)
                    if overlap_months > 0:
                        overlaps.append({
                            "companies": [sorted_exp[i-1].get('company'), exp.get('company')],
                            "overlap_months": overlap_months
                        })
            
            if last_end_date is None or end_dt > last_end_date:
                last_end_date = end_dt

        return {
            "total_experience_months": total_months,
            "total_experience_years": round(total_months / 12, 1),
            "gaps": gaps,
            "overlaps": overlaps
        }
