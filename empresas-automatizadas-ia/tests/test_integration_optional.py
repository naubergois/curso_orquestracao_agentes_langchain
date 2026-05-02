"""Testes de integração (opcionais): requerem chaves e serviços externos."""

from __future__ import annotations

import os

import pytest

from tests.conftest import app_test_client

pytestmark = pytest.mark.integration


@pytest.fixture
def require_google() -> None:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        pytest.skip("GOOGLE_API_KEY / GEMINI_API_KEY não definidas")


def test_ex18_resumir(require_google: None) -> None:
    with app_test_client("exercicio-18-api-agent-factory") as client:
        response = client.post(
            "/resumir",
            json={"texto": "Este é um texto longo que deve ser resumido em poucas frases para validar o endpoint."},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "resumo" in data and len(data["resumo"]) > 0
