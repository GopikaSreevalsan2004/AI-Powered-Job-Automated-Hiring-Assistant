import os
import json
import re
import uuid

input_dir = r"c:\Users\gopik\OneDrive\Pictures\Desktop\Zecpath\data\job data"
output_dir = r"c:\Users\gopik\OneDrive\Pictures\Desktop\Zecpath\output\jd files"

os.makedirs(output_dir, exist_ok=True)

def parse_jd(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Determine job title from filename
    filename = os.path.basename(filepath)
    title_match = re.match(r'\d+_(.*?)\.txt', filename)
    job_title = title_match.group(1).strip() if title_match else filename.replace('.txt', '')

    data = {
        "job_id": str(uuid.uuid4()),
        "job_title": job_title,
        "company": "Placeholder Company", 
        "location": "Remote", 
        "employment_type": "Full-time", 
        "summary": "",
        "responsibilities": [],
        "requirements": {
            "years_of_experience": {"min": 0, "max": 0},
            "education": []
        },
        "skills_required": [],
        "skills_preferred": [],
        "benefits": [],
        "metadata": {}
    }
    
    current_section = None
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        if "job summary" in lower_line:
            current_section = "summary"
            continue
        elif "key responsibilities" in lower_line or "responsibilities" == lower_line:
            current_section = "responsibilities"
            continue
        elif "required skills" in lower_line or "skills" == lower_line:
            current_section = "skills"
            continue
        elif "qualifications" in lower_line:
            current_section = "qualifications"
            continue
            
        if not current_section:
            continue
            
        # Clean bullet points
        clean_item = re.sub(r'^[\u2022\-\*\s]+', '', line).strip()
        
        if current_section == "summary":
            if data["summary"]:
                data["summary"] += " " + clean_item
            else:
                data["summary"] = clean_item
                
        elif current_section == "responsibilities":
            if clean_item:
                data["responsibilities"].append(clean_item)
                
        elif current_section == "skills":
            if clean_item:
                data["skills_required"].append({"name": clean_item})
                
        elif current_section == "qualifications":
            if clean_item:
                # Predict YOE
                yoe_match = re.search(r'(\d+)(?:\s*(?:-|to|–)\s*(\d+))?\+?\s*years?', clean_item, re.IGNORECASE)
                if yoe_match:
                    min_y = int(yoe_match.group(1))
                    max_y = int(yoe_match.group(2)) if yoe_match.group(2) else min_y
                    data["requirements"]["years_of_experience"] = {"min": min_y, "max": max_y}
                
                data["requirements"]["education"].append(clean_item)

    return data

converted_count = 0
for file in os.listdir(input_dir):
    if file.endswith('.txt'):
        filepath = os.path.join(input_dir, file)
        jd_data = parse_jd(filepath)
        
        json_filename = file.replace('.txt', '.json')
        json_filepath = os.path.join(output_dir, json_filename)
        
        with open(json_filepath, 'w', encoding='utf-8') as jf:
            json.dump(jd_data, jf, indent=2)
            
        converted_count += 1

print(f"Successfully converted {converted_count} files to JSON in {output_dir}")
