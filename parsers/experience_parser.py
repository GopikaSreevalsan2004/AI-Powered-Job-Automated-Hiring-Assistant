import re
import logging
from datetime import datetime
from typing import List, Dict, Optional

class ExperienceParser:
    """
    Parser to extract professional experience details including company names,
    job titles, and employment durations.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Standard Date Patterns (e.g., Jan 2020 - Mar 2022, 2018 - 2020, 01/2019 - Present)
        months = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
        self.date_pattern_full = re.compile(
            rf'\b({months}\s*\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})[^a-zA-Z0-9]*[-–—to]+[^a-zA-Z0-9]*({months}\s*\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}}|Present|Current|Ongoing|Now)\b',
            re.IGNORECASE
        )
        
        # Special case: "(Ongoing) July 2025" or similar reverse forms
        self.date_pattern_ongoing = re.compile(
            rf'\b(Ongoing|Present|Current)\b[^a-zA-Z0-9]*({months}\s*\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})\b',
            re.IGNORECASE
        )
        
        # Look for single dates (fallback)
        self.date_single = re.compile(rf'\b({months}\s*\d{{4}}|\d{{1,2}}/\d{{4}}|\d{{4}})\b', re.IGNORECASE)

        # Job Titles heuristics
        self.common_titles = ['Engineer', 'Developer', 'Manager', 'Lead', 'Architect', 'Analyst', 'Consultant', 
                              'Scientist', 'Administrator', 'Director', 'Specialist', 'Instructor', 'Researcher', 'Data']
        
    def parse_experience_block(self, text: str) -> List[Dict]:
        experiences = []
        
        # Remove common section prefixes if they accidentally bleed in
        text = re.sub(r'^(?i:EXPERIENCE|WORK EXPERIENCE|INTERNSHIP /EXPERIENCE|EMPLOYMENT HISTORY)\s*', '', text)
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_exp = {}
        
        for idx, line in enumerate(lines):
            # 1. Look for Date Ranges
            date_match = self.date_pattern_full.search(line)
            ongoing_match = self.date_pattern_ongoing.search(line)
            date_single_match = self.date_single.search(line)
            
            # 2. Look for "Role at Company" (Dummy Format)
            at_match = re.search(r'([A-Za-z\s\-&]+)\s+at\s+([A-Za-z\s\-&]+)', line, re.IGNORECASE)
            
            if date_match or ongoing_match or date_single_match or (at_match and len(at_match.group(1).split()) <= 4):
                if current_exp and (current_exp.get('role') or current_exp.get('company')):
                    experiences.append(current_exp)
                
                current_exp = {
                    "start_date": None,
                    "end_date": None,
                    "role": "",
                    "company": "",
                    "description": ""
                }
                
                if date_match:
                    current_exp["start_date"] = date_match.group(1).strip()
                    current_exp["end_date"] = date_match.group(2).strip()
                    
                    remaining = line.replace(date_match.group(0), "").strip()
                    self._extract_role_company(remaining, current_exp)
                    
                    if not current_exp["role"] and not current_exp["company"] and idx > 0:
                        self._extract_role_company(lines[idx-1], current_exp)
                        
                elif ongoing_match:
                    # Ongoing usually implies start date is unknown, end date is "Ongoing"
                    # But if it says "Ongoing July 2025", maybe July 2025 is start date
                    current_exp["start_date"] = ongoing_match.group(2).strip()
                    current_exp["end_date"] = "Ongoing"
                    
                    remaining = line.replace(ongoing_match.group(0), "").strip()
                    # Remove surrounding parens/brackets if any left over
                    remaining = re.sub(r'^[()|\[\]]+|[()|\[\]]+$', '', remaining).strip()
                    self._extract_role_company(remaining, current_exp)
                    
                    if not current_exp["role"] and not current_exp["company"] and idx > 0:
                        self._extract_role_company(lines[idx-1], current_exp)

                elif date_single_match:
                    current_exp["start_date"] = date_single_match.group(1).strip()
                    current_exp["end_date"] = "Present" # Assume present or just a single point in time
                    
                    remaining = line.replace(date_single_match.group(0), "").strip()
                    remaining = re.sub(r'^[()|\[\]]+|[()|\[\]]+$', '', remaining).strip()
                    self._extract_role_company(remaining, current_exp)
                    
                    if not current_exp["role"] and not current_exp["company"] and idx > 0:
                        self._extract_role_company(lines[idx-1], current_exp)

                elif at_match:
                    current_exp["role"] = at_match.group(1).strip()
                    # Clean company (remove anything after period)
                    company = at_match.group(2).split('.')[0].strip()
                    current_exp["company"] = company
                    
                    # Description might be the rest of the line
                    remaining = line[at_match.end():].strip()
                    if remaining.startswith('.'):
                        remaining = remaining[1:].strip()
                    if remaining:
                        current_exp["description"] = remaining
                    
                continue
                
            if current_exp:
                # Try to extract title if missing
                if not current_exp.get("role") and any(title.lower() in line.lower() for title in self.common_titles) and len(line.split()) <= 5:
                    self._extract_role_company(line, current_exp)
                else:
                    if current_exp.get("description"):
                        current_exp["description"] += " " + line
                    else:
                        current_exp["description"] = line
            else:
                # Unmatched line, maybe a standalone title
                if any(title.lower() in line.lower() for title in self.common_titles) and len(line.split()) <= 6:
                    current_exp = {
                        "start_date": None,
                        "end_date": None,
                        "role": "",
                        "company": "",
                        "description": ""
                    }
                    self._extract_role_company(line, current_exp)
        
        if current_exp and (current_exp.get('role') or current_exp.get('company')):
            experiences.append(current_exp)
            
        return experiences
        
    def _extract_role_company(self, text: str, current_exp: Dict):
        text = text.strip()
        if not text:
            return
            
        parts = re.split(r'\s*[|\-–—,]\s*', text)
        if len(parts) >= 2:
            part1, part2 = parts[0].strip(), parts[1].strip()
            
            p1_has_title = any(t.lower() in part1.lower() for t in self.common_titles)
            p2_has_title = any(t.lower() in part2.lower() for t in self.common_titles)
            
            if p2_has_title and not p1_has_title:
                current_exp["role"] = part2
                if not current_exp.get("company"):
                    current_exp["company"] = part1
            else:
                current_exp["role"] = part1
                if not current_exp.get("company"):
                    current_exp["company"] = part2
        else:
            if any(t.lower() in text.lower() for t in self.common_titles):
                current_exp["role"] = text
            else:
                if len(text.split()) <= 3 and not current_exp.get("company"):
                    current_exp["company"] = text

    def normalize_dates(self, date_str: str) -> Optional[datetime]:
        """
        Converts extracted date strings into datetime objects.
        """
        if not date_str:
            return None
        
        date_str = date_str.lower().strip()
        if date_str in ["present", "current", "now", "ongoing"]:
            return datetime.now()
        
        date_str = re.sub(r'[^a-z0-9/ ]', '', date_str)
        
        formats = [
            "%b %Y", "%B %Y", "%m/%Y", "%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
