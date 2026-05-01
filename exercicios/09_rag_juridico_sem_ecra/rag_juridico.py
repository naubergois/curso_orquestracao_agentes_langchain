"""Cadeia RAG (LCEL) sobre Chroma — exercício 9."""

from __future__ import annotations

from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


def formatar_documentos(docs: list[Document]) -> str:
    blocos: list[str] = []
    for d in docs:
        meta = d.metadata.get("source", "?")
        blocos.append(f"[Fonte: {meta}]\n{d.page_content}")
    return "\n\n---\n\n".join(blocos)


def construir_cadeia_rag(llm: Any, retriever) -> Any:
    """Retriever com `invoke(str)` que devolve lista de `Document`."""

    def _contexto(pergunta: str) -> str:
        docs = retriever.invoke(pergunta)
        return formatar_documentos(docs)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "És um assistente de **estudo** em português europeu. Responde só com base no "
                "contexto fornecido. Se o contexto não bastar, diz explicitamente que não há "
                "informação suficiente nos excertos. Não inventes artigos de lei nem jurisprudência.",
            ),
            (
                "human",
                "Contexto (excertos de PDFs pedagógicos):\n{contexto}\n\nPergunta: {pergunta}",
            ),
        ]
    )

    return (
        RunnablePassthrough.assign(contexto=RunnableLambda(lambda x: _contexto(x["pergunta"])))
        | prompt
        | llm
        | StrOutputParser()
    )


def construir_cadeia_rag_hibrido(
    llm: Any,
    retriever,
    *,
    limite_sql: int = 5,
) -> Any:
    """RAG que junta **processos** em PostgreSQL (estruturado) com **excertos PDF** no Chroma (não estruturado)."""

    def _pdf(pergunta: str) -> str:
        docs = retriever.invoke(pergunta)
        return formatar_documentos(docs)

    def _sql(pergunta: str) -> str:
        from db_processos import contexto_sql_para_rag

        return contexto_sql_para_rag(pergunta, limite=limite_sql)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "És um assistente de **estudo** em português europeu. Tens duas fontes independentes: "
                "**(A) quadro processual fictício** em base relacional (PostgreSQL) e **(B) excertos de PDFs "
                "pedagógicos** recuperados por similaridade (Chroma). Relaciona-as quando fizer sentido — por "
                "exemplo, os PDFs associados a cada processo indicam o tema dos anexos didáticos que podem "
                "apoiar a resposta. Se uma das fontes não for relevante, indica-o sem inventar factos. "
                "Não inventes números de processo nem jurisprudência real.",
            ),
            (
                "human",
                "**(A) Dados estruturados — processos (PostgreSQL)**\n{dados_processos}\n\n"
                "**(B) Texto não estruturado — excertos de PDFs (RAG vetorial)**\n{contexto_pdf}\n\n"
                "**Pergunta:** {pergunta}",
            ),
        ]
    )

    return (
        RunnablePassthrough.assign(
            contexto_pdf=RunnableLambda(lambda x: _pdf(x["pergunta"])),
            dados_processos=RunnableLambda(lambda x: _sql(x["pergunta"])),
        )
        | prompt
        | llm
        | StrOutputParser()
    )
