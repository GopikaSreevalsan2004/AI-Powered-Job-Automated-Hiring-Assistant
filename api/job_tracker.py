import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from .schemas import JobStatus

class JobTracker:
    def __init__(self):
        # In a real production app, this would be Redis or a Database
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job(self, message: str = "Job queued") -> str:
        job_id = f"job_{uuid.uuid4()}"
        self.jobs[job_id] = {
            "status": JobStatus.QUEUED,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        return job_id

    def update_job(self, job_id: str, status: JobStatus, message: str, result: Any = None, error: str = None):
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status
            self.jobs[job_id]["message"] = message
            self.jobs[job_id]["updated_at"] = datetime.now().isoformat()
            if result is not None:
                self.jobs[job_id]["result"] = result
            if error is not None:
                self.jobs[job_id]["error"] = error

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

# Singleton instance
tracker = JobTracker()
