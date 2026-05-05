import json
import os
from ats_engine.shortlisting_engine import ShortlistingEngine

def main():
    # 1. Load the final scores
    scores_path = 'output/processed_results/candidate_final_scores.json'
    
    if not os.path.exists(scores_path):
        print(f"Error: {scores_path} not found. Please run final scoring first.")
        return
        
    with open(scores_path, 'r', encoding='utf-8') as f:
        candidate_scores = json.load(f)
        
    # 2. Initialize Shortlisting Engine
    # Given the current data distribution, we'll use slightly lower thresholds for demo
    # In production, these would be configured per role requirements.
    engine = ShortlistingEngine(
        shortlist_threshold=0.3, # Top candidates
        review_threshold=0.1     # Mid-range
    )
    
    # 3. Process Rankings and Categorize
    print("Automating candidate shortlisting and filtering...")
    processed_rankings = engine.process_rankings(candidate_scores)
    
    # 4. Generate Recruiter-Friendly Output
    csv_path = 'output/shortlisting_report.csv'
    engine.generate_recruiter_report(processed_rankings, csv_path)
    
    # 5. Generate Markdown Summary
    md_summary = engine.generate_markdown_summary(processed_rankings)
    md_path = 'output/shortlisting_summary.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_summary)
        
    # 6. Output structured automation results
    results_path = 'output/automation_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump({
            "shortlisted_count": len(processed_rankings["shortlisted"]),
            "review_count": len(processed_rankings["needs_review"]),
            "rejected_count": len(processed_rankings["auto_rejected"]),
            "top_candidate": processed_rankings["all_ranked"][0]["candidate_name"] if processed_rankings["all_ranked"] else None
        }, f, indent=4)

    print(f"\nShortlisting complete.")
    print(f"- Recruiter CSV: {csv_path}")
    print(f"- Markdown Summary: {md_path}")
    print(f"- Automation Stats: {results_path}")

if __name__ == "__main__":
    main()
