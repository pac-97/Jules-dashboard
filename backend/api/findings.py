from fastapi import APIRouter
from services.aws_service import aws_service

router = APIRouter()

@router.get("/inspector")
def get_inspector_findings():
    return aws_service.get_inspector_findings()

@router.get("/cspm")
def get_cspm_findings():
    return aws_service.get_security_hub_findings()
