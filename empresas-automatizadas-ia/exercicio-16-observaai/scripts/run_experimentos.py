#!/usr/bin/env python3
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from dotenv import load_dotenv

load_dotenv(_ROOT.parent.parent / ".env", override=False)
load_dotenv(_ROOT / ".env", override=True)

from app.experimentos import correr_entrada  # noqa: E402

if __name__ == "__main__":
    txt = " ".join(sys.argv[1:]) or "O que é um agente de IA?"
    print(json.dumps(correr_entrada(txt), ensure_ascii=False, indent=2))
