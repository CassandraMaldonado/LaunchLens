from fastapi.testclient import TestClient

from launch_lens.api import app

client = TestClient(app)


def test_health_and_analysis_endpoints():
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.get("/api/analysis?seed=42&users=1000")
    assert response.status_code == 200
    assert response.json()["experiment"]["users"] == 1000


def test_invalid_sample_size_is_rejected():
    assert client.get("/api/analysis?users=20").status_code == 422

