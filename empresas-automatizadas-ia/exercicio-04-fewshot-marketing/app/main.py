"""FewShot Marketing — API FastAPI (geração de campanhas com few-shot + Instructor)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from app.schemas.campanha import ESTILO_PARA_INSTRUCAO, Campanha, GerarCampanhaEntrada
from app.services.gerador_campanha import gerar_campanha


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

app = FastAPI(
    title="FewShot Marketing",
    version="1.0.0",
    description="Campanhas estilo marca via few-shot (LangChain) + saída estruturada (Instructor + Pydantic).",
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "exercicio": 4,
        "empresa": "FewShot Marketing",
        "frameworks": ["LangChain (prompts)", "Instructor", "Pydantic", "Gemini"],
    }


@app.get("/campanhas/estilos")
def listar_estilos() -> dict[str, str]:
    """Presets do desafio extra: formal | engracado | tecnico | provocativo (+ livre)."""
    return dict(ESTILO_PARA_INSTRUCAO)


@app.post("/campanhas/gerar", response_model=Campanha)
def post_gerar(body: GerarCampanhaEntrada) -> Campanha:
    if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
        raise HTTPException(status_code=503, detail="Defina GOOGLE_API_KEY no .env da raiz do repositório.")
    try:
        return gerar_campanha(body)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def main() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    main()
