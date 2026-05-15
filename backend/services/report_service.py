import pandas as pd
from typing import List, Dict, Any
import io

class ReportService:
    def generate_inspector_report(self, findings: List[Dict[str, Any]]) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not findings:
                pd.DataFrame([{'Message': 'No findings available'}]).to_excel(writer, sheet_name='Executive Summary', index=False)
                return output.getvalue()

            df = pd.DataFrame(findings)

            # Global Executive Summary
            summary_data = {
                'Metric': ['Total Findings', 'Critical', 'High'],
                'Value': [
                    len(df),
                    len(df[df['severity'] == 'CRITICAL']) if 'severity' in df.columns else 0,
                    len(df[df['severity'] == 'HIGH']) if 'severity' in df.columns else 0
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive Summary', index=False)

            # Group findings into separate sheets by AWS Account ID
            if 'accountId' in df.columns:
                for account_id, group in df.groupby('accountId'):
                    sheet_name = f"Account {account_id}"[:31]  # Excel limits sheet names to 31 chars
                    group.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                df.to_excel(writer, sheet_name='All Findings', index=False)

        return output.getvalue()

    def generate_cspm_report(self, cspm_data: Dict[str, Any]) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Scorecard
            scorecard = {
                'Metric': ['Compliance Score', 'CIS Score', 'NIST Score', 'Passed Controls', 'Failed Controls'],
                'Value': [
                    cspm_data.get('compliance_score', 0),
                    cspm_data.get('cis_score', 0),
                    cspm_data.get('nist_score', 0),
                    cspm_data.get('passed_controls', 0),
                    cspm_data.get('failed_controls', 0)
                ]
            }
            pd.DataFrame(scorecard).to_excel(writer, sheet_name='Scorecard', index=False)

            # Group Failed Controls into separate sheets by AWS Account ID
            if 'findings' in cspm_data and cspm_data['findings']:
                df = pd.DataFrame(cspm_data['findings'])
                if 'accountId' in df.columns:
                    for account_id, group in df.groupby('accountId'):
                        sheet_name = f"Failed {account_id}"[:31]
                        group.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    df.to_excel(writer, sheet_name='Failed Controls', index=False)
            else:
                pd.DataFrame([{'Message': 'No failed controls available'}]).to_excel(writer, sheet_name='Failed Controls', index=False)

        return output.getvalue()

report_service = ReportService()
