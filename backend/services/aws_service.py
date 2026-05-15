import os
import boto3
import logging
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AWSService:
    def __init__(self):
        try:
            # Check default chain and IAM instance metadata service first (works natively on EC2)
            self.session = boto3.Session(region_name='us-east-1')

            # Test credentials
            sts = self.session.client('sts')
            sts.get_caller_identity()
            logger.info("Successfully authenticated via standard boto3 credential chain.")

        except Exception as e:
            logger.warning(f"Standard authentication failed: {e}. Falling back to AWS SSO lib.")
            try:
                import aws_sso_lib
                profile = os.getenv('AWS_PROFILE', 'default')
                logger.info(f"Using AWS SSO profile: {profile}")
                self.session = aws_sso_lib.get_boto3_session(profile=profile, region_name='us-east-1')
            except Exception as sso_e:
                logger.error(f"Failed to initialize boto3 via SSO as well: {sso_e}")
                self.session = None

        try:
            if self.session:
                self.inspector_client = self.session.client('inspector2')
                self.securityhub_client = self.session.client('securityhub')
                self.s3_client = self.session.client('s3')
                self.org_client = self.session.client('organizations')
                self.sts_client = self.session.client('sts')
            else:
                raise ValueError("Session is null")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
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
        if not self.org_client:
            logger.error("Boto3 Organizations client not initialized.")
            return accounts
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
        except Exception as e:
            logger.error(f"Error fetching AWS Accounts: {e}")
        return accounts

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
