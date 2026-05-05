import os
import json
import pandas as pd
from ats_engine.master_scorer import MasterScorer
from ats_engine.semantic_engine import SemanticEngine
from ats_engine.shortlisting_engine import ShortlistingEngine

def load_all_data():
    """Loads and merges all processed data dimensions."""
    # 1. Experience
    with open('data/processed/structured_experiences.json', 'r', encoding='utf-8') as f:
        all_exp = json.load(f)
    
    # 2. Education
    with open('data/processed/structured_academic_profiles.json', 'r', encoding='utf-8') as f:
        all_edu = json.load(f)
        
    # 3. Skills
    all_skills = {}
    skills_dir = 'data/extracted_skills'
    for f_name in os.listdir(skills_dir):
        if f_name.endswith('_skills.json'):
            res_name = f_name.replace('_skills.json', '.pdf')
            with open(os.path.join(skills_dir, f_name), 'r', encoding='utf-8') as f:
                all_skills[res_name] = json.load(f)
    
    # 4. JDs
    jd_dir = 'output/jd files'
    all_jds = []
    for jd_file in sorted(os.listdir(jd_dir)):
        if jd_file.endswith('.json'):
            with open(os.path.join(jd_dir, jd_file), 'r', encoding='utf-8') as f:
                all_jds.append(json.load(f))
    
    # Pre-build Semantic Corpus
    resume_combined_list = []
    for res_name in all_exp.keys():
        resume_combined_list.append({
            "structured_experiences": all_exp[res_name].get("structured_experiences", []),
            "skills": all_skills.get(res_name, [])
        })
    
    corpus = SemanticEngine.build_corpus(resume_combined_list, all_jds)
    semantic_engine = SemanticEngine(corpus=corpus)
                
    return all_exp, all_edu, all_skills, all_jds, semantic_engine

def main():
    print("Initializing Cross-Matching Engine for all JDs and Resumes...")
    all_exp, all_edu, all_skills, all_jds, semantic_engine = load_all_data()
    
    # Initialize engines with default thresholds
    shortlister = ShortlistingEngine(shortlist_threshold=0.35, review_threshold=0.15)
    scorer = MasterScorer() # uses default weights
    
    cross_match_results = []
    
    # We'll limit to first 15 JDs for performance and clarity in the report, 
    # but the logic supports all.
    limit_jds = all_jds[:15] 
    
    print(f"Processing {len(all_exp)} resumes against {len(limit_jds)} Job Descriptions...")
    
    for jd in limit_jds:
        jd_title = jd.get('job_title', 'Unknown')
        jd_reqs = {"required_skills": [s['name'] for s in jd['skills_required']]}
        
        for res_name, exp_data in all_exp.items():
            edu_data = all_edu.get(res_name, {})
            skills_data = all_skills.get(res_name, [])
            
            # 1. Semantic Similarity
            res_data_for_sem = {"structured_experiences": exp_data.get("structured_experiences", []), "skills": skills_data}
            sem_result = semantic_engine.calculate_similarity(res_data_for_sem, jd)
            
            # 2. Master Score
            score_data = scorer.calculate_candidate_score(skills_data, exp_data, edu_data, sem_result, jd_reqs)
            
            # 3. Categorize
            status = "Auto-Rejected"
            if score_data['final_score'] >= shortlister.shortlist_threshold:
                status = "Shortlisted"
            elif score_data['final_score'] >= shortlister.review_threshold:
                status = "Review"
                
            cross_match_results.append({
                "Job Description": jd_title,
                "Candidate": res_name,
                "Score": f"{score_data['final_score']*100:.1f}%",
                "Status": status
            })

    # Generate Cross-Match Report
    df = pd.DataFrame(cross_match_results)
    output_path = "output/cross_match_matrix.csv"
    df.to_csv(output_path, index=False)
    
    # Generate Markdown Matrix for display
    summary_path = "output/cross_match_summary.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("# Cross-Matching Matrix: Resumes vs Job Descriptions\n\n")
        f.write("This report shows the status of every candidate across multiple job openings.\n\n")
        
        # Create a pivot-table style view for MD
        pivot_df = df.pivot(index='Job Description', columns='Candidate', values='Status')
        
        # MD Tables are hard with 11 columns, so we'll group by JD
        for jd_name in df['Job Description'].unique():
            f.write(f"## {jd_name}\n")
            subset = df[df['Job Description'] == jd_name].sort_values(by='Score', ascending=False)
            f.write("| Status | Candidate | Score |\n")
            f.write("|--------|-----------|-------|\n")
            for _, row in subset.iterrows():
                status_emoji = "🎯 " if row['Status'] == "Shortlisted" else "🔍 " if row['Status'] == "Review" else "❌ "
                f.write(f"| {status_emoji}{row['Status']} | {row['Candidate']} | {row['Score']} |\n")
            f.write("\n")

    print(f"\nCross-matching complete.")
    print(f"- CSV Matrix: {output_path}")
    print(f"- Markdown Summary: {summary_path}")

if __name__ == "__main__":
    main()
