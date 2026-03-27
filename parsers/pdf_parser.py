import pdfplumber
import os

class PDFParser:
    def __init__(self, logger=None):
        self.logger = logger

    def extract_text(self, pdf_path: str) -> str:
        """Extracts text from a PDF, handling multi-page and tables."""
        if not os.path.exists(pdf_path):
            if self.logger:
                self.logger.error(f"File not found: {pdf_path}")
            return ""

        full_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    # 1. Extract tables first and format them as text
                    tables = page.extract_tables()
                    table_text = ""
                    for table in tables:
                        for row in table:
                            # Filter None and join cells with tab or pipe
                            row_str = " | ".join([str(cell).strip() if cell else "" for cell in row])
                            table_text += row_str + "\n"
                    
                    # 2. Extract regular text (pdfplumber handles multi-column reasonably well)
                    page_text = page.extract_text()
                    
                    if page_text:
                        full_text.append(f"--- Page {i+1} ---\n{page_text}")
                    if table_text:
                        full_text.append(f"--- Page {i+1} Tables ---\n{table_text}")
            
            return "\n\n".join(full_text)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return ""
