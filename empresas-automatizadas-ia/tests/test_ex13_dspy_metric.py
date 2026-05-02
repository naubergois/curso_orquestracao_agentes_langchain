"""Ex. 13 — métrica heurística sem chamar LLM."""

from __future__ import annotations

import sys

import pytest

from tests.conftest import EMPRESAS_ROOT, purge_app_package


def test_metrica_retorna_chaves() -> None:
    pytest.importorskip("dspy", reason="pip install dspy-ai (ver exercicio-13/requirements.txt)")
    root = str((EMPRESAS_ROOT / "exercicio-13-dspy-optimizer").resolve())
    purge_app_package()
    sys.path.insert(0, root)
    try:
        import importlib

        mod = importlib.import_module("app.dspy_pipeline")
        m = mod.claridade_completude_precisao(
            "Primeiro passo. Segundo passo. Conclusão.", "passo"
        )
        assert "claridade" in m and "completude" in m and "precisao" in m and "total" in m
    finally:
        if root in sys.path:
            sys.path.remove(root)
        purge_app_package()
