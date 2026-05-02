"""Few-shot marketing: LangChain monta o prompt; Instructor + Gemini devolvem `Campanha`."""

from __future__ import annotations

import os
from functools import lru_cache

import instructor
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate

from app.schemas.campanha import ESTILO_PARA_INSTRUCAO, Campanha, GerarCampanhaEntrada


# --- Few-shot: exemplos fictícios que ancram formato + «identidade» FewShot Marketing ---
_EXEMPLOS_FEWSHOT = """
### Exemplo de campanha A (marca directa, tom profissional-quente)
- titulo: «O teu CRM não precisa de mais dashboards — precisa de menos drama»
- publico_alvo: líderes de vendas B2B em scale-ups europeias
- tom: confiante e irónico leve
- texto_post: «Durante anos vendemos a promessa do «360º vision». O resultado? Equipas a passar horas a actualizar campos que ninguém lê. Esta semana testámos uma abordagem radical: menos relatórios, mais uma pergunta — «o que muda hoje?». Spoiler: as reuniões encurtaram 20%.»
- chamada_para_acao: «Marca uma demo de 15 min e leva o checklist anti-reunião vazio.»
- hashtags: ["#SalesOps", "#B2B", "#Produtividade"]

### Exemplo de campanha B (tom didático, público técnico)
- titulo: «Embeddings não são magia — são geometria com pressa de entrega»
- publico_alvo: engenheiros de software a entrar em IA aplicada
- tom: didático, metaforas técnicas, zero mansplaining
- texto_post: «Se pensas em embeddings como «números misteriosos», vamos traduzir: são coordenadas num espaço onde «similar» significa perto. O teu retriever não «adivinha» — mede distâncias. Quando isso falha, normalmente o problema não é o modelo; é o chunking ou a limpeza dos dados.»
- chamada_para_acao: «Descarrega o notebook-base de chunking e valida o teu índice em 30 minutos.»
- hashtags: ["#RAG", "#Embeddings", "#ML"]

### Exemplo de campanha C (urgência ética, tom provocativo-controlado)
- titulo: «Compliance não é PowerPoint — é decisão sob pressão»
- publico_alvo: DPOs e security leads em SaaS
- tom: provocativo mas respeitoso
- texto_post: «Ninguém compra software de compliance por paixão. Compra porque o medo tem SLA. A diferença entre equipas que sobrevivem a auditorias e as que não sobrevivem não é o número de políticas — é ter trilhos executáveis quando o incidente chega às 2h da manhã.»
- chamada_para_acao: «Pede o template de runbook de incidente — sem formulários infinitos.»
- hashtags: ["#Compliance", "#Security", "#SaaS"]
"""

_SYSTEM_BASE = f"""És copywriter sénior da **FewShot Marketing** (Portugal — português europeu).
A marca vende campanhas que soam humanas, específicas e com voz própria — **não** copy genérica de LinkedIn automático.

Regras:
- Inspiras-te nos exemplos abaixo para **ritmo**, **estrutura mental** e **nível de concretização**.
- A saída será validada contra um schema: preenche todos os campos com texto original para o produto pedido.
- `hashtags`: 3 a 12 entradas; usa `#` no início de cada uma.
- Evita discriminação, claims médicos ilegais ou promessas numeradas inventadas.

{_EXEMPLOS_FEWSHOT}
"""

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _SYSTEM_BASE + "\n### Instruções de estilo neste pedido\n{instrucoes_estilo}\n"),
        (
            "human",
            "Novo briefing:\n"
            "- Produto/serviço: {produto}\n"
            "- Público-alvo: {publico}\n"
            "- Notas adicionais de tom: {tom}\n\n"
            "Gera **uma** campanha nova no mesmo espírito dos exemplos.",
        ),
    ]
)


def _messages_para_dicts(messages: list[BaseMessage]) -> list[dict[str, str]]:
    role_map = {"system": "system", "human": "user", "ai": "assistant"}
    out: list[dict[str, str]] = []
    for m in messages:
        r = role_map.get(getattr(m, "type", ""), "user")
        out.append({"role": r, "content": str(m.content)})
    return out


def _nome_modelo() -> str:
    raw = (
        os.environ.get("GEMINI_MODEL_EX04")
        or os.environ.get("GEMINI_MODEL")
        or "gemini-2.0-flash"
    )
    return raw.replace("models/", "").strip()


@lru_cache(maxsize=1)
def _cliente_instructor():
    """Cliente Instructor com provider Google (usa GOOGLE_API_KEY no ambiente)."""
    model = _nome_modelo()
    return instructor.from_provider(f"google/{model}")


def montar_instrucoes_estilo(body: GerarCampanhaEntrada) -> str:
    base = ESTILO_PARA_INSTRUCAO.get(body.estilo, ESTILO_PARA_INSTRUCAO["livre"])
    return base


def gerar_campanha(body: GerarCampanhaEntrada) -> Campanha:
    instrucoes = montar_instrucoes_estilo(body)
    msgs = _PROMPT.format_messages(
        produto=body.produto.strip(),
        publico=body.publico.strip(),
        tom=body.tom.strip(),
        instrucoes_estilo=instrucoes,
    )
    payload = _messages_para_dicts(msgs)
    client = _cliente_instructor()
    # Parâmetros extra dependem da versão do Instructor / provider; mantemos API mínima estável.
    return client.create(
        messages=payload,
        response_model=Campanha,
        max_retries=2,
    )
