from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.aws_service import aws_service
from services.report_service import report_service
from services.email_service import email_service
from services.chart_service import chart_service
from services.email_log_service import email_log_service
from services.owner_service import owner_service
from datetime import datetime

router = APIRouter()

class EmailSendRequest(BaseModel):
    to: str
    cc: Optional[str] = ""
    subject: str
    body: str
    accounts: List[str]

@router.get("/logs")
def get_email_logs():
    return email_log_service.get_logs()

@router.post("/send")
def send_custom_email(req: EmailSendRequest):
    try:
        # 1. Fetch Findings
        inspector_findings = aws_service.get_inspector_findings()
        cspm_findings = aws_service.get_security_hub_findings()
        trend_data = aws_service.get_s3_historical_data()
        trend_chart = chart_service.generate_trend_chart(trend_data)

        # 2. Filter findings for the accounts
        owner_inspector = [f for f in inspector_findings if f.get('accountId') in req.accounts]

        owner_cspm = {
            'compliance_score': cspm_findings.get('compliance_score', 0),
            'cis_score': cspm_findings.get('cis_score', 0),
            'nist_score': cspm_findings.get('nist_score', 0),
            'findings': [f for f in cspm_findings.get('findings', []) if f.get('accountId') in req.accounts]
        }

        # 2b. Build account report from the single shared S3 scores sheet
        account_scores_df = aws_service.get_account_scores_for_accounts(req.accounts)
        merged_account_report = report_service.generate_account_report_from_scores(account_scores_df)
        account_summary = report_service.summarize_account_scores(account_scores_df)

        # 3. Generate Reports
        inspector_xlsx = report_service.generate_inspector_report(owner_inspector)
        cspm_xlsx = report_service.generate_cspm_report(owner_cspm)

        # 4. Send Email
        extended_body = req.body or ""
        if account_summary.get('accounts'):
            extended_body += "<br><br><strong>Included Account Reports:</strong> " + ", ".join(account_summary['accounts'])
            extended_body += f"<br><strong>Total findings from account XLSX:</strong> {account_summary.get('findings', 0)}"

        success = email_service.send_owner_report_email(
            owner_email=req.to,
            accounts=req.accounts,
            inspector_report=inspector_xlsx,
            cspm_report=cspm_xlsx,
            account_report=merged_account_report,
            trend_chart=trend_chart,
            subject=req.subject,
            body=extended_body,
            cc=req.cc
        )

        # 5. Log Result
        status = "SUCCESS" if success else "FAILED"
        email_log_service.add_log(
            to=req.to,
            cc=req.cc,
            subject=req.subject,
            body=req.body,
            status=status,
            accounts=req.accounts
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send email.")

        # Update owner lastEmailed state if it matches an owner
        owners = owner_service.get_owners()
        for o in owners:
            if o.get("email") == req.to:
                o["lastEmailed"] = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        owner_service.update_owners(owners)

        return {"status": "success", "message": "Email sent and logged successfully"}

    except Exception as e:
        email_log_service.add_log(
            to=req.to,
            cc=req.cc,
            subject=req.subject,
            body=req.body,
            status=f"ERROR: {str(e)}",
            accounts=req.accounts
        )
        raise HTTPException(status_code=500, detail=str(e))
