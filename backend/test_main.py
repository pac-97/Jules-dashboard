from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_dashboard_summary():
    response = client.get("/api/dashboard/executive-summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_findings" in data
    assert "compliance_score" in data
