#!/usr/bin/env python3
"""Executa avaliação DSPy no terminal (equivalente a POST /avaliar)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT.parent.parent / ".env", override=False)
load_dotenv(_ROOT / ".env", override=True)

from app.dspy_pipeline import avaliar  # noqa: E402


def main() -> None:
    out = avaliar()
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
