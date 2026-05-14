import os
import io
import json
import boto3
import logging
import random
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AWSService:
    def __init__(self):
        try:
            # Using boto3.Session() natively inherits AWS SSO profiles when configured via environment
            self.session = boto3.Session(region_name='us-east-1')
            self.inspector_client = self.session.client('inspector2')
            self.securityhub_client = self.session.client('securityhub')
            self.s3_client = self.session.client('s3')
            self.org_client = self.session.client('organizations')
            self.sts_client = self.session.client('sts')
        except Exception as e:
            logger.error(f"Failed to initialize boto3 session/clients: {e}")
            self.inspector_client = None
            self.securityhub_client = None
            self.s3_client = None
            self.org_client = None
            self.sts_client = None

    def get_aws_identity(self) -> Dict[str, str]:
        if not self.sts_client:
            return {"status": "Disconnected", "identity": "No STS Client"}
        try:
            identity = self.sts_client.get_caller_identity()
            return {
                "status": "Connected",
                "account": identity.get("Account"),
                "arn": identity.get("Arn"),
                "userId": identity.get("UserId")
            }
        except Exception as e:
            logger.error(f"Error fetching AWS identity: {e}")
            return {"status": "Error", "identity": str(e)}

    def get_all_accounts(self) -> List[Dict[str, str]]:
        accounts = []
        if self.org_client:
            try:
                paginator = self.org_client.get_paginator('list_accounts')
                for page in paginator.paginate():
                    for account in page.get('Accounts', []):
                        if account.get('Status') == 'ACTIVE':
                            accounts.append({
                                "id": account.get('Id'),
                                "name": account.get('Name'),
                                "email": account.get('Email')
                            })
                if accounts:
                    return accounts
            except self.org_client.exceptions.AccessDeniedException as e:
                logger.error(f"Organizations access denied while fetching AWS accounts: {e}")
            except Exception as e:
                logger.error(f"Error fetching AWS Accounts from Organizations: {e}")

        # Fallback: derive accounts from account report files in S3 if Organizations access is not available.
        return self.get_all_accounts_from_s3()

    def get_all_accounts_from_s3(self) -> List[Dict[str, str]]:
        accounts = []
        if not self.s3_client:
            logger.error("Boto3 S3 client not initialized. Cannot derive account list from S3.")
            return accounts

        bucket = os.getenv("AWS_S3_REPORT_BUCKET", "aws-security-reports")
        prefix = os.getenv("AWS_S3_ACCOUNT_REPORT_PREFIX", "account_reports/")

        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get('Contents', []):
                    key = obj.get('Key', '')
                    filename = os.path.basename(key)
                    if filename.lower().endswith('.xlsx'):
                        account_id = os.path.splitext(filename)[0]
                        accounts.append({
                            "id": account_id,
                            "name": account_id,
                            "email": ""
                        })
        except Exception as e:
            logger.error(f"Error deriving AWS accounts from S3 bucket {bucket} prefix {prefix}: {e}")

        return accounts

    def _get_s3_object_bytes(self, key: str, bucket: str) -> bytes:
        if not self.s3_client:
            logger.error("Boto3 S3 client not initialized. Cannot fetch S3 object.")
            return b""

        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error fetching S3 object {key} from bucket {bucket}: {e}")
            return b""

    def get_s3_historical_data(self) -> List[Dict[str, Any]]:
        bucket = os.getenv("AWS_S3_TRENDS_BUCKET", "centralized-security-findings")
        trend_key = os.getenv("AWS_S3_TRENDS_KEY", "all-ac-security-scores/May_benchmark_scores.csv")
        raw_bytes = self._get_s3_object_bytes(trend_key, bucket)

        if raw_bytes:
            try:
                if trend_key.lower().endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(raw_bytes))
                else:
                    workbook = pd.read_excel(io.BytesIO(raw_bytes), sheet_name=None)
                    if not workbook:
                        return []
                    df = workbook.get('Sheet1') or next(iter(workbook.values()))

                if df is None or df.empty:
                    return []

                df.columns = [str(c).lower() for c in df.columns]
                if 'date' not in df.columns:
                    df['date'] = df.iloc[:, 0]

                df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
                trend_data = []
                for _, row in df.iterrows():
                    trend_data.append({
                        'date': row.get('date'),
                        'compliance_score': float(row.get('compliance_score', 0) or 0),
                        'cis_score': float(row.get('cis_score', 0) or 0),
                        'nist_score': float(row.get('nist_score', 0) or 0),
                        'critical': int(row.get('critical', 0) or 0),
                        'high': int(row.get('high', 0) or 0),
                        'medium': int(row.get('medium', 0) or 0),
                        'low': int(row.get('low', 0) or 0)
                    })
                return trend_data
            except Exception as e:
                logger.error(f"Error parsing trend data from S3: {e}")

        # Fallback to JSON data if XLSX does not exist.
        json_key = os.getenv("AWS_S3_TRENDS_JSON_KEY", "findings_count_trends.json")
        if not self.s3_client:
            return []

        try:
            response = self.s3_client.get_object(Bucket=os.getenv("AWS_S3_TRENDS_BUCKET", "aws-security-historical-findings"), Key=json_key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            return data
        except Exception as e:
            logger.error(f"Error fetching JSON trend data from S3: {e}")
            return []

    def download_account_reports(self, account_ids: List[str]) -> Dict[str, bytes]:
        reports: Dict[str, bytes] = {}
        if not self.s3_client:
            logger.error("Boto3 S3 client not initialized. Cannot fetch account reports from S3.")
            return reports

        bucket = os.getenv("AWS_S3_REPORT_BUCKET", "aws-security-reports")
        template = os.getenv("AWS_S3_ACCOUNT_REPORT_KEY_TEMPLATE", "account_reports/{account_id}.xlsx")

        for account_id in account_ids:
            key = template.format(account_id=account_id)
            report_bytes = self._get_s3_object_bytes(key, bucket)
            if report_bytes:
                reports[account_id] = report_bytes
            else:
                logger.warning(f"Account report XLSX not found for account {account_id} in S3 key {key}")

        return reports

    def get_inspector_findings(self) -> List[Dict[str, Any]]:
        findings = []
        if not self.inspector_client:
            logger.error("Boto3 Inspector client not initialized. Cannot fetch real data.")
            return findings

        try:
            paginator = self.inspector_client.get_paginator('list_findings')
            for page in paginator.paginate(
                filterCriteria={
                    'findingStatus': [{'comparison': 'EQUALS', 'value': 'ACTIVE'}]
                }
            ):
                for finding in page.get('findings', []):
                    findings.append({
                        'id': finding.get('findingArn'),
                        'accountId': finding.get('awsAccountId'),
                        'severity': finding.get('severity'),
                        'resourceType': finding.get('resources', [{}])[0].get('type'),
                        'findingType': finding.get('type'),
                        'region': finding.get('resources', [{}])[0].get('region'),
                        'status': finding.get('status'),
                        'cveId': finding.get('packageVulnerabilityDetails', {}).get('vulnerabilityId'),
                        'createdAt': finding.get('firstObservedAt', datetime.now()).isoformat()
                    })
        except Exception as e:
            logger.error(f"Error fetching real Inspector findings: {e}")

        return findings

    def get_security_hub_findings(self) -> Dict[str, Any]:
        result = {
            'compliance_score': 0.0,
            'cis_score': 0.0,
            'nist_score': 0.0,
            'failed_controls': 0,
            'passed_controls': 0,
            'findings': []
        }

        if not self.securityhub_client:
            logger.error("Boto3 SecurityHub client not initialized. Cannot fetch real data.")
            return result

        try:
            # 1. Fetch Standards Subscriptions to calculate overall posture
            cis_failed = 0
            cis_passed = 0
            nist_failed = 0
            nist_passed = 0

            # Using Security Hub get_findings without restricting to FAILED so we can tally PASSED too.
            # Filtering for ACTIVE records that have a compliance status.
            paginator = self.securityhub_client.get_paginator('get_findings')
            for page in paginator.paginate(
                Filters={
                    'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}],
                }
            ):
                for finding in page.get('Findings', []):
                    comp_status = finding.get('Compliance', {}).get('Status')
                    if comp_status not in ['PASSED', 'FAILED', 'WARNING', 'NOT_AVAILABLE']:
                        continue

                    standards = str(finding.get('Compliance', {}).get('RelatedRequirements', []))

                    if comp_status == 'PASSED':
                        result['passed_controls'] += 1
                        if 'CIS' in standards: cis_passed += 1
                        if 'NIST' in standards: nist_passed += 1
                    elif comp_status == 'FAILED':
                        result['failed_controls'] += 1
                        if 'CIS' in standards: cis_failed += 1
                        if 'NIST' in standards: nist_failed += 1

                        # Only attach failed controls to the detailed list to avoid massive payloads
                        result['findings'].append({
                            'accountId': finding.get('AwsAccountId'),
                            'controlId': finding.get('Compliance', {}).get('SecurityControlId', 'N/A'),
                            'title': finding.get('Title'),
                            'status': comp_status,
                            'severity': finding.get('Severity', {}).get('Label')
                        })

            # 2. Calculate percentages
            total_controls = result['passed_controls'] + result['failed_controls']
            if total_controls > 0:
                result['compliance_score'] = round((result['passed_controls'] / total_controls) * 100, 1)

            total_cis = cis_passed + cis_failed
            if total_cis > 0:
                result['cis_score'] = round((cis_passed / total_cis) * 100, 1)

            total_nist = nist_passed + nist_failed
            if total_nist > 0:
                result['nist_score'] = round((nist_passed / total_nist) * 100, 1)

        except Exception as e:
            logger.error(f"Error fetching real SecurityHub findings: {e}")

        return result

    def get_s3_historical_data(self) -> List[Dict[str, Any]]:
        if not self.s3_client:
            logger.error("Boto3 S3 client not initialized. Cannot fetch real data.")
            return []

        try:
            import json
            bucket = os.getenv("AWS_S3_TRENDS_BUCKET", "aws-security-historical-findings")
            key = "findings_count_trends.json"
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            logger.info(f"Successfully retrieved historical trend data from S3 bucket {bucket}.")
            return data
        except Exception as e:
            logger.error(f"Error fetching real S3 historical data: {e}")
            return []

aws_service = AWSService()
