from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()

def test_get_at_risk_students():
    response = client.get("/api/analytics/at-risk?threshold=75")
    assert response.status_code == 200

def test_get_class_summary():
    response = client.get("/api/attendance/summary/1")
    # Accept 200 if class exists, or 404 if class 1 is unseeded
    assert response.status_code in [200, 404]