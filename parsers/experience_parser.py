import re
from datetime import datetime
from typing import List, Dict, Optional
import spacy

class ExperienceParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if model not loaded
            self.nlp = None

    def parse_experience_block(self, text: str) -> List[Dict]:
        """
        Parses a block of text containing multiple experience entries.
        """
        # This is a simplified version. In a real scenario, we'd use NER and complex regex.
        # For this implementation, we will look for patterns of Company, Role, and Dates.
        
        experiences = []
        
        # Split by what looks like new entries (often dates or double newlines)
        # For now, let's assume we use a regex to find date ranges and split around them
        date_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\d{4})\s*[-–—to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{1,2}/\d{4}|\d{4}|Present|Current)'
        
        # Heuristic: split text by lines and try to group
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_exp = {}
        previous_line = ""
        
        for line in lines:
            # Check for dates
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match:
                if current_exp and ('role' in current_exp or 'company' in current_exp):
                    experiences.append(current_exp)
                
                current_exp = {
                    "start_date": date_match.group(1),
                    "end_date": date_match.group(2),
                    "description": ""
                }
                
                # Try to extract role/company from the same line
                remaining_text = line.replace(date_match.group(0), "").strip()
                if remaining_text:
                    parts = re.split(r'[,|–—-]', remaining_text)
                    if len(parts) >= 2:
                        current_exp["role"] = parts[0].strip()
                        current_exp["company"] = parts[1].strip()
                    elif parts[0].strip():
                        current_exp["role"] = parts[0].strip()
                
                # If not found on same line, check previous line
                if "role" not in current_exp and previous_line:
                    parts = re.split(r'[,|–—-]', previous_line)
                    if len(parts) >= 2:
                        current_exp["role"] = parts[0].strip()
                        current_exp["company"] = parts[1].strip()
                    else:
                        current_exp["role"] = previous_line.strip()
            
            elif current_exp:
                # If we don't have a role/company yet, maybe this line has it
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
        Converts various date formats to datetime object.
        """
        if not date_str:
            return None
        
        date_str = date_str.lower().strip()
        if date_str in ["present", "current", "now"]:
            return datetime.now()
        
        formats = [
            "%b %Y", "%B %Y", "%m/%Y", "%Y"
        ]
        
        # Clean string
        date_str = re.sub(r'[^a-z0-9/ ]', '', date_str)
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
