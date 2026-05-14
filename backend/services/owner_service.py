import json
import os
from typing import List, Dict, Any

DATA_FILE = "owners.json"

class OwnerService:
    def __init__(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w') as f:
                json.dump([
                    {"email": "secops-lead@enterprise.com", "accounts": ["123456789012", "987654321098"], "lastEmailed": "2024-05-13 08:00 AM"},
                    {"email": "engineering-vp@enterprise.com", "accounts": ["555555555555", "444444444444", "333333333333"], "lastEmailed": "2024-05-13 08:02 AM"}
                ], f)

    def get_owners(self) -> List[Dict[str, Any]]:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)

    def update_owners(self, owners: List[Dict[str, Any]]):
        with open(DATA_FILE, 'w') as f:
            json.dump(owners, f, indent=2)

owner_service = OwnerService()
