from typing import Dict, List, Any
import pandas as pd
import os

class ShortlistingEngine:
    """
    Automates the ranking, filtering, and categorization of candidates
    based on their final ATS scores.
    """
    
    def __init__(self, 
                 shortlist_threshold: float = 0.6, 
                 review_threshold: float = 0.3):
        self.shortlist_threshold = shortlist_threshold
        self.review_threshold = review_threshold

    def process_rankings(self, candidate_scores: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """
        Sorts candidates and categorizes them into zones: Shortlisted, Review, Rejected.
        """
        # Convert dict to list of candidates with their names
        candidate_list = []
        for name, data in candidate_scores.items():
            candidate_list.append({
                "candidate_name": name,
                **data
            })
            
        # 1. Sorting by final score
        sorted_candidates = sorted(candidate_list, key=lambda x: x['final_score'], reverse=True)
        
        # 2. Categorization (Auto-reject and review zones)
        shortlisted = []
        review = []
        rejected = []
        
        for cand in sorted_candidates:
            score = cand['final_score']
            if score >= self.shortlist_threshold:
                cand['status_zone'] = "Shortlisted"
                shortlisted.append(cand)
            elif score >= self.review_threshold:
                cand['status_zone'] = "Needs Review"
                review.append(cand)
            else:
                cand['status_zone'] = "Auto-Rejected"
                rejected.append(cand)
                
        return {
            "all_ranked": sorted_candidates,
            "shortlisted": shortlisted,
            "needs_review": review,
            "auto_rejected": rejected
        }

    def generate_recruiter_report(self, processed_data: Dict[str, List[Dict]], output_path: str):
        """
        Generates a recruiter-friendly CSV/Excel-style report.
        """
        report_rows = []
        for zone in ["shortlisted", "needs_review", "auto_rejected"]:
            for cand in processed_data[zone]:
                report_rows.append({
                    "Rank": 0, # Will fill below
                    "Candidate": cand['candidate_name'],
                    "Status": cand['status_zone'],
                    "Final Score": f"{cand['final_score']*100:.1f}%",
                    "Skills Match": f"{cand['score_breakdown']['skill_match']['score']*100:.1f}%",
                    "Exp Score": f"{cand['score_breakdown']['experience_relevance']['score']*100:.1f}%",
                    "Edu Score": f"{cand['score_breakdown']['education_alignment']['score']*100:.1f}%",
                    "Semantic Sim": f"{cand['score_breakdown']['semantic_similarity']['score']*100:.1f}%",
                    "Summary": cand['explanation']
                })
        
        df = pd.DataFrame(report_rows)
        # Add Rank
        df['Rank'] = range(1, len(df) + 1)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        return output_path

    def generate_markdown_summary(self, processed_data: Dict[str, List[Dict]]) -> str:
        """Generates a high-level summary in Markdown for quick viewing."""
        summary = "# Hiring Automation: Shortlisting Summary\n\n"
        
        summary += "## 🎯 Shortlisted Candidates\n"
        if not processed_data['shortlisted']:
            summary += "_No candidates met the high-bar threshold for auto-shortlisting._\n\n"
        else:
            summary += "| Rank | Name | Score | Key Strength |\n"
            summary += "|------|------|-------|--------------|\n"
            for i, c in enumerate(processed_data['shortlisted']):
                summary += f"| {i+1} | {c['candidate_name']} | {c['final_score']*100:.1f}% | {c['explanation'].split('.')[0]} |\n"
            summary += "\n"

        summary += "## 🔍 Needs Manual Review\n"
        if not processed_data['needs_review']:
            summary += "_No candidates in the mid-range review zone._\n\n"
        else:
            summary += "| Rank | Name | Score | Recommendation |\n"
            summary += "|------|------|-------|----------------|\n"
            for i, c in enumerate(processed_data['needs_review']):
                summary += f"| {i+1} | {c['candidate_name']} | {c['final_score']*100:.1f}% | Review manually for potential |\n"
            summary += "\n"
            
        summary += "## ❌ Auto-Rejected\n"
        summary += f"Total: {len(processed_data['auto_rejected'])} candidates filtered out based on low alignment scores.\n"
        
        return summary
