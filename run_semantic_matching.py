import os
import json
import pandas as pd
from ats_engine.semantic_engine import SemanticEngine

def load_data():
    """Loads and merges resume and JD data."""
    # 1. Load Experience data
    exp_path = 'data/processed/structured_experiences.json'
    with open(exp_path, 'r', encoding='utf-8') as f:
        all_exp = json.load(f)
    
    # 2. Load Skills data
    skills_dir = 'data/extracted_skills'
    resumes_combined = {}
    
    for filename, exp_data in all_exp.items():
        # Filename in exp_data is 'Resume1.pdf'
        # Filename in skills_dir is 'Resume1_skills.json'
        base_name = filename.replace('.pdf', '')
        skill_file = f"{base_name}_skills.json"
        skill_path = os.path.join(skills_dir, skill_file)
        
        skills = []
        if os.path.exists(skill_path):
            with open(skill_path, 'r', encoding='utf-8') as f:
                skills = json.load(f)
        
        resumes_combined[filename] = {
            "structured_experiences": exp_data.get("structured_experiences", []),
            "skills": skills
        }
    
    # 3. Load JDs
    jd_dir = 'output/jd files'
    all_jds = []
    for jd_file in os.listdir(jd_dir):
        if jd_file.endswith('.json'):
            with open(os.path.join(jd_dir, jd_file), 'r', encoding='utf-8') as f:
                all_jds.append(json.load(f))
                
    return resumes_combined, all_jds

def main():
    print("Initializing Semantic Matching Engine...")
    resumes, jds = load_data()
    
    # Build corpus for vectorizer
    print("Building corpus and fitting vectorizer...")
    corpus = SemanticEngine.build_corpus(list(resumes.values()), jds)
    engine = SemanticEngine(corpus=corpus)
    
    results = []
    
    # For validation, we'll match all resumes against a selection of diverse JDs
    # or just the first 5 for the report
    sample_jds = jds[:5]
    
    print(f"Running semantic matching for {len(resumes)} resumes against {len(sample_jds)} sample JDs...")
    
    for jd in sample_jds:
        jd_title = jd.get('job_title', 'Unknown')
        for res_name, res_data in resumes.items():
            match_result = engine.calculate_similarity(res_data, jd)
            
            results.append({
                "resume": res_name,
                "job_title": jd_title,
                "score": match_result["total_score"],
                "match_level": match_result["match_level"],
                "skill_sim": match_result["dimensions"]["skill_semantic_overlap"],
                "exp_sim": match_result["dimensions"]["experience_semantic_overlap"]
            })
            
    # Generate Report
    df = pd.DataFrame(results)
    report_path = "semantic_matching_report.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Semantic Matching Accuracy Report\n\n")
        f.write("This report evaluates the performance of the Deep Semantic Matching Engine.\n\n")
        
        f.write("## Method\n")
        f.write("- **Vectorization:** TF-IDF with Unigrams and Bigrams.\n")
        f.write("- **Similarity Measure:** Cosine Similarity.\n")
        f.write("- **Dimensions:** Skills Overlap (45%) and Experience Context (55%).\n\n")
        
        f.write("## Top Matches per Job Description\n")
        for jd_title in df['job_title'].unique():
            f.write(f"### Job: {jd_title}\n")
            top_matches = df[df['job_title'] == jd_title].sort_values(by='score', ascending=False).head(3)
            f.write("| Resume | Total Score | Match Level | Skill Sim | Exp Sim |\n")
            f.write("|--------|-------------|-------------|-----------|---------|\n")
            for _, row in top_matches.iterrows():
                f.write(f"| {row['resume']} | {row['score']:.4f} | {row['match_level']} | {row['skill_sim']:.4f} | {row['exp_sim']:.4f} |\n")
            f.write("\n")
            
        f.write("## Scoring Distribution\n")
        stats = df['score'].describe()
        f.write(f"- **Mean Score:** {stats['mean']:.4f}\n")
        f.write(f"- **Max Score:** {stats['max']:.4f}\n")
        f.write(f"- **Min Score:** {stats['min']:.4f}\n\n")
        
        f.write("## Tuning & Threshold Validation\n")
        f.write("- **Excellent Match (> 0.6):** High semantic alignment across both skills and experience.\n")
        f.write("- **Good Match (0.4 - 0.6):** Strong skills or experience alignment.\n")
        f.write("- **Potential Match (0.2 - 0.4):** Some keyword overlap but weak contextual alignment.\n")
        
    print(f"Matching complete. Report generated at {report_path}")

if __name__ == "__main__":
    main()
