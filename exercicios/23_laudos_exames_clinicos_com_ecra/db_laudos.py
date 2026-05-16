"""Acesso PostgreSQL aos pacientes e laudos (demo)."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg2
from psycopg2.extras import Json, RealDictCursor


def _database_url() -> str:
    u = (os.environ.get("DATABASE_URL") or "").strip()
    if not u:
        raise RuntimeError("Defina DATABASE_URL (ex.: postgresql://curso:curso@db:5432/laudos_clinicos).")
    return u


@contextmanager
def cursor_dict() -> Iterator[Any]:
    conn = psycopg2.connect(_database_url())
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def listar_pacientes_resumo() -> list[dict[str, Any]]:
    with cursor_dict() as cur:
        cur.execute(
            """
            SELECT p.id, p.nome_completo, p.idade, p.sexo,
                   (SELECT COUNT(*) FROM exames_laboratoriais e WHERE e.paciente_id = p.id) AS n_exames,
                   (SELECT nivel_gravidade FROM avaliacoes_engine a
                    WHERE a.paciente_id = p.id ORDER BY a.criado_em DESC LIMIT 1) AS ultimo_nivel
            FROM pacientes p
            ORDER BY p.id
            """
        )
        return [dict(row) for row in cur.fetchall()]


def ficha_paciente(paciente_id: int) -> dict[str, Any] | None:
    with cursor_dict() as cur:
        cur.execute(
            "SELECT * FROM pacientes WHERE id = %s",
            (paciente_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def laudos_paciente_texto(paciente_id: int) -> str:
    with cursor_dict() as cur:
        cur.execute(
            """
            SELECT codigo, data_exame, painel, laudo_texto, valores_estruturados
            FROM exames_laboratoriais
            WHERE paciente_id = %s
            ORDER BY data_exame, id
            """,
            (paciente_id,),
        )
        rows = cur.fetchall()
    blocos: list[str] = []
    for r in rows:
        vs = r.get("valores_estruturados")
        extra = ""
        if vs is not None:
            extra = "\nValores (JSON): " + json.dumps(vs, ensure_ascii=False)
        blocos.append(
            f"--- {r['codigo']} | {r['data_exame']} | {r.get('painel') or '—'}\n{r['laudo_texto']}{extra}"
        )
    return "\n\n".join(blocos) if blocos else "(sem exames)"


def ultima_avaliacao_dict(paciente_id: int) -> dict[str, Any] | None:
    with cursor_dict() as cur:
        cur.execute(
            """
            SELECT id, nivel_gravidade, score, payload_json, criado_em
            FROM avaliacoes_engine
            WHERE paciente_id = %s
            ORDER BY criado_em DESC
            LIMIT 1
            """,
            (paciente_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        d = dict(row)
        if isinstance(d.get("criado_em"), object) and hasattr(d["criado_em"], "isoformat"):
            d["criado_em"] = d["criado_em"].isoformat()
        return d


def inserir_avaliacao(paciente_id: int, nivel: str, score: int, payload: dict[str, Any]) -> None:
    with cursor_dict() as cur:
        cur.execute(
            """
            INSERT INTO avaliacoes_engine (paciente_id, nivel_gravidade, score, payload_json)
            VALUES (%s, %s, %s, %s)
            """,
            (paciente_id, nivel, score, Json(payload)),
        )
