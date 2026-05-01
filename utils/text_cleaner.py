import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""
        
        # Normalize whitespace (replace multiple spaces/newlines with single ones)
        text = re.sub(r'\s+', ' ', text)
        
        # Remove non-printable characters and noise symbols
        # Keeping basic punctuation and common resume symbols like bullets
        text = re.sub(r'[^\x20-\x7E\s•●○\-\*]', '', text)
        
        # Standardize capitalization for common headings
        headings = ["SKILLS", "EDUCATION", "EXPERIENCE", "PROJECTS", "CERTIFICATIONS", "SUMMARY", "CONTACT"]
        for heading in headings:
            # Match heading at start or after a period/newline
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
