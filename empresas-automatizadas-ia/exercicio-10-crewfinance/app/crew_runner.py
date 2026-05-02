"""CrewFinance — CrewAI + Gemini (via string de modelo LiteLLM)."""

from __future__ import annotations

import os

from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel, Field


class PedidoFinanceiro(BaseModel):
    pedido: str = Field(..., min_length=20, description="Briefing para análise financeira fictícia.")


def _llm() -> str:
    m = (
        os.environ.get("GEMINI_MODEL_EX10")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    ).replace("models/", "")
    return f"gemini/{m}"


def executar_crew(pedido: str) -> str:
    llm = _llm()

    analista = Agent(
        role="Analista financeiro",
        goal="Extrair factos e riscos quantitativos do briefing.",
        backstory="Especialista em PME e fluxo de caixa; português europeu.",
        llm=llm,
        verbose=False,
    )
    critico = Agent(
        role="Crítico de raciocínio",
        goal="Encontrar lacunas, premissas fracas e enviesamentos.",
        backstory="Perfil cético-constructivo; não aceita números sem fonte no texto.",
        llm=llm,
        verbose=False,
    )
    redator = Agent(
        role="Redator executivo",
        goal="Transformar análise+crítica num relatório curto e acionável.",
        backstory="Escreve para conselho de administração fictício.",
        llm=llm,
        verbose=False,
    )
    auditor = Agent(
        role="Auditor de premissas",
        goal="Questionar explicitamente premissas frágeis (desafio extra).",
        backstory="Foco em pressupostos não declarados e cenários alternativos.",
        llm=llm,
        verbose=False,
    )

    t_analise = Task(
        description=f"Briefing:\n{pedido}\n\nProduz análise estruturada (marcadores).",
        expected_output="Lista de achados e riscos em PT-PT.",
        agent=analista,
    )
    t_critica = Task(
        description="Critica a análise anterior; lista falhas e perguntas em aberto.",
        expected_output="Crítica pontual em PT-PT.",
        agent=critico,
        context=[t_analise],
    )
    t_auditoria = Task(
        description="Lista premissas frágeis levantadas pela crítica e propõe checks.",
        expected_output="Secção 'Premissas a validar'.",
        agent=auditor,
        context=[t_analise, t_critica],
    )
    t_relatorio = Task(
        description="Integra análise, crítica e auditoria num relatório final ≤ 400 palavras.",
        expected_output="Relatório markdown simples.",
        agent=redator,
        context=[t_analise, t_critica, t_auditoria],
    )

    crew = Crew(
        agents=[analista, critico, auditor, redator],
        tasks=[t_analise, t_critica, t_auditoria, t_relatorio],
        process=Process.sequential,
        verbose=False,
    )
    return str(crew.kickoff(inputs={})).strip()
