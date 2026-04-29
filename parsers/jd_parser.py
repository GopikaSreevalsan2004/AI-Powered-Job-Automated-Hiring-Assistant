import re
import os
import uuid
from typing import Dict, Any

from models.job_models import JobRequirementProfile, SkillRequirement, ExperienceRequirement
from utils.text_cleaner import TextCleaner
from utils.synonym_mapper import SynonymMapper

class JDParser:
    """
    Intelligent Job Description parser that converts text to a structured AI-friendly JobRequirementProfile.
    """
    
    def __init__(self):
        self.cleaner = TextCleaner()
        self.synonym_mapper = SynonymMapper()

    def parse(self, raw_text: str, filename: str = "") -> JobRequirementProfile:
        """
        Parses raw text of a job description and extracts fields.
        """
        cleaned_text = self.cleaner.clean(raw_text)
        lines = cleaned_text.split('\n')
        
        profile = JobRequirementProfile(job_id=str(uuid.uuid4()))
        
        # 1. Title Extraction
        if filename:
            title_match = re.match(r'\d+_(.*?)\.txt', os.path.basename(filename))
            profile.job_title = title_match.group(1).strip() if title_match else os.path.basename(filename).replace('.txt', '')
        else:
            profile.job_title = lines[0].strip() if lines else "Unknown Role"
            
        profile.standard_role_name = self.synonym_mapper.normalize_role(profile.job_title)
        
        # 2. Section Parsing
        current_section = None
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
                
            clean_item = re.sub(r'^[\u2022\-\*\s]+', '', line).strip()
            if not clean_item:
                continue
                
            if current_section == "summary":
                if profile.summary:
                    profile.summary += " " + clean_item
                else:
                    profile.summary = clean_item
                    
            elif current_section == "responsibilities":
                profile.responsibilities.append(clean_item)
                
            elif current_section == "skills":
                standard_name = self.synonym_mapper.normalize_skill(clean_item)
                # Guess proficiency from text
                prof = None
                lower_item = clean_item.lower()
                if "expert" in lower_item or "advanced" in lower_item:
                    prof = "Expert"
                elif "intermediate" in lower_item:
                    prof = "Intermediate"
                elif "basic" in lower_item or "familiar" in lower_item:
                    prof = "Beginner"
                
                profile.skills.append(SkillRequirement(
                    name=clean_item,
                    standard_name=standard_name,
                    proficiency=prof,
                    required=True
                ))
                
            elif current_section == "qualifications":
                # Extract YOE
                yoe_match = re.search(r'(\d+)(?:\s*(?:-|to|–)\s*(\d+))?\+?\s*years?', clean_item, re.IGNORECASE)
                if yoe_match:
                    min_y = int(yoe_match.group(1))
                    max_y = int(yoe_match.group(2)) if yoe_match.group(2) else min_y
                    # Take the highest numbers if multiple mentioned
                    if min_y > profile.experience.min_years:
                        profile.experience.min_years = min_y
                        profile.experience.max_years = max_y if max_y > max_y else max_y
                
                # Check for degree keywords
                edu_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma']
                if any(kw in clean_item.lower() for kw in edu_keywords):
                    profile.education.append(clean_item)
                else:
                    # Treat everything else under qualifications as an additional skill or qualification
                    # Add as preferred skill instead to not lose data
                    standard_name = self.synonym_mapper.normalize_skill(clean_item)
                    profile.skills.append(SkillRequirement(
                        name=clean_item,
                        standard_name=standard_name,
                        required=False
                    ))

        return profile
