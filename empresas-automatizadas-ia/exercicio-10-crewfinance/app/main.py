"""CrewFinance — API sobre crew CrewAI."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.crew_runner import PedidoFinanceiro, executar_crew


def _env() -> None:
    r = Path(__file__).resolve().parents[1]
    load_dotenv(r.parent.parent / ".env", override=False)
    load_dotenv(r / ".env", override=True)


_env()

app = FastAPI(title="CrewFinance", version="1.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "exercicio": 10}


@app.post("/relatorio")
def relatorio(body: PedidoFinanceiro) -> dict:
    if not os.environ.get("GOOGLE_API_KEY"):
        raise HTTPException(status_code=503, detail="GOOGLE_API_KEY em falta (LiteLLM/Gemini).")
    try:
        return {"relatorio": executar_crew(body.pedido)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)[:900]) from e


def main() -> None:
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))


if __name__ == "__main__":
    main()
