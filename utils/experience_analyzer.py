from typing import List, Dict

class ExperienceAnalyzer:
    """
    Analyzes an individual's career trajectory by calculating total experience,
    detecting employment gaps, and identifying overlapping roles.
    """
    def __init__(self):
        pass

    def analyze_experience(self, experiences: List[Dict]) -> Dict:
        """
        Analyzes a candidate's timeline.
        Requires 'start_dt' and 'end_dt' to be populated datetime objects.
        """
        total_months = 0
        gaps = []
        overlaps = []
        
        # Filter experiences with valid dates
        valid_exps = [e for e in experiences if e.get('start_dt') and e.get('end_dt')]
        
        # Sort by start date
        valid_exps.sort(key=lambda x: x['start_dt'])
        
        if not valid_exps:
            return {
                "total_experience_years": 0.0,
                "gaps": [],
                "overlaps": []
            }
            
        # Calculate timeline
        for i in range(len(valid_exps)):
            curr = valid_exps[i]
            
            # Add duration
            months = (curr['end_dt'].year - curr['start_dt'].year) * 12 + (curr['end_dt'].month - curr['start_dt'].month)
            total_months += max(0, months)
            
            # Check gaps and overlaps with next experience
            if i < len(valid_exps) - 1:
                next_exp = valid_exps[i+1]
                
                # If current ends after next begins -> overlap
                if curr['end_dt'] > next_exp['start_dt']:
                    overlap_months = (curr['end_dt'].year - next_exp['start_dt'].year) * 12 + (curr['end_dt'].month - next_exp['start_dt'].month)
                    overlaps.append({
                        "role1": curr.get('role', 'Unknown'),
                        "role2": next_exp.get('role', 'Unknown'),
                        "overlap_months": overlap_months
                    })
                    # Subtract overlap from total to avoid double counting
                    total_months -= overlap_months
                
                # If current ends before next begins -> gap
                elif curr['end_dt'] < next_exp['start_dt']:
                    gap_months = (next_exp['start_dt'].year - curr['end_dt'].year) * 12 + (next_exp['start_dt'].month - curr['end_dt'].month)
                    if gap_months > 1: # Ignore 1 month gap
                        gaps.append({
                            "after_role": curr.get('role', 'Unknown'),
                            "before_role": next_exp.get('role', 'Unknown'),
                            "gap_months": gap_months
                        })
                        
        total_years = round(total_months / 12.0, 1)
        
        return {
            "total_experience_years": total_years,
            "gaps": gaps,
            "overlaps": overlaps
        }
