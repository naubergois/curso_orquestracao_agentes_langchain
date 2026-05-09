"""PostgreSQL: utilizadores, sessões e resumo acumulado por utilizador (exercício 19)."""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


def _load_local_env() -> None:
    here = Path(__file__).resolve()
    for directory in (here.parent, *here.parents):
        env_path = directory / ".env"
        if env_path.is_file():
            load_dotenv(env_path, override=False)
            return


_load_local_env()


def database_url() -> str:
    u = (os.environ.get("DATABASE_URL") or "").strip()
    if u:
        return u
    return "postgresql://curso:curso@127.0.0.1:5437/chat_memoria_demo"


def _connect():
    return psycopg2.connect(database_url(), connect_timeout=10)


def obter_ou_criar_utilizador(external_id: str) -> int:
    ext = (external_id or "").strip()
    if not ext:
        raise ValueError("external_id obrigatório.")
    with _connect() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO utilizadores (external_id) VALUES (%s)
                ON CONFLICT (external_id) DO UPDATE SET external_id = EXCLUDED.external_id
                RETURNING id
                """,
                (ext,),
            )
            row = cur.fetchone()
            uid = int(row[0])
            cur.execute(
                """
                INSERT INTO resumo_acumulado (utilizador_id, texto)
                VALUES (%s, '')
                ON CONFLICT (utilizador_id) DO NOTHING
                """,
                (uid,),
            )
    return uid


def ler_resumo_acumulado(external_id: str) -> str:
    uid = obter_ou_criar_utilizador(external_id)
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT texto FROM resumo_acumulado WHERE utilizador_id = %s",
                (uid,),
            )
            row = cur.fetchone()
    return (row[0] or "").strip() if row else ""


def registar_nova_sessao(external_id: str, session_uuid: uuid.UUID | None = None) -> uuid.UUID:
    uid = obter_ou_criar_utilizador(external_id)
    sid = session_uuid or uuid.uuid4()
    with _connect() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessoes_chat (utilizador_id, session_uuid)
                VALUES (%s, %s)
                """,
                (uid, str(sid)),
            )
    return sid


def listar_sessoes_utilizador(external_id: str, limite: int = 12) -> list[dict]:
    uid = obter_ou_criar_utilizador(external_id)
    with _connect() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT session_uuid::text AS session_uuid, resumo_sessao, criada_em, encerrada_em
                FROM sessoes_chat
                WHERE utilizador_id = %s
                ORDER BY criada_em DESC
                LIMIT %s
                """,
                (uid, limite),
            )
            return [dict(r) for r in cur.fetchall()]


def _actualizar_resumo_acumulado(utilizador_id: int, novo_texto: str) -> None:
    with _connect() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE resumo_acumulado
                SET texto = %s, actualizado_em = NOW()
                WHERE utilizador_id = %s
                """,
                (novo_texto.strip(), utilizador_id),
            )


def _merge_summaries(llm, texto_anterior: str, resumo_sessao: str) -> str:
    from langchain_core.messages import HumanMessage

    msg = HumanMessage(
        content=f"""Junta o **resumo acumulado** com o **resumo desta sessão** num único texto conciso (máximo ~800 palavras), em **português europeu**.
Preserva factos, preferências e decisões importantes. Elimina redundância e conversa trivial.

### Resumo acumulado anterior
{texto_anterior or '(vazio)'}

### Resumo desta sessão
{resumo_sessao}
"""
    )
    out = llm.invoke([msg])
    c = out.content
    return (c if isinstance(c, str) else str(c)).strip()


def encerrar_sessao_e_persistir_resumos(
    external_id: str,
    session_uuid: uuid.UUID,
    transcricao_conversa: str,
    llm_summarizer,
    llm_merger,
) -> tuple[str, str]:
    """Gera resumo da sessão, grava na linha `sessoes_chat`, funde no resumo acumulado do utilizador.

    Retorna (resumo_sessao, resumo_acumulado_actualizado).
    """
    from langchain_core.messages import HumanMessage

    uid = obter_ou_criar_utilizador(external_id)
    if not transcricao_conversa.strip():
        raise ValueError("transcricao_conversa vazia.")

    sum_msg = HumanMessage(
        content=f"""Resume a conversa abaixo para memória de longo prazo (3–8 bullets ou parágrafos curtos).
Foco: objectivos do utilizador, decisões, preferências, factos estáveis. Ignora cumprimentos vazios.

### Transcrição
{transcricao_conversa[:50000]}
"""
    )
    r_sess = llm_summarizer.invoke([sum_msg])
    resumo_sess = (r_sess.content if isinstance(r_sess.content, str) else str(r_sess.content)).strip()

    anterior = ler_resumo_acumulado(external_id)
    acumulado = (
        resumo_sess
        if not anterior.strip()
        else _merge_summaries(llm_merger, anterior, resumo_sess)
    )

    with _connect() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE sessoes_chat
                SET resumo_sessao = %s, encerrada_em = NOW()
                WHERE utilizador_id = %s AND session_uuid = %s
                """,
                (resumo_sess, uid, str(session_uuid)),
            )
    _actualizar_resumo_acumulado(uid, acumulado)
    return resumo_sess, acumulado
