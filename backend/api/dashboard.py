from fastapi import APIRouter
from services.aws_service import aws_service

router = APIRouter()

@router.get("/executive-summary")
def get_executive_summary():
    cspm = aws_service.get_security_hub_findings()
    findings = aws_service.get_inspector_findings()

    critical_count = len([f for f in findings if f.get('severity') == 'CRITICAL'])
    high_count = len([f for f in findings if f.get('severity') == 'HIGH'])

    return {
        "total_findings": len(findings),
        "critical_findings": critical_count,
        "high_findings": high_count,
        "compliance_score": cspm.get("compliance_score"),
        "cis_score": cspm.get("cis_score"),
        "nist_score": cspm.get("nist_score")
    }

@router.get("/trends")
def get_trends():
    return aws_service.get_s3_historical_data()
