import pdfplumber
import os

class PDFParser:
    def __init__(self, logger=None):
        self.logger = logger

    def extract_text(self, pdf_path: str, fast_mode: bool = False) -> str:
        """
        Extracts text from a PDF. 
        fast_mode=True skips table extraction for significant speed gains.
        """
        if not os.path.exists(pdf_path):
            if self.logger:
                self.logger.error(f"File not found: {pdf_path}")
            return ""

        full_text = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        full_text.append(f"--- Page {i+1} ---\n{page_text}")
                    
                    # Skip tables in fast mode or if not present
                    if not fast_mode:
                        tables = page.extract_tables()
                        if tables:
                            table_text = ""
                            for table in tables:
                                for row in table:
                                    row_str = " | ".join([str(cell).strip() if cell else "" for cell in row if cell])
                                    if row_str.strip():
                                        table_text += row_str + "\n"
                            if table_text.strip():
                                full_text.append(f"--- Page {i+1} Tables ---\n{table_text}")
            
            return "\n\n".join(full_text)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing PDF {pdf_path}: {e}")
            return ""
