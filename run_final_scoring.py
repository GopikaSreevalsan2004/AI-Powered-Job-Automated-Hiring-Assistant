import os
import json
import pandas as pd
from ats_engine.master_scorer import MasterScorer
from ats_engine.semantic_engine import SemanticEngine

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
    
    # 4. Semantic (We'll re-calculate for the target JD)
    # We need to build the corpus first
    jd_dir = 'output/jd files'
    all_jds = []
    for jd_file in os.listdir(jd_dir):
        if jd_file.endswith('.json'):
            with open(os.path.join(jd_dir, jd_file), 'r', encoding='utf-8') as f:
                all_jds.append(json.load(f))
    
    # Combine resume data for corpus
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
    print("Loading all processed candidate data...")
    all_exp, all_edu, all_skills, all_jds, semantic_engine = load_all_data()
    
    # Choose a target JD (e.g., Big Data Engineer)
    target_jd = all_jds[0] # 01_Big Data Engineer.json
    print(f"Target Role: {target_jd['job_title']}")
    
    # Extract requirements for skill match
    jd_reqs = {
        "required_skills": [s['name'] for s in target_jd['skills_required']]
    }
    
    # Custom weights for this role (e.g. prioritize experience and skills)
    role_weights = {
        "skill_match": 0.40,
        "experience_relevance": 0.30,
        "education_alignment": 0.10,
        "semantic_similarity": 0.20
    }
    
    scorer = MasterScorer(weights=role_weights)
    final_results = {}
    
    print(f"Generating explainable scores for {len(all_exp)} candidates...")
    
    for res_name in all_exp.keys():
        # Get individual components
        exp_data = all_exp[res_name]
        edu_data = all_edu.get(res_name, {})
        skills_data = all_skills.get(res_name, [])
        
        # Calculate semantic score
        res_data_for_sem = {
            "structured_experiences": exp_data.get("structured_experiences", []),
            "skills": skills_data
        }
        sem_result = semantic_engine.calculate_similarity(res_data_for_sem, target_jd)
        
        # Final Master Score
        master_output = scorer.calculate_candidate_score(
            skills_data, exp_data, edu_data, sem_result, jd_reqs
        )
        
        # Add human-readable explanation
        master_output["explanation"] = scorer.generate_explanation_text(master_output)
        
        final_results[res_name] = master_output

    # Save to JSON
    output_path = 'data/processed/candidate_final_scores.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, indent=4)
        
    # Generate Summary MD
    summary_path = "candidate_scoring_report.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"# Candidate Scoring Report: {target_jd['job_title']}\n\n")
        f.write("## Configurable Weights\n")
        f.write(f"- Skill Match: {role_weights['skill_match']*100}%\n")
        f.write(f"- Experience: {role_weights['experience_relevance']*100}%\n")
        f.write(f"- Education: {role_weights['education_alignment']*100}%\n")
        f.write(f"- Semantic: {role_weights['semantic_similarity']*100}%\n\n")
        
        f.write("## Ranked Candidates\n")
        f.write("| Rank | Candidate | Score | Summary |\n")
        f.write("|------|-----------|-------|---------|\n")
        
        # Sort by final score
        ranked = sorted(final_results.items(), key=lambda x: x[1]['final_score'], reverse=True)
        for i, (name, data) in enumerate(ranked):
            f.write(f"| {i+1} | {name} | {data['final_score']*100:.1f} | {data['explanation']} |\n")
            
    print(f"\nFinal scores generated. Results saved to: {output_path}")
    print(f"Summary report generated at: {summary_path}")

if __name__ == "__main__":
    main()
