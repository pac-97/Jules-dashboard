import pandas as pd
from typing import List, Dict, Any
import io

class ReportService:
    def generate_inspector_report(self, findings: List[Dict[str, Any]]) -> bytes:
        df = pd.DataFrame(findings)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Executive Summary
            summary_data = {
                'Metric': ['Total Findings', 'Critical', 'High'],
                'Value': [
                    len(df),
                    len(df[df['severity'] == 'CRITICAL']) if 'severity' in df.columns else 0,
                    len(df[df['severity'] == 'HIGH']) if 'severity' in df.columns else 0
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive Summary', index=False)

            # Full Findings
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

            # Failed Controls
            if 'findings' in cspm_data:
                pd.DataFrame(cspm_data['findings']).to_excel(writer, sheet_name='Failed Controls', index=False)

        return output.getvalue()

report_service = ReportService()
