"""Smoke tests: GET /health para todas as APIs FastAPI."""

from __future__ import annotations

import pytest

from tests.conftest import FASTAPI_EXERCISES, app_test_client


@pytest.mark.parametrize("slug", FASTAPI_EXERCISES)
def test_health_ok(slug: str) -> None:
    with app_test_client(slug) as client:
        response = client.get("/health")
        assert response.status_code == 200, f"{slug}: {response.text}"
        body = response.json()
        assert body.get("status") == "ok"
