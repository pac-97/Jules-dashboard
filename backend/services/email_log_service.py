import json
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime

DATA_FILE = "email_logs.json"

class EmailLogService:
    def __init__(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w') as f:
                json.dump([], f)

    def get_logs(self) -> List[Dict[str, Any]]:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)

    def add_log(self, to: str, cc: str, subject: str, body: str, status: str, accounts: List[str]):
        logs = self.get_logs()
        log_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "to": to,
            "cc": cc,
            "subject": subject,
            "body": body,
            "status": status,
            "accounts": accounts
        }
        logs.append(log_entry)
        with open(DATA_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

email_log_service = EmailLogService()
