import os
import glob
import json
from ats_engine.skill_extractor import SkillExtractionEngine

def main():
    processed_dir = os.path.join("data", "processed")
    output_dir = os.path.join("data", "extracted_skills")
    os.makedirs(output_dir, exist_ok=True)
    
    txt_files = glob.glob(os.path.join(processed_dir, "*.txt"))
    if not txt_files:
        print(f"No .txt files found in {processed_dir}")
        return
        
    print("Loading Skill Extraction Engine (this may take a few seconds)...")
    extractor = SkillExtractionEngine()
    
    report_data = []
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        print(f"Extracting skills from {filename}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        skills = extractor.extract_skills(text)
        
        # Save structured JSON
        out_path = os.path.join(output_dir, filename.replace(".txt", "_skills.json"))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(skills, f, indent=4)
            
        # Collect for report
        skill_names = [s["name"] for s in skills]
        report_data.append({
            "filename": filename,
            "total_skills": len(skills),
            "top_skills": skill_names[:5] # top 5 by confidence
        })
        
    # Generate summary report
    report_path = "skill_extraction_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Skill Extraction Report\n\n")
        f.write("Summary of skills extracted from processed resumes using the NLP engine.\n\n")
        
        f.write("## Results per Resume\n")
        f.write("| Resume File | Total Skills Found | Top Confidence Skills |\n")
        f.write("|-------------|--------------------|-----------------------|\n")
        
        for rd in report_data:
            top_str = ", ".join(rd["top_skills"])
            f.write(f"| {rd['filename']} | {rd['total_skills']} | {top_str} |\n")
            
    print(f"\nSuccessfully processed {len(txt_files)} resumes.")
    print(f"Structured skill JSONs saved to: {output_dir}")
    print(f"Summary report generated at: {report_path}")

if __name__ == '__main__':
    main()
