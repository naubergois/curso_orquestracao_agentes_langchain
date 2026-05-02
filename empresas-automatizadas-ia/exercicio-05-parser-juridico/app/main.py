"""Parser Jurídico — API FastAPI (Exercício 5)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.schemas.demanda import DemandaExtraida, TextoDemandaIn
from app.services.parser_juridico import TextoNaoJuridicoError, analisar_demanda


def _carregar_env() -> None:
    ex_root = Path(__file__).resolve().parents[1]
    repo_root = ex_root.parent.parent
    load_dotenv(repo_root / ".env", override=False)
    load_dotenv(ex_root / ".env", override=True)


_carregar_env()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Parser Jurídico",
    version="1.0.0",
    description=(
        "Empresa simulada **Parser Jurídico**: extracção estruturada de demandas informais "
        "com **Pydantic**, **Instructor** + Gemini e gate para texto não jurídico."
    ),
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "exercicio": 5,
        "empresa": "Parser Jurídico",
        "modelo": (
            os.environ.get("GEMINI_MODEL_EX05")
            or os.environ.get("GEMINI_MODEL")
            or "gemini-2.0-flash"
        ).replace("models/", ""),
    }


@app.post(
    "/analisar",
    response_model=DemandaExtraida,
    responses={
        422: {
            "description": "Validação falhou ou texto não jurídico (bloqueio).",
            "content": {
                "application/json": {
                    "example": {
                        "detail": {
                            "codigo": "TEXTO_NAO_JURIDICO",
                            "mensagem": "O texto parece ser uma receita culinária sem contexto jurídico.",
                        }
                    }
                }
            },
        },
        503: {"description": "Falha ao contactar o modelo (quota/rede)."},
    },
)
def analisar(body: TextoDemandaIn) -> DemandaExtraida:
    """Recebe texto livre e devolve JSON estruturado após screening + extração validada."""
    key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise HTTPException(
            status_code=503,
            detail={
                "codigo": "CONFIG_INCOMPLETA",
                "mensagem": "Defina GOOGLE_API_KEY no `.env` na raiz do repositório.",
            },
        )

    try:
        return analisar_demanda(body.texto)
    except TextoNaoJuridicoError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "codigo": "TEXTO_NAO_JURIDICO",
                "mensagem": e.motivo,
            },
        ) from e
    except ValidationError as e:
        logger.warning("Validação Pydantic/Instructor: %s", e)
        raise HTTPException(
            status_code=422,
            detail={
                "codigo": "VALIDACAO_SAIDA",
                "mensagem": "O modelo devolveu dados inválidos para o schema.",
                "erros": e.errors(),
            },
        ) from e
    except Exception as e:
        logger.exception("Falha na análise")
        raise HTTPException(
            status_code=503,
            detail={
                "codigo": "MODELO_INDISPONIVEL",
                "mensagem": str(e)[:500],
            },
        ) from e


@app.exception_handler(HTTPException)
async def http_exc_handler(_, exc: HTTPException):
    """Respostas JSON consistentes com campo `detail` estruturado quando for dict."""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": {"mensagem": exc.detail}},
    )


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
