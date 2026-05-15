from fastapi import APIRouter, BackgroundTasks
from datetime import datetime
from services.scheduler import run_daily_reporting_job
from services.aws_service import aws_service

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
def trigger_manual_job(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_daily_reporting_job)
    return {"status": "Job triggered successfully", "job_id": f"job-manual-{int(datetime.now().timestamp())}"}

@router.get("/aws-status")
def get_aws_status():
    return aws_service.get_aws_identity()
