import json
import os
from typing import List, Dict, Any

def calculate_set_metrics(extracted: List[str], ground_truth: List[str]):
    extracted_set = set(s.lower() for s in extracted)
    gt_set = set(s.lower() for s in ground_truth)
    
    tp = len(extracted_set.intersection(gt_set))
    fp = len(extracted_set - gt_set)
    fn = len(gt_set - extracted_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "mismatches": list(gt_set - extracted_set), # FN
        "hallucinations": list(extracted_set - gt_set) # FP
    }

def main():
    print("Starting ATS Accuracy Validation...")
    
    # Paths
    gt_path = 'data/validation_ground_truth.json'
    scores_path = 'data/processed/candidate_final_scores.json'
    skills_dir = 'data/extracted_skills'
    
    with open(gt_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
        
    with open(scores_path, 'r', encoding='utf-8') as f:
        ai_scores = json.load(f)
        
    report = []
    total_metrics = {"precision": 0.0, "recall": 0.0, "f1": 0.0, "count": 0}
    mismatch_cases = []
    
    for res_name, gt_data in ground_truth.items():
        if res_name not in ai_scores:
            print(f"Warning: {res_name} not found in AI scores.")
            continue
            
        ai_data = ai_scores[res_name]
        
        # 1. Skill Metrics
        skills_file = os.path.join(skills_dir, res_name.replace('.pdf', '_skills.json'))
        extracted_skills = []
        if os.path.exists(skills_file):
            with open(skills_file, 'r', encoding='utf-8') as f:
                skills_json = json.load(f)
                extracted_skills = [s['name'] for s in skills_json]
        
        skill_metrics = calculate_set_metrics(extracted_skills, gt_data['expected_skills'])
        
        # 2. Score Accuracy
        ai_score = ai_data['final_score']
        score_in_range = gt_data['expected_score_range'][0] <= ai_score <= gt_data['expected_score_range'][1]
        
        # 3. Status Check
        ai_status = "Shortlisted" if ai_score >= 0.5 else "Rejected"
        manual_status = gt_data['manual_review_status']
        status_match = ai_status == manual_status
        
        entry_report = {
            "resume": res_name,
            "category": gt_data['category'],
            "profile": gt_data['profile'],
            "skill_recall": skill_metrics['recall'],
            "skill_precision": skill_metrics['precision'],
            "expected_status": manual_status,
            "ai_status": ai_status,
            "status_match": status_match,
            "score_valid": score_in_range
        }
        report.append(entry_report)
        
        # Track totals
        total_metrics["precision"] += skill_metrics['precision']
        total_metrics["recall"] += skill_metrics['recall']
        total_metrics["f1"] += skill_metrics['f1']
        total_metrics["count"] += 1
        
        if not status_match or not score_in_range:
            mismatch_cases.append({
                "resume": res_name,
                "manual_status": manual_status,
                "ai_status": ai_status,
                "ai_score": ai_score,
                "expected_range": gt_data['expected_score_range']
            })
            
    # Calculate Averages
    avg_metrics = {k: v / total_metrics["count"] for k, v in total_metrics.items() if k != "count"}
    
    # Save Results
    results = {
        "metrics": avg_metrics,
        "detail": report,
        "mismatches": mismatch_cases
    }
    
    # Generate MD Report
    with open("ats_validation_report.md", "w", encoding="utf-8") as f:
        f.write("# ATS Validation & Accuracy Report\n\n")
        f.write("## Executive Summary\n")
        f.write(f"- **Global Skill Extraction Precision:** {avg_metrics['precision']*100:.1f}%\n")
        f.write(f"- **Global Skill Extraction Recall:** {avg_metrics['recall']*100:.1f}%\n")
        f.write(f"- **Global F1 Score:** {avg_metrics['f1']*100:.1f}%\n")
        f.write(f"- **Decision Alignment Accuracy:** {(sum(1 for r in report if r['status_match']) / len(report))*100:.1f}%\n\n")
        
        f.write("## Reliability per Role Category\n")
        f.write("| Category | Profile | Resume | Skill Recall | Status Match | Score Validity |\n")
        f.write("|----------|---------|--------|--------------|--------------|----------------|\n")
        for r in report:
            f.write(f"| {r['category']} | {r['profile']} | {r['resume']} | {r['skill_recall']*100:.1f}% | {'✅' if r['status_match'] else '❌'} | {'✅' if r['score_valid'] else '⚠️'} |\n")
        
        f.write("\n## Mismatch Cases & Improvement Backlog\n")
        if not mismatch_cases:
            f.write("No major mismatches found in this validation cycle.\n")
        else:
            f.write("| Resume | AI Status | Manual | AI Score | Expected Range | Issue |\n")
            f.write("|--------|-----------|--------|----------|----------------|-------|\n")
            for m in mismatch_cases:
                issue = "Status Mismatch" if m['ai_status'] != m['manual_status'] else "Score slightly off range"
                f.write(f"| {m['resume']} | {m['ai_status']} | {m['manual_status']} | {m['ai_score']:.2f} | {m['expected_range']} | {issue} |\n")
        
        f.write("\n## Improvement Backlog\n")
        f.write("1. **[Tech]** Improve skill extraction for compound tech terms (e.g., 'Web Development' split into 'Web' and 'Development').\n")
        f.write("2. **[Non-Tech]** Enhance the skill dictionary to recognize soft skills and non-technical role-specific competencies.\n")
        f.write("3. **[Seniority]** Refine experience scoring to better distinguish between 'Lead' roles and 'Senior' roles based on management context.\n")
        f.write("4. **[Accuracy]** Investigate low recall in legacy tech stacks mentioned in senior profiles.\n")

    print("Validation report generated: ats_validation_report.md")

if __name__ == "__main__":
    main()
