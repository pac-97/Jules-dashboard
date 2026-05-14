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
        scores_df = self._get_scores_dataframe_from_s3()
        if scores_df is None or scores_df.empty:
            return accounts

        account_col = None
        if 'accountid' in scores_df.columns:
            account_col = 'accountid'
        elif 'account_id' in scores_df.columns:
            account_col = 'account_id'

        if not account_col:
            logger.error("Account ID column not found in scores CSV.")
            return accounts

        for account_id in sorted(scores_df[account_col].dropna().astype(str).unique()):
            accounts.append({
                "id": account_id,
                "name": account_id,
                "email": ""
            })
        return accounts

    def _get_scores_dataframe_from_s3(self) -> Any:
        bucket = "centralized-security-findings"
        key = "all-ac-security-scores/May_benchmark_scores.csv"
        raw_bytes = self._get_s3_object_bytes(key, bucket)
        if not raw_bytes:
            return None

        try:
            df = pd.read_csv(io.BytesIO(raw_bytes))
        except Exception as e:
            logger.error(f"Error reading scores CSV from S3: {e}")
            return None

        df.columns = [str(c).strip().lower() for c in df.columns]
        if 'date' not in df.columns and not df.empty:
            df['date'] = df.iloc[:, 0]

        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        return df

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
        df = self._get_scores_dataframe_from_s3()
        if df is None or df.empty:
            return []

        numeric_columns = [
            'compliance_score',
            'cis_score',
            'nist_score',
            'critical',
            'high',
            'medium',
            'low'
        ]

        for col in numeric_columns:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        df = df.dropna(subset=['date'])
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')

        trend_df = df.groupby('date', as_index=False).agg({
            'compliance_score': 'mean',
            'cis_score': 'mean',
            'nist_score': 'mean',
            'critical': 'sum',
            'high': 'sum',
            'medium': 'sum',
            'low': 'sum'
        })

        trend_data = trend_df.to_dict('records')
        return trend_data

    def get_account_scores_for_accounts(self, account_ids: List[str]) -> Any:
        df = self._get_scores_dataframe_from_s3()
        if df is None or df.empty:
            return pd.DataFrame()

        account_col = None
        if 'accountid' in df.columns:
            account_col = 'accountid'
        elif 'account_id' in df.columns:
            account_col = 'account_id'

        if not account_col:
            logger.error("Account ID column not found in scores CSV.")
            return pd.DataFrame()

        filtered = df[df[account_col].astype(str).isin([str(a) for a in account_ids])].copy()
        return filtered

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

aws_service = AWSService()
