import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.aws_service import aws_service
from services.report_service import report_service
from services.email_service import email_service
from services.owner_service import owner_service
from services.chart_service import chart_service
from datetime import datetime

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def run_daily_reporting_job():
    logger.info("Starting daily security reporting job...")

    # 1. Fetch Findings
    inspector_findings = aws_service.get_inspector_findings()
    cspm_findings = aws_service.get_security_hub_findings()
    trend_data = aws_service.get_s3_historical_data()
    trend_chart = chart_service.generate_trend_chart(trend_data)

    # 2. Get Owners
    owners = owner_service.get_owners()

    for owner in owners:
        owner_email = owner.get("email")
        accounts = owner.get("accounts", [])

        # 3. Filter findings for owner accounts
        owner_inspector = [f for f in inspector_findings if f.get('accountId') in accounts]

        owner_cspm = {
            'compliance_score': cspm_findings.get('compliance_score', 0),
            'cis_score': cspm_findings.get('cis_score', 0),
            'nist_score': cspm_findings.get('nist_score', 0),
            'findings': [f for f in cspm_findings.get('findings', []) if f.get('accountId') in accounts]
        }

        # 4. Generate Reports
        inspector_xlsx = report_service.generate_inspector_report(owner_inspector)
        cspm_xlsx = report_service.generate_cspm_report(owner_cspm)

        # 5. Send Email
        success = email_service.send_owner_report_email(
            owner_email=owner_email,
            accounts=accounts,
            inspector_report=inspector_xlsx,
            cspm_report=cspm_xlsx,
            trend_chart=trend_chart
        )

        if success:
            owner['lastEmailed'] = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    # Update state
    owner_service.update_owners(owners)
    logger.info("Daily security reporting job completed.")

def init_scheduler():
    if not scheduler.running:
        # Schedule to run every day at 8:00 AM
        scheduler.add_job(
            run_daily_reporting_job,
            trigger=CronTrigger(hour=8, minute=0),
            id='daily_reporting',
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler initialized.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shutdown.")
