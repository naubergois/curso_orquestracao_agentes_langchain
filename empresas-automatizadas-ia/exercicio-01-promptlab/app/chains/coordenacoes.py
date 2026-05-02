"""Orquestrações multi-agente entre perfis PromptLab (mesmo LLM, system prompts distintos)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from app.chains.promptlab_chain import gerar_resposta
from app.schemas.coordenacao import (
    CoordenacaoSaida,
    EtapaCoordenacao,
    ModoCoordenacao,
)
from app.schemas.pergunta import PerfilAssistente
from app.services.llm_factory import criar_chat
from app.services.prompts_coordenacao import SYSTEM_ROUTER, SYSTEM_SINTETIZADOR


def _invoke_custom(system: str, human: str, temperature: float = 0.35) -> str:
    llm = criar_chat(temperature=temperature)
    res: AIMessage = llm.invoke(
        [SystemMessage(content=system), HumanMessage(content=human)]
    )
    if isinstance(res.content, str):
        return res.content.strip()
    return str(res.content).strip()


class _RouterSchema(BaseModel):
    perfil_escolhido: str = Field(
        description="Um de: tecnico, professor, comercial, sarcastico_nerd"
    )
    motivo_breve: str = Field(description="Uma frase.")


def _sequencial_pipeline(pergunta: str) -> CoordenacaoSaida:
    etapas: list[EtapaCoordenacao] = []

    t1 = gerar_resposta(PerfilAssistente.tecnico, pergunta)
    etapas.append(
        EtapaCoordenacao(agente="tecnico", papel="Rascunho técnico inicial", saida=t1)
    )

    t2 = gerar_resposta(
        PerfilAssistente.professor,
        "Texto técnico do colega:\n"
        f"{t1}\n\n"
        "Reformula para um público intermédio: mantém rigor mas melhora pedagogia.",
    )
    etapas.append(
        EtapaCoordenacao(
            agente="professor",
            papel="Reformulação didática do output técnico",
            saida=t2,
        )
    )

    t3 = gerar_resposta(
        PerfilAssistente.comercial,
        "Versão didática:\n"
        f"{t2}\n\n"
        "Acrescenta valor para decisão de negócio (benefício, próximo passo sugerido) sem alterar factos.",
    )
    etapas.append(
        EtapaCoordenacao(
            agente="comercial",
            papel="Camada de valor e próximos passos",
            saida=t3,
        )
    )

    return CoordenacaoSaida(
        modo=ModoCoordenacao.sequencial_pipeline.value,
        resposta_final=t3,
        etapas=etapas,
    )


def _paralelo_sintese(pergunta: str) -> CoordenacaoSaida:
    etapas: list[EtapaCoordenacao] = []

    def _run(perfil: PerfilAssistente, papel: str) -> tuple[str, str, str]:
        texto = gerar_resposta(perfil, pergunta)
        return perfil.value, papel, texto

    specs = [
        (PerfilAssistente.tecnico, "Perspetiva técnica"),
        (PerfilAssistente.professor, "Perspetiva pedagógica"),
        (PerfilAssistente.comercial, "Perspetiva comercial"),
    ]
    blocos: dict[str, str] = {}

    with ThreadPoolExecutor(max_workers=3) as pool:
        fut_map = {
            pool.submit(_run, perfil, papel): (perfil, papel)
            for perfil, papel in specs
        }
        for fut in as_completed(fut_map):
            pid, papel, texto = fut.result()
            etapas.append(EtapaCoordenacao(agente=pid, papel=papel, saida=texto))
            blocos[pid] = texto

    _ordem = {"tecnico": 0, "professor": 1, "comercial": 2}
    etapas.sort(key=lambda e: _ordem.get(e.agente, 99))

    pacote = (
        f"Pergunta original:\n{pergunta}\n\n"
        f"### Técnico\n{blocos['tecnico']}\n\n"
        f"### Professor\n{blocos['professor']}\n\n"
        f"### Comercial\n{blocos['comercial']}"
    )
    final = _invoke_custom(
        SYSTEM_SINTETIZADOR,
        "Funde as perspetivas numa resposta única ao cliente:\n\n" + pacote,
        temperature=0.3,
    )
    etapas.append(
        EtapaCoordenacao(
            agente="sintetizador",
            papel="Fusão das três perspetivas paralelas",
            saida=final,
        )
    )

    return CoordenacaoSaida(
        modo=ModoCoordenacao.paralelo_sintese.value,
        resposta_final=final,
        etapas=etapas,
    )


def _debate_critico(pergunta: str) -> CoordenacaoSaida:
    etapas: list[EtapaCoordenacao] = []

    r1 = gerar_resposta(PerfilAssistente.tecnico, pergunta)
    etapas.append(
        EtapaCoordenacao(agente="tecnico", papel="Primeira resposta técnica", saida=r1)
    )

    critica = gerar_resposta(
        PerfilAssistente.sarcastico_nerd,
        "Pergunta:\n"
        f"{pergunta}\n\n"
        "Resposta técnica do colega:\n"
        f"{r1}\n\n"
        "Identifica lacunas, ambiguidades ou otimismo excessivo. Mantém humor leve.",
    )
    etapas.append(
        EtapaCoordenacao(
            agente="sarcastico_nerd",
            papel="Crítica construtiva / segunda opinião",
            saida=critica,
        )
    )

    r2 = gerar_resposta(
        PerfilAssistente.tecnico,
        "Pergunta:\n"
        f"{pergunta}\n\n"
        "A minha primeira resposta:\n"
        f"{r1}\n\n"
        "Crítica recebida:\n"
        f"{critica}\n\n"
        "Resposta técnica **revisada** que integra o feedback.",
    )
    etapas.append(
        EtapaCoordenacao(
            agente="tecnico",
            papel="Revisão técnica pós-debate",
            saida=r2,
        )
    )

    return CoordenacaoSaida(
        modo=ModoCoordenacao.debate_critico.value,
        resposta_final=r2,
        etapas=etapas,
    )


def _router_inteligente(pergunta: str) -> CoordenacaoSaida:
    llm = criar_chat(temperature=0.1).with_structured_output(_RouterSchema)
    decisao: _RouterSchema = llm.invoke(
        [
            SystemMessage(content=SYSTEM_ROUTER),
            HumanMessage(content=pergunta),
        ]
    )
    etapas = [
        EtapaCoordenacao(
            agente="router",
            papel="Escolha do perfil único",
            saida=f"{decisao.perfil_escolhido}: {decisao.motivo_breve}",
        )
    ]
    raw = (
        decisao.perfil_escolhido.strip()
        .lower()
        .replace("á", "a")
        .replace("í", "i")
        .replace("-", "_")
        .replace(" ", "_")
    )
    aliases = {
        "sarcastico": "sarcastico_nerd",
        "nerd": "sarcastico_nerd",
        "comercial_vendas": "comercial",
    }
    raw = aliases.get(raw, raw)
    try:
        perfil = PerfilAssistente(raw)
    except ValueError:
        perfil = PerfilAssistente.tecnico
        etapas.append(
            EtapaCoordenacao(
                agente="router",
                papel="Fallback",
                saida="Perfil inválido devolvido pelo router — usado `tecnico`.",
            )
        )

    texto = gerar_resposta(perfil, pergunta)
    etapas.append(
        EtapaCoordenacao(
            agente=perfil.value,
            papel="Resposta final pelo perfil escolhido",
            saida=texto,
        )
    )

    return CoordenacaoSaida(
        modo=ModoCoordenacao.router_inteligente.value,
        resposta_final=texto,
        etapas=etapas,
    )


def _refinamento_triplo(pergunta: str) -> CoordenacaoSaida:
    """Professor abre (acessível) → técnico endurece rigor → comercial fecha."""
    etapas: list[EtapaCoordenacao] = []

    s1 = gerar_resposta(PerfilAssistente.professor, pergunta)
    etapas.append(
        EtapaCoordenacao(
            agente="professor",
            papel="Primeira explicação didática",
            saida=s1,
        )
    )

    s2 = gerar_resposta(
        PerfilAssistente.tecnico,
        "Versão didática inicial:\n"
        f"{s1}\n\n"
        "Verifica rigor técnico, corrige imprecisões e acrescenta nuances necessárias.",
    )
    etapas.append(
        EtapaCoordenacao(
            agente="tecnico",
            papel="Endurecimento técnico / correções",
            saida=s2,
        )
    )

    s3 = gerar_resposta(
        PerfilAssistente.comercial,
        "Versão técnica refinada:\n"
        f"{s2}\n\n"
        "Apresenta ao cliente final de forma clara, com ênfase em valor e próximo passo.",
    )
    etapas.append(
        EtapaCoordenacao(
            agente="comercial",
            papel="Empacotamento final para cliente",
            saida=s3,
        )
    )

    return CoordenacaoSaida(
        modo=ModoCoordenacao.refinamento_triplo.value,
        resposta_final=s3,
        etapas=etapas,
    )


def executar_coordenacao(modo: ModoCoordenacao, pergunta: str) -> CoordenacaoSaida:
    if modo == ModoCoordenacao.sequencial_pipeline:
        return _sequencial_pipeline(pergunta)
    if modo == ModoCoordenacao.paralelo_sintese:
        return _paralelo_sintese(pergunta)
    if modo == ModoCoordenacao.debate_critico:
        return _debate_critico(pergunta)
    if modo == ModoCoordenacao.router_inteligente:
        return _router_inteligente(pergunta)
    if modo == ModoCoordenacao.refinamento_triplo:
        return _refinamento_triplo(pergunta)
    raise ValueError(modo)


DESCRICOES_MODOS: dict[str, str] = {
    ModoCoordenacao.sequencial_pipeline.value: (
        "Pipeline sequencial: técnico → professor (didática) → comercial (valor)."
    ),
    ModoCoordenacao.paralelo_sintese.value: (
        "Paralelo: três perfis respondem em paralelo; um sintetizador funde num texto único."
    ),
    ModoCoordenacao.debate_critico.value: (
        "Debate: técnico responde, perfil sarcástico critica, técnico revisa."
    ),
    ModoCoordenacao.router_inteligente.value: (
        "Router LLM escolhe um único perfil; esse agente responde."
    ),
    ModoCoordenacao.refinamento_triplo.value: (
        "Refinamento: professor abre → técnico corrige rigor → comercial fecha."
    ),
}
