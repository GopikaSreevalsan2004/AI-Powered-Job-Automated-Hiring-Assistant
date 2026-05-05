import json
import os
import pandas as pd
from utils.fairness_module import FairnessModule

def main():
    print("Initializing Fair Evaluation & Bias Reduction Module...")
    
    # 1. Load the latest candidate scores
    scores_path = 'data/processed/candidate_final_scores.json'
    if not os.path.exists(scores_path):
        print(f"Error: {scores_path} not found. Please run final scoring first.")
        return
        
    with open(scores_path, 'r', encoding='utf-8') as f:
        candidate_scores = json.load(f)
        
    fair_mod = FairnessModule()
    
    # 2. Process for Fairness
    raw_scores = []
    fair_results = []
    
    print(f"Applying anonymization and normalization to {len(candidate_scores)} candidates...")
    
    for filename, data in candidate_scores.items():
        # Anonymize Name
        anon_id = fair_mod.anonymize_candidate_name(filename)
        
        # Raw score for normalization
        raw_scores.append(data['final_score'])
        
        # Check for bias in summary or explanation
        bias_check = fair_mod.check_bias_indicators(data['explanation'])
        
        fair_results.append({
            "Candidate ID": anon_id,
            "Raw Score": data['final_score'],
            "Summary": data['explanation'],
            "Bias Status": bias_check['recommendation']
        })
        
    # 3. Apply Scoring Normalization
    normalized_scores = fair_mod.normalize_scores(raw_scores)
    
    for i, res in enumerate(fair_results):
        res["Normalized Score"] = f"{normalized_scores[i]*100:.1f}%"
        res["Raw Score"] = f"{res['Raw Score']*100:.1f}%"

    # 4. Generate Fair Ranking Report
    df = pd.DataFrame(fair_results)
    # Sort by normalized score
    df = df.sort_values(by="Normalized Score", ascending=False)
    
    report_path = 'output/fair_evaluation_report.csv'
    df.to_csv(report_path, index=False)
    
    # Generate MD Summary
    md_path = 'output/fair_evaluation_summary.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Fair Evaluation Report (Blind Review Mode)\n\n")
        f.write("This report uses anonymized IDs and normalized scoring to ensure fair candidate assessment.\n\n")
        f.write("| Rank | Candidate ID | Normalized Score | Raw Score | Bias Detection | Summary |\n")
        f.write("|------|--------------|------------------|-----------|----------------|---------|\n")
        
        for i, row in enumerate(df.values):
            f.write(f"| {i+1} | {row[0]} | {row[4]} | {row[1]} | {row[3]} | {row[2]} |\n")
            
    print(f"\nFair evaluation complete.")
    print(f"- Anonymized Report: {report_path}")
    print(f"- Fair Summary (Blind): {md_path}")
    print("- Bias Reduction Documentation: docs/bias_reduction_logic.md")

if __name__ == "__main__":
    main()
