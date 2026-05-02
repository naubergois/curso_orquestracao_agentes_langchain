"""Ex. 2 — funções puras do Streamlit app (sem UI)."""

from __future__ import annotations

import sys

from tests.conftest import EMPRESAS_ROOT, purge_app_package


def test_historico_para_mensagens_inclui_system_e_human() -> None:
    root = str((EMPRESAS_ROOT / "exercicio-02-atendimento-360").resolve())
    purge_app_package()
    sys.path.insert(0, root)
    try:
        import importlib

        mod = importlib.import_module("app.main")
        msgs = mod._historico_para_mensagens([{"role": "user", "content": "Olá"}])
        assert len(msgs) >= 2
        from langchain_core.messages import HumanMessage, SystemMessage

        assert isinstance(msgs[0], SystemMessage)
        assert any(isinstance(m, HumanMessage) for m in msgs)
    finally:
        if root in sys.path:
            sys.path.remove(root)
        purge_app_package()
