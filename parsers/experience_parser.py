import re
from datetime import datetime
from typing import List, Dict, Optional

class ExperienceParser:
    """
    Parser to extract professional experience details including company names,
    job titles, and employment durations.
    """
    def __init__(self):
        pass

    def parse_experience_block(self, text: str) -> List[Dict]:
        """
        Parses a block of text containing multiple experience entries.
        Returns a list of structured experience dictionaries.
        """
        experiences = []
        
        # Simple date pattern: Jan 2020 - Present, 01/2018 - 12/2019, 2015 to 2017
        date_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\d{4}|Present|Current)'
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_exp = {}
        previous_line = ""
        
        for line in lines:
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            
            # Simple "Role at Company" pattern
            at_match = re.search(r'([A-Za-z\s]+)\s+at\s+([A-Za-z\s]+)', line, re.IGNORECASE)
            
            if date_match:
                if current_exp and ('role' in current_exp or 'company' in current_exp):
                    experiences.append(current_exp)
                
                current_exp = {
                    "start_date": date_match.group(1).strip(),
                    "end_date": date_match.group(2).strip(),
                    "description": ""
                }
                
                # Extract role/company
                remaining_text = line.replace(date_match.group(0), "").strip()
                if remaining_text:
                    parts = re.split(r'[,|–—-]', remaining_text)
                    if len(parts) >= 2:
                        current_exp["role"] = parts[0].strip()
                        current_exp["company"] = parts[1].strip()
                    elif parts[0].strip():
                        current_exp["role"] = parts[0].strip()
                
                # Check previous line if role is missing
                if "role" not in current_exp and previous_line:
                    parts = re.split(r'[,|–—-]', previous_line)
                    if len(parts) >= 2:
                        current_exp["role"] = parts[0].strip()
                        current_exp["company"] = parts[1].strip()
                    else:
                        current_exp["role"] = previous_line.strip()
                        
            elif at_match and not date_match:
                # Fallback for "Role at Company" format
                if current_exp and ('role' in current_exp or 'company' in current_exp):
                    experiences.append(current_exp)
                
                current_exp = {
                    "start_date": None,
                    "end_date": None,
                    "role": at_match.group(1).strip(),
                    "company": at_match.group(2).split('.')[0].strip(), # split at dot if there is a sentence end
                    "description": ""
                }
            
            elif current_exp:
                if "role" not in current_exp:
                    parts = re.split(r'[,|–—-]', line)
                    if len(parts) >= 2:
                        current_exp["role"] = parts[0].strip()
                        current_exp["company"] = parts[1].strip()
                    else:
                        current_exp["role"] = line
                else:
                    current_exp["description"] += line + " "
            
            previous_line = line

        if current_exp and ('role' in current_exp or 'company' in current_exp):
            experiences.append(current_exp)
            
        return experiences

    def normalize_dates(self, date_str: str) -> Optional[datetime]:
        """
        Converts extracted date strings into datetime objects.
        """
        if not date_str:
            return None
        
        date_str = date_str.lower().strip()
        if date_str in ["present", "current", "now"]:
            return datetime.now()
        
        formats = [
            "%b %Y", "%B %Y", "%m/%Y", "%Y"
        ]
        
        date_str = re.sub(r'[^a-z0-9/ ]', '', date_str)
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
