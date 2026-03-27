import pytest
import os
from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DOCXParser
from utils.text_cleaner import TextCleaner


def test_text_cleaner_basic():
    cleaner = TextCleaner()
    dirty_text = "  Hello   World!!!  \n\n  This is  a test.  "
    cleaned = cleaner.clean(dirty_text)
    assert cleaned == "Hello World!!! This is a test."

def test_text_cleaner_headings():
    cleaner = TextCleaner()
    text = "skills education experience"
    cleaned = cleaner.clean(text)
    # Heading standardization (case normalization)
    assert "SKILLS" in cleaned
    assert "EDUCATION" in cleaned
    assert "EXPERIENCE" in cleaned

def test_text_cleaner_standardize_headings():
    cleaner = TextCleaner()
    text = "SKILLS Python, Java EDUCATION University of X"
    standardized = cleaner.standardize_headings(text)
    assert "\nSKILLS\n" in standardized
    assert "\nEDUCATION\n" in standardized

def test_pdf_parser_nonexistent():
    parser = PDFParser()
    assert parser.extract_text("nonexistent.pdf") == ""

def test_docx_parser_nonexistent():
    parser = DOCXParser()
    assert parser.extract_text("nonexistent.docx") == ""
