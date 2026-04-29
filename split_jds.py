import re
import os

filepath = r'c:\Users\gopik\OneDrive\Pictures\Desktop\Zecpath\data\jd.txt\jd.txt'
outdir = r'c:\Users\gopik\OneDrive\Pictures\Desktop\Zecpath\data\job data'

os.makedirs(outdir, exist_ok=True)

with open(filepath, 'r', encoding='utf-8') as f:
    text = f.read()

# Pattern: newline, digits, optional space/newline, optional symbols, dot, space, Title
parts = re.split(r'(?=\b\d+(?:\s*\r?\n\s*)?[^\w\s]*\.\s+[A-Z])', text)

count = 0
for part in parts:
    part = part.strip()
    if not part:
        continue
    
    # Try to extract the title
    match = re.match(r'\b\d+(?:\s*\r?\n\s*)?[^\w\s]*\.\s+([^\r\n]+)', part)
    if match:
        title = match.group(1).strip()
        # Clean up title for filename
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        # Remove any leading/trailing unicode symbols
        safe_title = safe_title.encode('ascii', 'ignore').decode('ascii').strip()
        
        # If it's empty after cleanup, use a generic name
        if not safe_title:
            safe_title = f"jd_{count+1}"
            
        filename = f"{count+1:02d}_{safe_title}.txt"
        
        # Write to file
        with open(os.path.join(outdir, filename), 'w', encoding='utf-8') as out_f:
            out_f.write(part)
        count += 1
    else:
        # What if there is no match? We might have leftover chunks (e.g. section headers)
        pass

print(f"Successfully processed and saved {count} job descriptions into '{outdir}'")
