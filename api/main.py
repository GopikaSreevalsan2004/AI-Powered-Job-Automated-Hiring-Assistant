import os
import json
import shutil
import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse
from .schemas import (
    ResumeSchema, JobDescriptionSchema, JobResponse, JobStatus, 
    ScoringRequest, ScoringResponse, ShortlistRequest, ShortlistResponse,
    ScoreBreakdown, ScoringByJDRequest
)
from .job_tracker import tracker
from utils.logger import setup_logger
from utils.text_cleaner import TextCleaner
from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DOCXParser
from ats_engine.skill_extractor import SkillExtractionEngine
from ats_engine.master_scorer import MasterScorer
from ats_engine.experience_engine import ExperienceEngine
from ats_engine.education_engine import EducationEngine
from ats_engine.semantic_engine import SemanticEngine
from ats_engine.shortlisting_engine import ShortlistingEngine

# Initialize App
app = FastAPI(
    title="ATS AI Intelligence API",
    description="API for Resume Parsing, Scoring, and Shortlisting",
    version="1.1.0"
)

# Setup Logger
logger = setup_logger("ats_api", log_file="api.log")

# Workers/Engines
pdf_parser = PDFParser(logger=logger)
docx_parser = DOCXParser(logger=logger)
cleaner = TextCleaner()
skill_extractor = SkillExtractionEngine(logger=logger)
experience_engine = ExperienceEngine()
education_engine = EducationEngine()
semantic_engine = SemanticEngine()
shortlisting_engine = ShortlistingEngine()

# Dependency for engines
def get_master_scorer(weights: Dict[str, float] = None):
    return MasterScorer(weights=weights)

