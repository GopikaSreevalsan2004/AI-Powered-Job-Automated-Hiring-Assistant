# ATS Troubleshooting Guide

This document lists common issues, their causes, and how to resolve them when working with the ATS system.

## 1. Parsing & Extraction Issues

### ❌ Symptom: Resume text is garbled or empty
- **Cause**: The PDF/DOCX might be image-based (scanned) rather than text-based.
- **Solution**: Ensure the input files have selectable text. If scanning is required, integrate an OCR engine (e.g., Tesseract) into `parsers/pdf_parser.py`.
- **Cause**: Unsupported file format.
- **Solution**: Currently only `.pdf` and `.docx` are supported. Check the file extension.

### ❌ Symptom: Skills or Experience sections are not detected
- **Cause**: Non-standard headings in the resume (e.g., "Where I've Been" instead of "Experience").
- **Solution**: Add the non-standard heading to the `HEADING_MAP` in `parsers/resume_classifier.py`.

## 2. Scoring & Accuracy Issues

### ❌ Symptom: Match score is 0% even for valid candidates
- **Cause**: The Job Description (JD) might be missing "Required Skills".
- **Solution**: Verify the JD JSON has a `required_skills` list. The `SkillEngine` relies on this for the baseline.
- **Cause**: Mismatch in date formatting in the experience section.
- **Solution**: Check `utils/text_cleaner.py` and ensure the regex for date extraction handles the specific format used in the resume.

### ❌ Symptom: Semantic score is unusually low
- **Cause**: Very short JD or Resume text.
- **Solution**: Semantic matching works best with at least 50-100 words of context.

## 3. API & Development Environment

### ❌ Symptom: `ModuleNotFoundError`
- **Cause**: Working directory issues or missing dependencies.
- **Solution**: Ensure you are running commands from the root directory and that the `venv` is active. Run `pip install -r requirements.txt`.

### ❌ Symptom: Async jobs never complete
- **Cause**: The background worker is not running or `api/job_tracker.py` cannot write to the state store.
- **Solution**: Check file permissions in the project directory. If using a separate worker process, ensure it is started.

## 4. Logging & Debugging

- **Verbose Logging**: Set the environment variable `LOG_LEVEL=DEBUG` to see detailed tracebacks for every parsing step.
- **Temporary Files**: Check the `temp_uploads/` directory to see the raw files being processed (note: these are deleted after parsing in production).

---

> [!TIP]
> If you encounter a new issue, please document it here along with the "Fix" to help other developers.
