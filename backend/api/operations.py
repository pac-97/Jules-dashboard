from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/jobs")
def get_jobs_history():
    return [
        {
            "id": "job-1",
            "type": "Daily Fetch & Notify",
            "status": "SUCCESS",
            "startedAt": datetime.now().isoformat(),
            "duration": "120s"
        },
        {
            "id": "job-2",
            "type": "Manual Trigger",
            "status": "FAILED",
            "startedAt": datetime.now().isoformat(),
            "duration": "15s"
        }
    ]

@router.post("/trigger-job")
def trigger_manual_job():
    return {"status": "Job triggered successfully", "job_id": "job-3"}
