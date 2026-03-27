import os
import shutil
from typing import List

class FileHandler:
    def __init__(self, resumes_dir: str, processed_dir: str):
        self.resumes_dir = resumes_dir
        self.processed_dir = processed_dir
        self._ensure_dirs()

    def _ensure_dirs(self):
        os.makedirs(self.resumes_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def list_resumes(self) -> List[str]:
        """Returns a list of absolute paths to resume files."""
        files = []
        for filename in os.listdir(self.resumes_dir):
            if filename.lower().endswith(('.pdf', '.docx')):
                files.append(os.path.join(self.resumes_dir, filename))
        return files

    def save_processed(self, filename: str, content: str):
        """Saves cleaned text to the processed directory."""
        # Use only the basename of the file and change extension to .txt
        base_name = os.path.basename(filename)
        file_root = os.path.splitext(base_name)[0]
        output_path = os.path.join(self.processed_dir, f"{file_root}.txt")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return output_path
