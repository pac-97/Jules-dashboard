from fastapi import APIRouter
from services.aws_service import aws_service

router = APIRouter()

@router.get("/inspector")
def get_inspector_findings():
    return aws_service.get_inspector_findings()

@router.get("/cspm")
def get_cspm_findings():
    return aws_service.get_security_hub_findings()

@router.get("/account-details/{account_id}")
def get_account_details(account_id: str):
    """Fetch findings count and security scores for a specific account"""
    scores_df = aws_service._get_scores_dataframe_from_s3()
    if scores_df is None or scores_df.empty:
        return {
            "account_id": account_id,
            "findings_count": 0,
            "cis_score": 0,
            "nist_score": 0,
            "compliance_score": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    
    # Find account column
    account_col = None
    for candidate in ['accountid', 'account_id', 'acctid']:
        if candidate in scores_df.columns:
            account_col = candidate
            break
    
    if not account_col:
        return {
            "account_id": account_id,
            "findings_count": 0,
            "cis_score": 0,
            "nist_score": 0,
            "compliance_score": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    
    # Filter by account ID
    account_df = scores_df[scores_df[account_col].astype(str) == str(account_id)]
    
    if account_df.empty:
        return {
            "account_id": account_id,
            "findings_count": 0,
            "cis_score": 0,
            "nist_score": 0,
            "compliance_score": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
    
    # Get latest record for this account (most recent date)
    if 'date' in account_df.columns:
        account_df = account_df.sort_values('date', ascending=False).iloc[0:1]
    else:
        account_df = account_df.iloc[0:1]
    
    record = account_df.iloc[0]
    
    findings_count = int(record.get('critical', 0)) + int(record.get('high', 0)) + int(record.get('medium', 0)) + int(record.get('low', 0))
    
    return {
        "account_id": account_id,
        "findings_count": findings_count,
        "cis_score": float(record.get('cis_score', 0) or 0),
        "nist_score": float(record.get('nist_score', 0) or 0),
        "compliance_score": float(record.get('compliance_score', 0) or 0),
        "critical": int(record.get('critical', 0) or 0),
        "high": int(record.get('high', 0) or 0),
        "medium": int(record.get('medium', 0) or 0),
        "low": int(record.get('low', 0) or 0)
    }
