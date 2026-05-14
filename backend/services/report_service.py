import io
import logging
from typing import List, Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)

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

    def merge_account_reports(self, account_reports: Dict[str, bytes]) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not account_reports:
                pd.DataFrame([{'Message': 'No account reports available'}]).to_excel(writer, sheet_name='Summary', index=False)
                return output.getvalue()

            for account_id, report_bytes in account_reports.items():
                try:
                    sheets = pd.read_excel(io.BytesIO(report_bytes), sheet_name=None)
                    for sheet_name, df in sheets.items():
                        safe_name = f"{account_id}_{sheet_name}"[:31]
                        df.to_excel(writer, sheet_name=safe_name, index=False)
                except Exception as e:
                    logger.warning(f"Unable to merge account report for {account_id}: {e}")
                    pd.DataFrame([{'Warning': f'Could not merge report for {account_id}: {str(e)}'}]).to_excel(
                        writer, sheet_name=f"{account_id}_error"[:31], index=False
                    )

        return output.getvalue()

    def summarize_account_reports(self, account_reports: Dict[str, bytes]) -> Dict[str, Any]:
        summary = {
            'accounts': [],
            'total_reports': len(account_reports),
            'findings': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        for account_id, report_bytes in account_reports.items():
            try:
                sheets = pd.read_excel(io.BytesIO(report_bytes), sheet_name=None)
                df = pd.concat([sheet for sheet in sheets.values() if not sheet.empty], ignore_index=True)
                if not df.empty:
                    summary['accounts'].append(account_id)
                    summary['findings'] += len(df)
                    for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                        if 'severity' in df.columns:
                            summary[level.lower()] += int((df['severity'] == level).sum())
                        elif level.lower() in df.columns:
                            summary[level.lower()] += int(df[level.lower()].sum())
            except Exception as e:
                logger.warning(f"Could not summarize account report for {account_id}: {e}")

        return summary

report_service = ReportService()
