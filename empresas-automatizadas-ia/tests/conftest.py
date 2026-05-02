"""Carregar cada `app.main:app` sem colisão do pacote `app`."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

EMPRESAS_ROOT = Path(__file__).resolve().parents[1]

# Empresas com API FastAPI (`app = FastAPI(...)` em app/main.py)
FASTAPI_EXERCISES = [
    "exercicio-01-promptlab",
    "exercicio-03-eduprompt",
    "exercicio-04-fewshot-marketing",
    "exercicio-05-parser-juridico",
    "exercicio-06-rag-juridico",
    "exercicio-07-busca-semantica",
    "exercicio-08-govbot",
    "exercicio-09-helpdesk-agent",
    "exercicio-10-crewfinance",
    "exercicio-11-autogen-research",
    "exercicio-12-semantic-kernel-office",
    "exercicio-13-dspy-optimizer",
    "exercicio-14-tutorgraph",
    "exercicio-15-auditoriagraph",
    "exercicio-16-observaai",
    "exercicio-17-localbot",
    "exercicio-18-api-agent-factory",
    "exercicio-20-empresa-autonoma-integrada",
]


def purge_app_package() -> None:
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]


@contextmanager
def app_test_client(exercise_relative: str) -> Iterator[TestClient]:
    root = (EMPRESAS_ROOT / exercise_relative).resolve()
    if not root.is_dir():
        raise FileNotFoundError(root)
    purge_app_package()
    path_str = str(root)
    sys.path.insert(0, path_str)
    try:
        import importlib

        try:
            mod = importlib.import_module("app.main")
        except ModuleNotFoundError as e:
            pytest.skip(f"{exercise_relative}: falta dependência ({e})")
        except ImportError as e:
            pytest.skip(f"{exercise_relative}: import falhou ({e})")
        application = getattr(mod, "app", None)
        if application is None:
            pytest.skip(f"{exercise_relative}: `app.main` sem FastAPI `app`")
        with TestClient(application, raise_server_exceptions=False) as client:
            yield client
    finally:
        if path_str in sys.path:
            sys.path.remove(path_str)
        purge_app_package()


@pytest.fixture
def empresas_root() -> Path:
    return EMPRESAS_ROOT


@pytest.fixture
def google_api_key_set() -> bool:
    import os

    return bool(os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"))
