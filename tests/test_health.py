"""
Smoke tests for the AgroArc FastAPI backend.

These tests run in-process via FastAPI's TestClient (no live server, no
external network) and verify that:
  - The application boots cleanly (all routers register, all models load)
  - Each domain's /health endpoint returns 200
  - The crop ML pipeline runs end-to-end (scaler -> model -> response)
  - The /chat endpoint degrades gracefully when GEMINI_API_KEY is unset
  - The weather endpoint reports "unconfigured" without OPENWEATHER_API_KEY

No real API keys are needed; the tests deliberately exercise the
fallback paths so CI can run without secrets.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client() -> TestClient:
    # Force the unconfigured paths regardless of whether a developer has a
    # populated backend/.env on disk. python-dotenv's load_dotenv() searches
    # parent directories and would otherwise pull in real keys; assigning
    # empty strings beats it because load_dotenv(override=False) won't
    # replace already-set variables.
    os.environ["OPENWEATHER_API_KEY"] = ""
    os.environ["GEMINI_API_KEY"] = ""

    from backend.app.main import app

    return TestClient(app)


def test_root_health(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "endpoints" in payload
    assert payload["endpoints"]["general_chat"] == "/chat"


def test_crop_health(client: TestClient) -> None:
    response = client.get("/api/v1/crop/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["models_loaded"] is True
    assert payload["scaler_loaded"] is True


def test_fertilizer_health(client: TestClient) -> None:
    response = client.get("/api/v1/fertilizer/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["models_loaded"] is True


def test_weather_health_reports_unconfigured_without_key(client: TestClient) -> None:
    response = client.get("/api/v1/weather/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["api_configured"] is False


def test_crop_prediction_runs_end_to_end(client: TestClient) -> None:
    payload = {
        "N": 90,
        "P": 42,
        "K": 43,
        "temperature": 20.8,
        "humidity": 82,
        "ph": 6.5,
        "rainfall": 202.9,
    }
    response = client.post("/api/v1/crop/predict-crop", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data["recommended_crop"], str) and data["recommended_crop"]
    assert 0.0 <= float(data["confidence"]) <= 100.0


def test_chat_falls_back_without_gemini_key(client: TestClient) -> None:
    response = client.post("/chat", json={"message": "ping"})
    assert response.status_code == 200
    body = response.json()
    assert "reply" in body
    assert "temporarily unable" in body["reply"].lower()