# Helper to load JD from disk
def load_jd_from_disk(filename: str) -> Dict:
    jd_path = os.path.join("output", "jd files", filename)
    if not os.path.exists(jd_path):
        if not filename.endswith(".json") and os.path.exists(jd_path + ".json"):
            jd_path += ".json"
        else:
            raise HTTPException(status_code=404, detail=f"JD file '{filename}' not found in output/jd files/")
    
    with open(jd_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- Background Work Modules ---

async def background_process_resume(job_id: str, file_path: str, jd_filename: Optional[str] = None):
    tracker.update_job(job_id, JobStatus.PROCESSING, "Extracting text from file...")
    
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    try:
        if ext == '.pdf':
            raw_text = pdf_parser.extract_text(file_path)
        elif ext == '.docx':
            raw_text = docx_parser.extract_text(file_path)
        
        if not raw_text:
            tracker.update_job(job_id, JobStatus.FAILED, "No text could be extracted", error="PARSING_ERROR")
            return

        tracker.update_job(job_id, JobStatus.PROCESSING, "Cleaning and extracting resume data...")
        cleaned_text = cleaner.clean(raw_text)
        
        # Comprehensive Parsing
        skills = skill_extractor.extract_skills(cleaned_text)
        exp_data = experience_engine.process_experience_text(cleaned_text)
        edu_data = education_engine.process_education_text(cleaned_text)
        
        result = {
            "full_extracted_text": cleaned_text[:2000],
            "skills": skills,
            "experience": exp_data,
            "education": edu_data.model_dump() if hasattr(edu_data, "model_dump") else edu_data,
            "parsing_status": "Successful",
            "hiring_decision": "Not Evaluated (No JD provided)"
        }

        # Optional Scoring if JD provided
        if jd_filename:
            tracker.update_job(job_id, JobStatus.PROCESSING, f"Scoring against JD: {jd_filename}...")
            jd_data = load_jd_from_disk(jd_filename)
            scorer = MasterScorer()
            
            # Simple conversion to ResumeSchema-like dict for perform_scoring
            # Ensure education is a list of dicts
            edu_list = edu_data.education if hasattr(edu_data, "education") else edu_data.get("education", [])
            if isinstance(edu_list, list) and len(edu_list) > 0 and not isinstance(edu_list[0], dict):
                edu_list = [e.model_dump() if hasattr(e, "model_dump") else e.__dict__ for e in edu_list]

            pseudo_resume = {
                "skills": skills,
                "experiences": exp_data.get("structured_experiences", []),
                "education": edu_list,
                "summary": cleaned_text[:500]
            }
            
            score_response = await perform_scoring(pseudo_resume, jd_data, None, scorer)
            result["scoring"] = score_response.model_dump()
            result["hiring_decision"] = score_response.status_zone
        
        tracker.update_job(job_id, JobStatus.COMPLETED, "Processing complete", result=result)
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        tracker.update_job(job_id, JobStatus.FAILED, str(e), error="INTERNAL_ERROR")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# --- Endpoints ---

@app.post("/api/v1/resumes/upload", response_model=JobResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    jd_filename: Optional[str] = None
):
    """Upload a resume for asynchronous parsing and optional scoring against a JD."""
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and DOCX are supported.")
    
    file_id = tracker.create_job(f"File upload accepted. JD: {jd_filename or 'None'}")
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, f"{file_id}_{file.filename}")
    
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    background_tasks.add_task(background_process_resume, file_id, temp_file_path, jd_filename)
    
    return JobResponse(
        job_id=file_id,
        status=JobStatus.QUEUED,
        message="Resume upload successful. Parsing started.",
        check_status_url=f"/api/v1/jobs/{file_id}"
    )

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Retrieve status and results of an async job."""
    job = tracker.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job ID not found")
    return job

async def perform_scoring(resume_data: Dict, jd_data: Dict, weights: Optional[Dict[str, float]], scorer: MasterScorer) -> ScoringResponse:
    """Helper to run the full scoring pipeline."""
    # 1. Process engines with JD context
    req_skills = [s["name"] for s in jd_data.get("skills_required", [])]
    jd_requirements = {
        "required_skills": req_skills, 
        "target_role": jd_data.get("job_title"),
        "minimum_education": jd_data.get("requirements", {}).get("education", ["Bachelor's"])[0] if jd_data.get("requirements", {}).get("education") else "Bachelor's",
        "target_field": jd_data.get("job_title", "") # Simple heuristic
    }
    
    # Experience Scoring using structured data
    experiences = resume_data.get("experiences", [])
    # Normalize keys for the scorer if needed (ResumeSchema uses different keys than ExperienceParser)
    normalized_exps = []
    for exp in experiences:
        normalized_exps.append({
            "role": exp.get("role", ""),
            "company": exp.get("company", ""),
            "description": exp.get("description", ""),
            "start_dt": exp.get("start_date"),
            "end_dt": exp.get("end_date")
        })
    ranked_exps = experience_engine.scorer.rank_experiences(normalized_exps, jd_requirements)
    exp_results = {"structured_experiences": ranked_exps, "analysis": {"total_experience_years": len(experiences) * 2}} # Simple fallback
    
    # Education Scoring using structured data
    edu_list = resume_data.get("education", [])
    edu_score = education_engine.scorer.score_education_relevance(edu_list, jd_requirements)
    edu_results = {"relevance_scoring": {"total_academic_score": edu_score}}
    
    # Semantic Scoring
    sem_results = semantic_engine.calculate_similarity(resume_data, jd_data)
    
    # 2. Master Scorer Final Calculation
    score_results = scorer.calculate_candidate_score(
        skills_data=resume_data.get("skills", []),
        experience_data=exp_results,
        education_data=edu_results,
        semantic_data=sem_results,
        jd_requirements=jd_requirements
    )
    
    # 3. Shortlisting Decision
    shortlist_data = shortlisting_engine.process_rankings({"candidate": score_results})
    shortlisted_info = shortlist_data["all_ranked"][0]
    
    breakdown = score_results["score_breakdown"]
    
    return ScoringResponse(
        match_score=score_results["final_score"] * 100,
        is_shortlisted=shortlisted_info["status_zone"] == "Shortlisted",
        status_zone=shortlisted_info["status_zone"],
        breakdown=ScoreBreakdown(
            skill_score=breakdown["skill_match"]["score"] * 100,
            experience_score=breakdown["experience_relevance"]["score"] * 100,
            education_score=breakdown["education_alignment"]["score"] * 100,
            semantic_similarity=breakdown["semantic_similarity"]["score"] * 100
        ),
        missing_critical_skills=[s for s in req_skills if not any(s.lower() in fs.get("name", "").lower() for fs in resume_data.get("skills", []))],
        recommendation=scorer.generate_explanation_text(score_results)
    )

@app.post("/api/v1/score", response_model=ScoringResponse)
async def score_resume(request: ScoringRequest, scorer: MasterScorer = Depends(get_master_scorer)):
    """Synchronously score a resume against a provided job description."""
    try:
        return await perform_scoring(request.resume_data.model_dump(), request.jd_data.model_dump(), request.weights, scorer)
    except Exception as e:
        logger.error(f"Scoring error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/score/by-jd", response_model=ScoringResponse)
async def score_resume_by_jd(request: ScoringByJDRequest, scorer: MasterScorer = Depends(get_master_scorer)):
    """Synchronously score a resume against a JD file in the output/jd files folder."""
    try:
        jd_data = load_jd_from_disk(request.jd_filename)
        return await perform_scoring(request.resume_data.model_dump(), jd_data, request.weights, scorer)
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Scoring by JD error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
