from fastapi import APIRouter
from services.aws_service import aws_service

router = APIRouter()

@router.get("/executive-summary")
def get_executive_summary():
    return aws_service.get_dashboard_summary_from_scores()

@router.get("/trends")
def get_trends():
    return aws_service.get_s3_historical_data()
