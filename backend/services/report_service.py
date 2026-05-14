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

    def generate_account_report_from_scores(self, scores_df: pd.DataFrame) -> bytes:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if scores_df is None or scores_df.empty:
                pd.DataFrame([{'Message': 'No account scores available'}]).to_excel(writer, sheet_name='Summary', index=False)
                return output.getvalue()

            id_col = 'accountid' if 'accountid' in scores_df.columns else 'account_id' if 'account_id' in scores_df.columns else None
            if not id_col:
                scores_df.to_excel(writer, sheet_name='Accounts', index=False)
            else:
                for account_id, group in scores_df.groupby(id_col):
                    sheet_name = f"Account_{account_id}"[:31]
                    group.to_excel(writer, sheet_name=sheet_name, index=False)

            summary = {
                'accounts': len(scores_df[id_col].unique()) if id_col else 1,
                'findings': len(scores_df),
                'critical': int(scores_df.get('critical', pd.Series(dtype='int')).fillna(0).sum()),
                'high': int(scores_df.get('high', pd.Series(dtype='int')).fillna(0).sum()),
                'medium': int(scores_df.get('medium', pd.Series(dtype='int')).fillna(0).sum()),
                'low': int(scores_df.get('low', pd.Series(dtype='int')).fillna(0).sum())
            }
            pd.DataFrame([summary]).to_excel(writer, sheet_name='Summary', index=False)

        return output.getvalue()

    def summarize_account_scores(self, scores_df: pd.DataFrame) -> Dict[str, Any]:
        summary = {
            'accounts': [],
            'findings': 0,
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        if scores_df is None or scores_df.empty:
            return summary

        id_col = 'accountid' if 'accountid' in scores_df.columns else 'account_id' if 'account_id' in scores_df.columns else None
        if id_col:
            summary['accounts'] = sorted(scores_df[id_col].astype(str).unique())

        summary['findings'] = len(scores_df)
        summary['critical'] = int(scores_df.get('critical', pd.Series(dtype='int')).fillna(0).sum())
        summary['high'] = int(scores_df.get('high', pd.Series(dtype='int')).fillna(0).sum())
        summary['medium'] = int(scores_df.get('medium', pd.Series(dtype='int')).fillna(0).sum())
        summary['low'] = int(scores_df.get('low', pd.Series(dtype='int')).fillna(0).sum())

        return summary

report_service = ReportService()
