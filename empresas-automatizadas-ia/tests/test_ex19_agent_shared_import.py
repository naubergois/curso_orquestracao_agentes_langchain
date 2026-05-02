"""Ex. 19 — módulo partilhado Streamlit/Gradio importa sem FastAPI."""

from __future__ import annotations

import sys

from tests.conftest import EMPRESAS_ROOT, purge_app_package


def test_agent_shared_importavel() -> None:
    root = str((EMPRESAS_ROOT / "exercicio-19-interface-agent-studio").resolve())
    purge_app_package()
    sys.path.insert(0, root)
    try:
        import importlib

        mod = importlib.import_module("app.agent_shared")
        assert callable(mod.responder)
    finally:
        if root in sys.path:
            sys.path.remove(root)
        purge_app_package()
