import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import pandas as pd
from typing import List, Dict, Any

class ChartService:
    def generate_trend_chart(self, trend_data: List[Dict[str, Any]]) -> bytes:
        if not trend_data:
            return b""

        df = pd.DataFrame(trend_data)

        plt.figure(figsize=(10, 5))
        plt.plot(df['date'], df['compliance_score'], marker='o', label='Compliance Score', color='#3b82f6')

        plt.title('Security Compliance Trend over 30 Days')
        plt.xlabel('Date')
        plt.ylabel('Compliance Score (%)')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        return buf.getvalue()

    def generate_cis_benchmark_chart(self, scores_df: pd.DataFrame) -> bytes:
        """Generate CIS AWS Foundations Benchmark v5.0.0 chart from account scores"""
        if scores_df is None or scores_df.empty or 'cis_score' not in scores_df.columns:
            return b""

        # Get latest scores by account
        account_col = 'accountid' if 'accountid' in scores_df.columns else 'account_id'
        if account_col not in scores_df.columns:
            return b""

        latest = scores_df.sort_values('date', ascending=False).drop_duplicates(account_col)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        accounts = latest[account_col].astype(str).values
        scores = latest['cis_score'].fillna(0).values
        
        colors = ['#22c55e' if s >= 80 else '#eab308' if s >= 60 else '#ef4444' for s in scores]
        ax.bar(accounts, scores, color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_title('CIS AWS Foundations Benchmark v5.0.0 - Account Scores', fontsize=14, fontweight='bold')
        ax.set_xlabel('AWS Account ID', fontsize=11)
        ax.set_ylabel('Compliance Score (%)', fontsize=11)
        ax.set_ylim(0, 100)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # Add value labels on bars
        for i, (account, score) in enumerate(zip(accounts, scores)):
            ax.text(i, score + 2, f'{score:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf.getvalue()

    def generate_nist_benchmark_chart(self, scores_df: pd.DataFrame) -> bytes:
        """Generate NIST Special Publication 800-53 Revision 5 chart from account scores"""
        if scores_df is None or scores_df.empty or 'nist_score' not in scores_df.columns:
            return b""

        # Get latest scores by account
        account_col = 'accountid' if 'accountid' in scores_df.columns else 'account_id'
        if account_col not in scores_df.columns:
            return b""

        latest = scores_df.sort_values('date', ascending=False).drop_duplicates(account_col)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        accounts = latest[account_col].astype(str).values
        scores = latest['nist_score'].fillna(0).values
        
        colors = ['#3b82f6' if s >= 80 else '#8b5cf6' if s >= 60 else '#f87171' for s in scores]
        ax.bar(accounts, scores, color=colors, alpha=0.7, edgecolor='black')
        
        ax.set_title('NIST Special Publication 800-53 Revision 5 - Account Scores', fontsize=14, fontweight='bold')
        ax.set_xlabel('AWS Account ID', fontsize=11)
        ax.set_ylabel('Compliance Score (%)', fontsize=11)
        ax.set_ylim(0, 100)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3)
        
        # Add value labels on bars
        for i, (account, score) in enumerate(zip(accounts, scores)):
            ax.text(i, score + 2, f'{score:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf.getvalue()

    def generate_severity_breakdown_chart(self, scores_df: pd.DataFrame) -> bytes:
        """Generate severity breakdown chart from account scores"""
        if scores_df is None or scores_df.empty:
            return b""

        critical = int(scores_df.get('critical', pd.Series(dtype='int')).fillna(0).sum())
        high = int(scores_df.get('high', pd.Series(dtype='int')).fillna(0).sum())
        medium = int(scores_df.get('medium', pd.Series(dtype='int')).fillna(0).sum())
        low = int(scores_df.get('low', pd.Series(dtype='int')).fillna(0).sum())
        
        if critical + high + medium + low == 0:
            return b""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        severities = ['Critical', 'High', 'Medium', 'Low']
        counts = [critical, high, medium, low]
        colors = ['#ef4444', '#f97316', '#eab308', '#3b82f6']
        
        wedges, texts, autotexts = ax.pie(counts, labels=severities, colors=colors, autopct='%1.1f%%',
                                            startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        ax.set_title('Security Findings by Severity', fontsize=14, fontweight='bold', pad=20)
        
        # Add count info
        legend_labels = [f'{sev}: {count}' for sev, count in zip(severities, counts)]
        ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        plt.close()
        
        return buf.getvalue()

chart_service = ChartService()
