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

    def sync_accounts(self, aws_accounts: List[Dict[str, str]]):
        owners = self.get_owners()

        # Build list of already mapped account IDs
        mapped_accounts = set()
        for o in owners:
            mapped_accounts.update(o.get('accounts', []))

        unmapped_accounts = []
        for acc in aws_accounts:
            if acc['id'] not in mapped_accounts:
                unmapped_accounts.append(acc['id'])

        # If there's unmapped accounts, either create a default 'Unassigned' owner bucket or attach to an existing generic pool
        if unmapped_accounts:
            unassigned_owner = next((o for o in owners if o.get('email') == 'unassigned@enterprise.com'), None)
            if not unassigned_owner:
                owners.append({
                    "email": "unassigned@enterprise.com",
                    "accounts": unmapped_accounts,
                    "lastEmailed": ""
                })
            else:
                unassigned_owner["accounts"].extend(unmapped_accounts)
                unassigned_owner["accounts"] = list(set(unassigned_owner["accounts"]))

        self.update_owners(owners)
        return {"synced": len(unmapped_accounts)}

owner_service = OwnerService()
