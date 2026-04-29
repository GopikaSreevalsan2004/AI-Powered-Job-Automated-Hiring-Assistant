import os
import glob
import json
from parsers.resume_classifier import ResumeSectionClassifier

def main():
    processed_dir = os.path.join("data", "processed")
    output_dir = os.path.join("data", "labeled_resumes")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all txt files
    txt_files = glob.glob(os.path.join(processed_dir, "*.txt"))
    
    if not txt_files:
        print("No .txt files found in data/processed/")
        return
        
    classifier = ResumeSectionClassifier()
    
    report_data = []
    
    for file_path in txt_files:
        filename = os.path.basename(file_path)
        print(f"Processing {filename}...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        sections = classifier.classify_lines(text)
        
        # Save labeled output
        out_path = os.path.join(output_dir, filename.replace(".txt", "_labeled.json"))
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=4)
            
        # Collect data for report
        found_sections = [s["label"] for s in sections]
        report_data.append({
            "filename": filename,
            "sections_found": list(set(found_sections)), # unique sections
            "total_blocks": len(sections)
        })
        
    # Generate accuracy report
    report_path = "section_detection_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Resume Section Detection Accuracy Report\n\n")
        f.write("This report summarizes the sections detected in each processed resume.\n\n")
        
        # Summary statistics
        all_detected_sections = []
        for rd in report_data:
            all_detected_sections.extend(rd["sections_found"])
            
        from collections import Counter
        section_counts = Counter(all_detected_sections)
        
        f.write("## Overall Section Detection Rates\n")
        f.write("| Section | Resumes Containing Section | % of Total Resumes |\n")
        f.write("|---------|----------------------------|--------------------|\n")
        total_resumes = len(txt_files)
        for sec, count in section_counts.most_common():
            percentage = (count / total_resumes) * 100
            f.write(f"| {sec} | {count} | {percentage:.1f}% |\n")
            
        f.write("\n## Breakdown by Resume\n")
        f.write("| Resume File | Detected Sections | Total Sections Blocks |\n")
        f.write("|-------------|-------------------|-----------------------|\n")
        for rd in report_data:
            sections_str = ", ".join(rd["sections_found"])
            f.write(f"| {rd['filename']} | {sections_str} | {rd['total_blocks']} |\n")
            
    print(f"\nCompleted processing {len(txt_files)} resumes.")
    print(f"Labeled outputs saved to: {output_dir}")
    print(f"Report generated at: {report_path}")

if __name__ == '__main__':
    main()
