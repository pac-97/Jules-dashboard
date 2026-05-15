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

chart_service = ChartService()
