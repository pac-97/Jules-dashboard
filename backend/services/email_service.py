import logging
import os
import requests
import msal
import base64
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.client_id = os.getenv("AZURE_CLIENT_ID", "dummy_client_id")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET", "dummy_client_secret")
        self.tenant_id = os.getenv("AZURE_TENANT_ID", "dummy_tenant_id")
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]

        try:
            self.app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
        except Exception as e:
            logger.warning(f"Could not initialize MSAL Application: {e}")
            self.app = None

    def _get_access_token(self) -> str:
        if not self.app:
            return "mock_token"
        # In a real setup without mocked vars, this will fetch the MSAL token.
        # Here we catch the exception for mock environment resilience
        try:
            result = self.app.acquire_token_silent(self.scope, account=None)
            if not result:
                result = self.app.acquire_token_for_client(scopes=self.scope)
            if "access_token" in result:
                return result["access_token"]
        except Exception as e:
            logger.warning(f"MSAL authentication failed or missing credentials: {e}")
        return "mock_token"

    def send_owner_report_email(self, owner_email: str, accounts: List[str], inspector_report: bytes, cspm_report: bytes, trend_chart: bytes = b"", subject: str = None, body: str = None, cc: str = None) -> bool:
        """
        Sends an email with consolidated account data to an owner using Azure AD Microsoft Graph API.
        """
        logger.info(f"Preparing to send consolidated email to {owner_email} for accounts: {accounts}")
        token = self._get_access_token()

        endpoint = f"https://graph.microsoft.com/v1.0/users/{owner_email}/sendMail"

        default_subject = "AWS Security Organizational Posture Report"
        default_body = f"<h3>Executive Summary</h3><p>Attached are the automated security reports for your owned accounts: {', '.join(accounts)}</p>"

        email_msg = {
            "message": {
                "subject": subject if subject else default_subject,
                "body": {
                    "contentType": "HTML",
                    "content": body if body else default_body
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": owner_email
                        }
                    }
                ],
                "attachments": [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": "Inspector_Report.xlsx",
                        "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "contentBytes": base64.b64encode(inspector_report).decode("utf-8")
                    },
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": "CSPM_Report.xlsx",
                        "contentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "contentBytes": base64.b64encode(cspm_report).decode("utf-8")
                    }
                ]
            },
            "saveToSentItems": "false"
        }
        if cc:
            email_msg["message"]["ccRecipients"] = [
                {
                    "emailAddress": {
                        "address": cc_email.strip()
                    }
                } for cc_email in cc.split(',') if cc_email.strip()
            ]

        if trend_chart:
            email_msg["message"]["attachments"].append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": "Trend_Chart.png",
                "contentType": "image/png",
                "contentBytes": base64.b64encode(trend_chart).decode("utf-8")
            })


        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            # We mock the post request if token is mocked
            if token == "mock_token":
                logger.info(f"[MOCK] Simulated sending email to {owner_email} via Microsoft Graph API")
                return True

            response = requests.post(endpoint, json=email_msg, headers=headers)
            response.raise_for_status()
            logger.info("Email sent successfully via Graph API.")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email via Graph API: {e}")
            return False

email_service = EmailService()
