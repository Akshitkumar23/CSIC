"""Tests for health probes and basic service accessibility."""
from fastapi.testclient import TestClient


def test_root_index(client: TestClient) -> None:
    """Verify root index endpoint exposes service metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert "version" in data
    assert data["api_v1"] == "/api/v1"


def test_health_live_probe(client: TestClient) -> None:
    """Verify Kubernetes liveness probe returns 200 and alive status."""
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert data["service"] == "csic-backend"
    assert "timestamp" in data


def test_health_ready_probe(client: TestClient) -> None:
    """Verify Kubernetes readiness probe returns 200 and ready status."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "timestamp" in data
