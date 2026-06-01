import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
        
        # 1. Strip common PDF artifacts and watermarks
        text = re.sub(r'(Page \d+ of \d+|Confidential|Resume of .*|www\..*\.com)', '', text, flags=re.IGNORECASE)
        
        # 2. Normalize encoding and remove non-printable characters
        text = text.encode('ascii', 'ignore').decode('ascii') # Force ASCII for stability
        
        # 3. Normalize whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # 4. Remove special noise symbols but keep separators
        text = re.sub(r'[^\w\s.,;:|&+/@#$%()\-•●○\*]', '', text)
        
        # 5. Standardize capitalization for common headings
        headings = ["SKILLS", "EDUCATION", "EXPERIENCE", "PROJECTS", "CERTIFICATIONS", "SUMMARY", "CONTACT", "WORK HISTORY"]
        for heading in headings:
            pattern = rf'(?i)\b{heading}\b'
            text = re.sub(pattern, heading, text)
            
        return text.strip()

    @staticmethod
    def standardize_headings(text: str) -> str:
        """
        Ensures headings are on their own lines or clearly demarcated.
        This helps downstream parsers align with the JSON schema.
        """
        headings = ["SKILLS", "EDUCATION", "EXPERIENCE", "PROJECTS", "CERTIFICATIONS", "SUMMARY", "CONTACT"]
        for heading in headings:
            pattern = rf'({heading})'
            text = re.sub(pattern, r'\n\1\n', text)
        
        # Clean up any double newlines introduced
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text
