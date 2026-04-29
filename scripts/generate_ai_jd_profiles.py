import os
import json
import sys

# Ensure the root directory is in the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.jd_parser import JDParser

def main():
    input_dir = r"c:\Users\gopik\OneDrive\Pictures\Desktop\Zecpath\data\job data"
    output_dir = r"c:\Users\gopik\OneDrive\Pictures\Desktop\Zecpath\output\jd_profiles"
    
    os.makedirs(output_dir, exist_ok=True)
    
    parser = JDParser()
    processed_count = 0
    
    print(f"Starting parsing of JDs from '{input_dir}'")
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                raw_text = f.read()
                
            try:
                # Parse the JD
                profile = parser.parse(raw_text, filename=filename)
                
                # Save it
                json_filename = filename.replace('.txt', '.json')
                json_path = os.path.join(output_dir, json_filename)
                
                with open(json_path, 'w', encoding='utf-8') as out_f:
                    json.dump(profile.to_dict(), out_f, indent=2)
                    
                processed_count += 1
            except Exception as e:
                print(f"Error parsing {filename}: {e}")
                
    print(f"Successfully processed and generated {processed_count} AI-friendly JD Profiles in '{output_dir}'.")

if __name__ == "__main__":
    main()
