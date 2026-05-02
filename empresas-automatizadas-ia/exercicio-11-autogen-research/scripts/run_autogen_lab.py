#!/usr/bin/env python3
"""Execução em CLI do debate (equivalente ao POST /debate)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Permitir `python scripts/run_autogen_lab.py` sem PYTHONPATH
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT.parent.parent / ".env", override=False)
load_dotenv(_ROOT / ".env", override=True)

from app.autogen_flow import executar_debate  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="AutoGen Research Lab — debate no terminal.")
    p.add_argument("tema", help="Tema ou pergunta")
    p.add_argument("--rodadas", type=int, default=4, help="Número de voltas (extra)")
    p.add_argument("--json", action="store_true", help="Imprime JSON")
    args = p.parse_args()
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Erro: GOOGLE_API_KEY não definido.", file=sys.stderr)
        sys.exit(1)
    out = executar_debate(args.tema, rodadas=args.rodadas)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for i, m in enumerate(out["log"], 1):
            print(f"\n--- {i}. {m['role']} ---\n{m['content']}")
        print("\n=== Relatório final ===\n", out["relatorio_final"])


if __name__ == "__main__":
    main()
