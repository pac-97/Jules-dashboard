import json
import os
import uuid
from typing import List, Dict, Any
from datetime import datetime

DATA_FILE = "templates.json"

class TemplateService:
    def __init__(self):
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'w') as f:
                json.dump([
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Standard Executive Report",
                        "subject": "AWS Security Organizational Posture Report",
                        "body": "<h3>Executive Summary</h3><p>Attached are the automated security reports for your owned accounts.</p>"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Critical Vulnerability Alert",
                        "subject": "URGENT: Critical AWS Findings Detected",
                        "body": "<h3>Action Required</h3><p>Critical vulnerabilities have been detected in the attached reports. Please remediate immediately.</p>"
                    }
                ], f)

    def get_templates(self) -> List[Dict[str, Any]]:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)

    def update_templates(self, templates: List[Dict[str, Any]]):
        for template in templates:
            if "id" not in template:
                template["id"] = str(uuid.uuid4())
        with open(DATA_FILE, 'w') as f:
            json.dump(templates, f, indent=2)

template_service = TemplateService()
