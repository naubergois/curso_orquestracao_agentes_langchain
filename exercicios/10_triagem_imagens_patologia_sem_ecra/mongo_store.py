"""Persistência dos casos de triagem em **MongoDB** (resultados do classificador + prioridade)."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

from triagem import nome_patologia_prioritaria


def uri_mongodb() -> str:
    return (
        os.environ.get("MONGODB_URI")
        or os.environ.get("EX10_MONGODB_URI")
        or "mongodb://curso:curso@127.0.0.1:27018/triagem?authSource=admin"
    ).strip()


_COLL: Collection | None = None


def coll_casos() -> Collection:
    global _COLL
    if _COLL is not None:
        return _COLL
    client = MongoClient(uri_mongodb(), serverSelectionTimeoutMS=8000)
    # URI …/triagem define a BD por defeito
    db = client.get_database("triagem")
    coll = db["casos"]
    coll.create_index("caso_id", unique=True)
    coll.create_index([("estado", 1), ("prioridade", -1)])
    _COLL = coll
    return coll


def inserir_caso(
    *,
    caso_id: str,
    origem: str,
    indice_amostra: int | None,
    split: str | None,
    rotulo_verdadeiro: int | None,
    resultado_classificador: dict[str, Any],
    prioridade: float,
) -> str:
    doc = {
        "caso_id": caso_id,
        "origem": origem,
        "indice_amostra": indice_amostra,
        "split": split,
        "rotulo_verdadeiro": rotulo_verdadeiro,
        "probabilidades": resultado_classificador["probabilidades"],
        "classe_predita": resultado_classificador["classe_predita"],
        "rotulo_predito": resultado_classificador["rotulo_predito"],
        "confianca_maxima": resultado_classificador["confianca_maxima"],
        "prioridade": prioridade,
        "patologia_prioritaria_nome": nome_patologia_prioritaria(),
        "estado": "pendente",
        "criado_em": datetime.now(timezone.utc),
    }
    coll_casos().update_one({"caso_id": caso_id}, {"$set": doc}, upsert=True)
    return caso_id


def listar_top_prioridade(limite: int = 10) -> list[dict[str, Any]]:
    cur = (
        coll_casos()
        .find({"estado": "pendente"})
        .sort("prioridade", -1)
        .limit(limite)
    )
    return list(cur)


def contar_pendentes() -> int:
    return coll_casos().count_documents({"estado": "pendente"})


def marcar_atendido(caso_id: str) -> bool:
    r = coll_casos().update_one(
        {"caso_id": caso_id},
        {"$set": {"estado": "atendido", "atendido_em": datetime.now(timezone.utc)}},
    )
    return r.modified_count > 0


def obter_caso(caso_id: str) -> dict[str, Any] | None:
    return coll_casos().find_one({"caso_id": caso_id})
