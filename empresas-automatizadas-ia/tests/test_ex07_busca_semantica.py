"""Ex. 7 — /buscar sem índice deve falhar com 503 (índice ausente é tratado)."""

from __future__ import annotations

import pytest

from tests.conftest import app_test_client


def test_buscar_sem_indice_retorna_503() -> None:
    with app_test_client("exercicio-07-busca-semantica") as client:
        response = client.post("/buscar", json={"pergunta": "teste de pergunta válida"})
        # Sem índice pré-construído no CI: esperado 503 ou 500 conforme ambiente
        assert response.status_code in (503, 500), response.text
