#!/usr/bin/env python3
"""Gera docs/*.md detalhados e exercicio_NN_sem_ecra.ipynb completos para as 20 empresas."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EX = [
    (1, "exercicio-01-promptlab", "PromptLab Consultoria", "prompt"),
    (2, "exercicio-02-atendimento-360", "Atendimento 360", "memory"),
    (3, "exercicio-03-eduprompt", "EduPrompt Academy", "lcel"),
    (4, "exercicio-04-fewshot-marketing", "FewShot Marketing", "fewshot"),
    (5, "exercicio-05-parser-juridico", "Parser Jurídico", "legal"),
    (6, "exercicio-06-rag-juridico", "RAG Jurídico", "rag"),
    (7, "exercicio-07-busca-semantica", "Busca Semântica Ltda.", "faiss"),
    (8, "exercicio-08-govbot", "GovBot Cidadão", "govbot"),
    (9, "exercicio-09-helpdesk-agent", "HelpDesk Agent", "agent"),
    (10, "exercicio-10-crewfinance", "CrewFinance", "crew"),
    (11, "exercicio-11-autogen-research", "AutoGen Research Lab", "autogen"),
    (12, "exercicio-12-semantic-kernel-office", "Semantic Kernel Office", "sk"),
    (13, "exercicio-13-dspy-optimizer", "DSPy Optimizer", "dspy"),
    (14, "exercicio-14-tutorgraph", "TutorGraph", "tutorgraph"),
    (15, "exercicio-15-auditoriagraph", "AuditoriaGraph", "audit"),
    (16, "exercicio-16-observaai", "ObservaAI", "observe"),
    (17, "exercicio-17-localbot", "LocalBot", "local"),
    (18, "exercicio-18-api-agent-factory", "API Agent Factory", "apifact"),
    (19, "exercicio-19-interface-agent-studio", "Interface Agent Studio", "ui"),
    (20, "exercicio-20-empresa-autonoma-integrada", "Empresa Autónoma Integrada", "mega"),
]


def md_cell(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [text]}


def code_cell(code: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [code],
    }


def nb_meta() -> dict:
    return {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"},
    }


SETUP_PY = '''from pathlib import Path
import os
from dotenv import load_dotenv

EX_ROOT = Path.cwd().resolve()
REPO_ROOT = EX_ROOT.parent.parent

load_dotenv(REPO_ROOT / ".env", override=False)
load_dotenv(EX_ROOT / ".env", override=True)

if not (os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")):
    raise RuntimeError("Defina GOOGLE_API_KEY no .env na raiz do repositório.")

print("OK — Repo:", REPO_ROOT)
print("OK — Exercício:", EX_ROOT)
'''


def doc_arquitetura(n: int, nome: str, tipo: str) -> str:
    blocos = {
        "prompt": """## Visão técnica
Entrada validada (Pydantic) → seleção de perfil → `SystemMessage` fixo por perfil → `HumanMessage` com a pergunta → modelo Gemini → texto da resposta.

## Componentes
- **Interface sem ecrã:** notebook executável célula a célula.
- **Opcional:** API FastAPI em `app/` espelha o mesmo contrato JSON (`./run_api.sh`).

## Fluxo de dados
```text
JSON/células → Schema perfil+pergunta → Prompt sistema → LLM → AIMessage → texto
```

## Extensões
Rate limiting, cache por hash (perfil+pergunta), testes unitários com LLM mockado.""",
        "memory": """## Visão técnica
Estado conversacional como lista ordenada de mensagens `{role, content}` reconstruída em mensagens LangChain antes de cada invocação.

## Por que lista em vez de memória automática?
Control explícito do que entra no contexto, exportação trivial (.json/.txt) e equivalência pedagógica ao `st.session_state`.

## Fluxo
```text
histórico → + user → SystemMessage + Human/AI alternados → Gemini → nova AIMessage → append histórico
```

## Opcional Streamlit
`app/main.py` + `./run_streamlit.sh` para UI; o notebook é a versão auditável.""",
        "lcel": """## Visão técnica
Três pipelines LCEL independentes partilham modelo e parser de texto: explicação, exercícios, resumo.

## Fluxo
```text
(tema, nível) → PromptTemplate → ChatModel → StrOutputParser → Markdown
```

## Reutilização
Encadear com `RunnableParallel` para gerar pacote educacional numa única chamada paralela (opcional).""",
        "fewshot": """## Visão técnica
Few-shot fixa exemplos no prompt; saída estruturada via `with_structured_output(Pydantic)` do modelo LangChain.

## Fluxo
```text
exemplos + pedido → LLM → objeto Campanha validado
```""",
        "legal": """## Visão técnica
Extração orientada por schema Pydantic; o modelo preenche campos a partir de texto livre (simulação — não é parecer jurídico real).

## Fluxo
```text
texto cliente → prompt estruturado → JSON → validação Pydantic → eventual correção de tipos
```""",
        "rag": """## Visão técnica
Fragmentação de documentos fictícios → embeddings (Gemini) → vetor em memória (Chroma) → retriever → prompt com contexto → resposta fundamentada.

## Componentes
- **Loader:** strings/ficheiros em `app/data/`.
- **Vector store:** Chroma persistente em disco opcional; aqui uso em memória para notebook.""",
        "faiss": """## Visão técnica
Sentence-Transformers (`all-MiniLM-L6-v2`) para embeddings locais → índice FAISS `IndexFlatIP` com vetores L2-normalizados → consulta por similaridade coseno.

## Fluxo
```text
corpus → encode → FAISS.add → query encode → search → top-k + scores
```""",
        "govbot": """## Visão técnica
RAG leve sobre documentos públicos fictícios (IPTU, iluminação, alvarás) com classificação auxiliar da intenção via LLM.

## Nota Haystack + Qdrant
Produção típica usaria Haystack 2.x + Qdrant; este notebook implementa o mesmo *contrato* pedagógico com LangChain + texto recuperado simples.""",
        "agent": """## Visão técnica
Agente ReAct simplificado: modelo escolhe entre ferramentas Python (`@tool`) que simulam ticketing.

## Fluxo
```text
mensagem → agent → tool calls → observações → resposta final
```""",
        "crew": """## Visão técnica
**CrewAI** é o alvo do enunciado; aqui mostramos **simulação sequencial** com três prompts especializados (analista → crítico → redator) reproduzindo o fluxo sem dependência obrigatória CrewAI no contentor.

## Extensão
Substituir por `crewai` real quando `pip install crewai` estiver disponível no ambiente.""",
        "autogen": """## Visão técnica
Debate multiagente com AutoGen é o alvo; o notebook usa **rodadas explícitas** três papéis (pesquisador, crítico, sintetizador) com chamadas Gemini separadas e histórico concatenado.""",
        "sk": """## Visão técnica
Semantic Kernel organiza *skills* (funções semânticas + planners). Em Python instala-se `semantic-kernel`.

Este notebook documenta o contrato e oferece fallback: três funções puramente LLM com prompts nomeados como skills.""",
        "dspy": """## Visão técnica
DSPy formaliza assinaturas e otimização de prompts; depende de `dspy-ai` e de tracing opcional.

Notebook: comparação manual duas variantes de instrução sobre o mesmo conjunto de perguntas (métrica simples).""",
        "tutorgraph": """## Visão técnica
Grafo pedagógico: diagnóstico → explicar → exercitar → corrigir → revisão. Implementação com `langgraph` quando instalado; caso contrário fluxo Python explícito.""",
        "audit": """## Visão técnica
RAMificações por nível de risco (baixo/médio/alto) com saídas diferentes; LangSmith pode registar traces (`LANGCHAIN_TRACING_V2`).""",
        "observe": """## Visão técnica
Experimento três prompts com medição tempo + custo estimado (tokens aproximados) + logging estruturado em lista Python exportável.""",
        "local": """## Visão técnica
Ollama expõe API compatível OpenAI em `localhost:11434`. LangChain `ChatOllama` ou endpoint compatível.

Notebook tenta `ChatOllama`; se falhar, documenta fallback Gemini apenas para não bloquear.""",
        "apifact": """## Visão técnica
Três operações HTTP (`/chat`, `/classificar`, `/resumir`) podem ser testadas com `httpx` contra API em execução **ou** com funções puras no notebook espelhando as chains.""",
        "ui": """## Visão técnica
Comparação Streamlit vs Gradio: mesmo *core* (`def responder(texto)->str`) invocado por duas camadas UI — aqui apenas o núcleo no notebook + instruções para lançar apps.""",
        "mega": """## Visão técnica
Integração: classificação → grafo decisão → RAG → relatório → log. Notebook orquestra módulos como funções encadeadas (protótipo monolítico legível).""",
    }
    corpo = blocos.get(tipo, "")
    return f"# Arquitetura — Exercício {n:02d}: {nome}\n\n{corpo}\n"


def doc_teorica(n: int, nome: str, tipo: str) -> str:
    intro = f"# Explicação teórica — Exercício {n:02d}: {nome}\n\n"
    temas = {
        "prompt": """## System prompt vs user prompt
O *system* define papel, tom e limites; o *user* traz a pergunta concreta. Variar só o system mantém comparável o comportamento do modelo entre perfis.

## Pydantic na entrada
Enums impedem valores de perfil inválidos; `Field` documenta limites e ajuda OpenAPI quando há API.

## AIMessage
É o envelope LangChain para saída do modelo; extrai-se `content` para texto simples.""",
        "memory": """## Memória de sessão
Em Streamlit usa-se `st.session_state`; no notebook a lista `historico` é o mesmo conceito sem UI.

## Context window
Históricos longos enchem o contexto — truncar ou resumir é necessário em produção.""",
        "lcel": """## LCEL
`|`, `RunnableSequence`, prompts tipados e parsers tornam pipelines testáveis e composáveis.

## StrOutputParser
Normaliza a saída do chat para `str`, útil para injetar Markdown.""",
        "fewshot": """## Few-shot prompting
Exemplos no prompt ancram estilo e formato; útil para identidade de marca.

## Saída estruturada
Modelos modernos expõem JSON schema; Pydantic valida e documenta.""",
        "legal": """## Extração de informação
Diferente de classificação única: vários campos simultâneos com opcionalidade e enums controlados.

## Guardrails
Em produção usar validações adicionais e bloqueio de inputs não jurídicos.""",
        "rag": """## RAG
Recuperação aumenta a factualidade face ao só LLM; chunks balanceiam granularidade vs contexto.

## Embeddings
Escolha do modelo de embedding afeta recall semântico.""",
        "faiss": """## Similaridade vetorial
Produto interno após normalização L2 equivale a cosine similarity.

## Keyword vs semântica
BM25 vs embeddings capturam comportamentos diferentes demonstráveis lado a lado.""",
        "govbot": """## QA com fontes
Responder com trecho citado aumenta confiança e auditoria.

## Classificação de demanda
Router semântico encaminha fluxos especializados.""",
        "agent": """## Agentes e ferramentas
O modelo decide *quando* chamar funções; ferramentas devem ser idempotentes quando possível.

## Observabilidade
Logar tool calls facilita debugging.""",
        "crew": """## Papéis e tarefas
Separar análise, crítica e redação reduz alucinação consolidada e melhora relatórios.""",
        "autogen": """## Debate multiagente
Crítica antecipada reduz confiança excessiva em primeira versão.""",
        "sk": """## Skills e planners
Skills encapsulam capacidades; planners descrevem decomposição de objetivos.""",
        "dspy": """## Otimização de prompts
DSPy trata prompts como parâmetros sujeitos a métricas declaradas.""",
        "tutorgraph": """## Grafos de estado
Estado partilhado e arestas condicionais modelam pedagogia adaptativa.""",
        "audit": """## Ramificações de risco
Baixo risco automatiza; alto exige human-in-the-loop.""",
        "observe": """## Tracing e custo
Sem métricas não há melhoria sistemática de prompts.""",
        "local": """## Dados sensíveis
Modelos locais reduzem exposição; há trade-off qualidade vs latência.""",
        "apifact": """## APIs como produto
Contratos estáveis (`POST` JSON) habilitam integrações.""",
        "ui": """## Prototipagem
Streamlit rápido para dados; Gradio forte em demos ML.""",
        "mega": """## Orquestração
Projeto final combina padrões anteriores num pipeline único.""",
    }
    return intro + temas.get(tipo, "(Ver enunciado global do curso.)")


def doc_passo(n: int, nome: str, folder: str) -> str:
    return f"""# Passo a passo — Exercício {n:02d}: {nome}

## 1. Ambiente
1. Na **raiz do repositório**, configure `.env` com `GOOGLE_API_KEY` (e variáveis opcionais do enunciado).
2. Na pasta `{folder}`, execute `./run.sh` para Jupyter Lab.

## 2. Notebook
Abra e execute na ordem **`exercicio_{n:02d}_sem_ecra.ipynb`** (kernel Python 3).

## 3. Artefactos gerados
Alguns notebooks escrevem ficheiros (`historico_export.json`, índices em `./tmp_vector`, etc.). Não commite dados sensíveis.

## 4. Modos opcionais
- **API / Streamlit:** ver `run_api.sh` ou `run_streamlit.sh` conforme pasta.

## 5. Parar containers
```bash
docker compose -f docker-compose.jupyter.yml down
```
"""


def doc_resultados(n: int, nome: str, tipo: str) -> str:
    return f"""# Resultados esperados — Exercício {n:02d}: {nome}

## Funcional
- Todas as células críticas executam sem excepção com `.env` válido.
- Saídas coerentes com o tipo `{tipo}` (ver notebook).

## Qualidade
- Textos em **português europeu** quando aplicável ao persona.
- Respostas RAG citam ou baseiam-se nos trechos recuperados.

## Avaliação
- Consegue explicar cada bloco do notebook a um colega.
- Identifica limitações (quota API, custo, ausência de frameworks opcionais).

## Evolução
Substituir simulações (ex.: Crew sequencial) pelos frameworks completos indicados no enunciado quando o ambiente permitir `pip install`.
"""


def build_notebook(n: int, nome: str, tipo: str) -> dict:
    cells: list[dict] = []
    cells.append(md_cell(f"# Exercício {n:02d} — {nome}\n\n**Entrega sem ecrã:** código executável abaixo + documentação em `docs/`.\n"))
    cells.append(md_cell("## 0. Ambiente e caminhos"))
    cells.append(code_cell(SETUP_PY))

    if tipo == "prompt":
        cells += [
            md_cell("## 1. Validação com Pydantic (espelha `app/schemas/pergunta.py`)"),
            code_cell(
                """from enum import Enum
from pydantic import BaseModel, Field

class Perfil(str, Enum):
    tecnico = "tecnico"
    professor = "professor"
    comercial = "comercial"
    sarcastico_nerd = "sarcastico_nerd"

class PerguntaEntrada(BaseModel):
    perfil: Perfil
    pergunta: str = Field(..., min_length=1, max_length=8000)

class RespostaSaida(BaseModel):
    perfil: str
    resposta: str

ex = PerguntaEntrada(perfil="professor", pergunta="O que é um agente de IA?")
print(ex.model_dump_json(indent=2))
"""
            ),
            md_cell("## 2. Perfis e LangChain (espelha `app/services/prompts.py` + chain)"),
            code_cell(
                """from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os

PERFIS = {
    "tecnico": "Consultor técnico sénior. Português europeu, preciso, estruturado.",
    "professor": "Professor didático. Português europeu, analogias e passos curtos.",
    "comercial": "Atendente comercial. Português europeu, cordial, focado em valor.",
    "sarcastico_nerd": "Consultor nerd sarcástico mas educado; mantém utilidade.",
}

def responder(perfil: str, pergunta: str) -> str:
    llm = ChatGoogleGenerativeAI(
        model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
        temperature=0.35,
    )
    msgs = [SystemMessage(content=PERFIS[perfil]), HumanMessage(content=pergunta)]
    ai: AIMessage = llm.invoke(msgs)
    return ai.content if isinstance(ai.content, str) else str(ai.content)

for p in ("tecnico", "professor", "comercial", "sarcastico_nerd"):
    body = PerguntaEntrada(perfil=p, pergunta="O que é RAG?")  # type: ignore[arg-type]
    out = RespostaSaida(perfil=body.perfil.value, resposta=responder(body.perfil.value, body.pergunta))
    print("---", out.perfil, "---")
    print(out.resposta[:900])
"""
            ),
        ]

    elif tipo == "memory":
        cells += [
            md_cell("## 1. Loop de conversa com histórico"),
            code_cell(
                """from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import json
import os
from pathlib import Path

SYSTEM = (
    "Assistente Atendimento 360. Português europeu, cordial. Usa o histórico."
)

def montar_mensagens(hist: list[dict]) -> list:
    out = [SystemMessage(content=SYSTEM)]
    for m in hist:
        if m["role"] == "user":
            out.append(HumanMessage(content=m["content"]))
        else:
            out.append(AIMessage(content=m["content"]))
    return out

def turno(hist: list[dict], texto: str) -> list[dict]:
    hist = [*hist, {"role": "user", "content": texto}]
    llm = ChatGoogleGenerativeAI(
        model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
        temperature=0.35,
    )
    ai: AIMessage = llm.invoke(montar_mensagens(hist))
    reply = ai.content if isinstance(ai.content, str) else str(ai.content)
    return [*hist, {"role": "assistant", "content": reply}]

h: list[dict] = []
h = turno(h, "O meu nome é João.")
h = turno(h, "Qual é o meu nome?")
print(json.dumps(h, ensure_ascii=False, indent=2))

Path("historico_export.json").write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")
print("Exportado historico_export.json")
"""
            ),
        ]

    elif tipo == "lcel":
        cells += [
            md_cell("## 1. Três chains LCEL (explicação, exercícios, resumo)"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.25,
)

def chain_explicacao():
    p = ChatPromptTemplate.from_messages([
        ("system", "És um autor educacional. Português europeu."),
        ("human", "Explica o tema {{tema}} para nível {{nivel}} em 2–3 parágrafos."),
    ])
    return p | llm | StrOutputParser()

def chain_exercicios():
    p = ChatPromptTemplate.from_messages([
        ("system", "Cria exercícios claros. Português europeu."),
        ("human", "Lista 5 exercícios sobre {{tema}} (nível {{nivel}}). Numera 1–5."),
    ])
    return p | llm | StrOutputParser()

def chain_resumo():
    p = ChatPromptTemplate.from_messages([
        ("system", "Resume de forma telegráfica. Português europeu."),
        ("human", "Resume {{tema}} para {{nivel}} em bullet points."),
    ])
    return p | llm | StrOutputParser()

tema, nivel = "RAG", "iniciante"
print("=== EXPLICAÇÃO ===\\n", chain_explicacao().invoke({"tema": tema, "nivel": nivel}))
print("\\n=== EXERCÍCIOS ===\\n", chain_exercicios().invoke({"tema": tema, "nivel": nivel}))
print("\\n=== RESUMO ===\\n", chain_resumo().invoke({"tema": tema, "nivel": nivel}))
"""
            ),
            md_cell("## 2. Desafio extra — narrativa sarcástica nerd"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

p = ChatPromptTemplate.from_messages([
    ("system", "Humor nerd corporativo leve; continua correto tecnicamente."),
    ("human", "Narra em 1 parágrafo sarcástico o tema {{tema}} para {{nivel}}."),
])
sarc = p | llm | StrOutputParser()
print(sarc.invoke({"tema": "RAG", "nivel": "iniciante"}))
"""
            ),
        ]

    elif tipo == "fewshot":
        cells += [
            md_cell("## 1. Few-shot + saída estruturada Pydantic"),
            code_cell(
                """from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

class Campanha(BaseModel):
    titulo: str
    publico_alvo: str
    tom: str
    texto_post: str
    chamada_para_acao: str
    hashtags: list[str] = Field(default_factory=list)

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.6,
)
structured = llm.with_structured_output(Campanha)

exemplos = \"\"\"Exemplo A (tom didático):
Título: Curso X para devs
Público: engenheiros
Tom: didático
Post: ...
CTA: Inscreve-te
Hashtags: #curso #ia

Exemplo B (tom provocativo):
Título: IA sem drama
...
\"\"\"

prompt = ChatPromptTemplate.from_messages([
    ("system", "Segue o estilo dos exemplos; português europeu."),
    ("human", exemplos + "\\n\\nCria campanha para:\\nProduto: {produto}\\nTom desejado: {tom}\\nPúblico: {publico}"),
])
chain = prompt | structured

camp = chain.invoke({
    "produto": "curso de agentes inteligentes",
    "tom": "didático e levemente sarcástico",
    "publico": "profissionais de tecnologia",
})
print(camp.model_dump_json(indent=2))
"""
            ),
        ]

    elif tipo == "legal":
        cells += [
            md_cell("## 1. Schema de análise jurídica (fictício)"),
            code_cell(
                """from enum import Enum
from pydantic import BaseModel, Field

class Risco(str, Enum):
    baixo = "baixo"
    medio = "medio"
    alto = "alto"

class Prioridade(str, Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"

class AnaliseDemanda(BaseModel):
    tipo_demanda: str
    partes: list[str] = Field(default_factory=list)
    prazo_mencionado: str | None = None
    risco: Risco
    prioridade: Prioridade
    resumo: str
"""
            ),
            md_cell("## 2. Extração com LLM + validação"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.1,
)
structured = llm.with_structured_output(AnaliseDemanda)

texto = \"\"\"Exmo. Advogado, somos a empresa Alfa e a Beta não entregou o módulo contratado.
O contrato prevê resposta em 10 dias. Pedimos análise de incumprimento.\"\"\"

p = ChatPromptTemplate.from_messages([
    ("system", "Extrai campos do schema; português europeu; não inventes factos sem indício no texto."),
    ("human", "{texto}"),
])
chain = p | structured
res = chain.invoke({"texto": texto})
print(res.model_dump_json(indent=2))
"""
            ),
            md_cell("## 3. Desafio — bloquear não jurídico"),
            code_cell(
                """def parece_juridico(t: str) -> bool:
    chave = ("contrato", "prazo", "autor", "réu", "incumprimento", "demanda", "cláusula", "exmo")
    tl = t.lower()
    return any(k in tl for k in chave)

lixo = "Receita de bolo de chocolate"
if not parece_juridico(lixo):
    print("BLOQUEADO: texto não parece jurídico.")
else:
    print(structured.invoke({"texto": lixo}))
"""
            ),
        ]

    elif tipo == "rag":
        cells += [
            md_cell("## 1. Documentos fictícios e chunking simples"),
            code_cell(
                """DOCS = [
    {"id": "contrato_servicos.txt", "texto": "Cláusula 7: prazo de resposta a pedidos de suporte é de 5 dias úteis."},
    {"id": "politica_privacidade.txt", "texto": "Os dados são conservados por 24 meses após termo do contrato."},
]
CHUNK_SIZE = 220

def chunk(doc: dict) -> list[dict]:
    t = doc["texto"]
    out = []
    for i in range(0, len(t), CHUNK_SIZE):
        out.append({"id": doc["id"], "chunk": t[i : i + CHUNK_SIZE]})
    return out

chunks = [c for d in DOCS for c in chunk(d)]
len(chunks), chunks[:2]
"""
            ),
            md_cell("## 2. Embeddings Gemini + Chroma (em memória)"),
            code_cell(
                """from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os

emb = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
vectordb = Chroma.from_documents(
    [Document(page_content=c["chunk"], metadata={"fonte": c["id"]}) for c in chunks],
    embedding=emb,
)
retriever = vectordb.as_retriever(search_kwargs={"k": 2})

pergunta = "Qual é o prazo de resposta a pedidos de suporte?"
docs = retriever.invoke(pergunta)
docs
"""
            ),
            md_cell("## 3. Geração com contexto"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.2,
)
ctx = "\\n".join(f"[{d.metadata.get('fonte')}] {d.page_content}" for d in docs)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Responde só com base no contexto; se faltar info, diz-o. Português europeu."),
    ("human", "Contexto:\\n{ctx}\\n\\nPergunta: {q}"),
])
chain = prompt | llm | StrOutputParser()
print(chain.invoke({"ctx": ctx, "q": pergunta}))
"""
            ),
        ]

    elif tipo == "faiss":
        cells += [
            md_cell("## 1. Instalar dependências locais de embedding + FAISS"),
            code_cell("# Descomente na primeira execução se faltar:\\n# %pip install -q sentence-transformers faiss-cpu"),
            code_cell(
                """from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

fnames = ["politica_suporte.txt", "manual_atendimento.txt", "faq_billing.txt"]
corpus = [
    "Política de suporte: SLA de primeiro contacto em 4 horas úteis.",
    "Manual: pedidos de reembolso analisados em até 10 dias.",
    "FAQ: faturas disponíveis no portal na área de billing.",
]
model = SentenceTransformer("all-MiniLM-L6-v2")
emb = model.encode(corpus, normalize_embeddings=True)
index = faiss.IndexFlatIP(emb.shape[1])
index.add(np.array(emb, dtype=np.float32))

query = "como obtenho a minha fatura?"
q = model.encode([query], normalize_embeddings=True)
scores, idx = index.search(np.array(q, dtype=np.float32), k=2)
list(zip(idx[0], scores[0]))
for i, sc in zip(idx[0], scores[0]):
    print(sc, corpus[i])
"""
            ),
        ]

    elif tipo == "govbot":
        cells += [
            md_cell("## 1. Base documental fictícia"),
            code_cell(
                """DOCS = {
    "iptu": "IPTU 2026: 1ª parcela até 10/janeiro; desconto de 5% pagamento único.",
    "iluminacao": "Reportar poste: linha verde 0800-XXX com código do poste.",
    "alvara": "Alvará de funcionamento: protocolo digital com planta e RRMC.",
}
"""
            ),
            md_cell("## 2. Classificação + RAG simplificado"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.2,
)

rotulo_p = ChatPromptTemplate.from_messages([
    ("system", "Classifica em uma etiqueta: imposto | protocolo | servico_urbano | licenca"),
    ("human", "Pergunta: {q}"),
])
rotulo = (rotulo_p | llm | StrOutputParser()).invoke({"q": "Quando vence o IPTU?"})
print("Classe:", rotulo)

ctx = "\\n".join(f"{k}: {v}" for k, v in DOCS.items())
resp_p = ChatPromptTemplate.from_messages([
    ("system", "Responde com base nos documentos; cita a secção lógica. Português europeu."),
    ("human", "Docs:\\n{ctx}\\n\\nPergunta: {q}"),
])
print((resp_p | llm | StrOutputParser()).invoke({"ctx": ctx, "q": "Como peço reembolso de luz?"}))
"""
            ),
        ]

    elif tipo == "agent":
        cells += [
            md_cell("## 1. Ferramentas simuladas"),
            code_cell(
                """from langchain_core.tools import tool

@tool
def abrir_chamado(descricao: str, email: str) -> str:
    return f"CHAMADO-UUID-991 aberto para {email}: {descricao[:80]}"

@tool
def consultar_status(ticket_id: str) -> str:
    return f"Ticket {ticket_id}: estado ABERTO (simulado)"

@tool
def classificar_problema(texto: str) -> str:
    return "Classificação: rede/Wi‑Fi (simulado)"
"""
            ),
            md_cell("## 2. Agente com bind_tools + invoke"),
            code_cell(
                """from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.2,
).bind_tools([abrir_chamado, consultar_status, classificar_problema])

msg = HumanMessage("O meu computador não conecta à rede no escritório.")
ai = llm.invoke([msg])
print(ai)
"""
            ),
        ]

    elif tipo == "crew":
        cells += [
            md_cell("## Equipa sequencial (simula CrewFinance)"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.35,
)

tema = "Pequena empresa com queda de receita de 20%: riscos de tesouraria."

ana = (ChatPromptTemplate.from_template("Analista financeiro: lista riscos objetivos.\\n{tema}") | llm | StrOutputParser()).invoke({"tema": tema})
crit = (ChatPromptTemplate.from_template("Crítico: aponta fragilidades na análise.\\n{ana}") | llm | StrOutputParser()).invoke({"ana": ana})
rel = (ChatPromptTemplate.from_template("Redator: relatório executivo 3 parágrafos com base na análise e crítica.\\nAnálise:\\n{ana}\\nCrítica:\\n{crit}") | llm | StrOutputParser()).invoke({"ana": ana, "crit": crit})
print(rel)
"""
            ),
        ]

    elif tipo == "autogen":
        cells += [
            md_cell("## Rodadas Pesquisador ↔ Crítico → Sintetizador"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.4,
)

def say(role: str, instr: str, **kw):
    p = ChatPromptTemplate.from_messages([
        ("system", role),
        ("human", instr),
    ])
    return (p | llm | StrOutputParser()).invoke(kw)

tema = "Impacto regulatório da IA generativa em PME europeias."
r1 = say("És um pesquisador.", "Proposta inicial sobre {tema}.", tema=tema)
r2 = say("És um crítico exigente.", "Critica:\\n{r1}", r1=r1)
r3 = say("És o pesquisador.", "Ajusta com base na crítica:\\n{r2}", r2=r2)
final = say("És sintetizador.", "Relatório final conciso:\\nPesquisa:{r1}\\nCrítica:{r2}\\nReposta:{r3}", r1=r1, r2=r2, r3=r3)
print(final)
"""
            ),
        ]

    elif tipo == "sk":
        cells += [
            md_cell("## Skills como funções com prompts nomeados"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.25,
)

def skill_resumir(texto: str) -> str:
    p = ChatPromptTemplate.from_template("Resume em 3 bullets:\\n{texto}")
    return (p | llm | StrOutputParser()).invoke({"texto": texto})

def skill_email(pedido: str) -> str:
    p = ChatPromptTemplate.from_template("Gera email formal PT-PT:\\n{pedido}")
    return (p | llm | StrOutputParser()).invoke({"pedido": pedido})

def skill_tarefas(reuniao: str) -> str:
    p = ChatPromptTemplate.from_template("Lista tarefas numeradas pós-reunião:\\n{reuniao}")
    return (p | llm | StrOutputParser()).invoke({"reuniao": reuniao})

print(skill_resumir("Texto longo... " * 8))
print(skill_email("Pedir atualização de cronograma ao fornecedor."))
print(skill_tarefas("Decidimos migrar DB em março e testar carga em abril."))
"""
            ),
        ]

    elif tipo == "dspy":
        cells += [
            md_cell("## Comparação manual de prompts (proxy DSPy)"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os
import time

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.2,
)

perguntas = ["O que é um embedding?", "Diferença entre agente e chain?"]

def run_variant(nome: str, system: str):
    p = ChatPromptTemplate.from_messages([
        ("system", system),
        ("human", "{q}"),
    ])
    chain = p | llm | StrOutputParser()
    lat = []
    for q in perguntas:
        t0 = time.perf_counter()
        out = chain.invoke({"q": q})
        lat.append(time.perf_counter() - t0)
    return nome, lat

v1 = "Responde em uma frase."
v2 = "Responde com definição, exemplo e limitação."
print(run_variant("A", v1))
print(run_variant("B", v2))
"""
            ),
        ]

    elif tipo == "tutorgraph":
        cells += [
            md_cell("## Fluxo tutor: diagnóstico → explicar → exercício → corrigir"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.3,
)

def step(system: str, human: str, **kw):
    p = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    return (p | llm | StrOutputParser()).invoke(kw)

tema = "Probabilidade condicionada"
diag = step("Diagnosticas lacunas.", "Aluno diz: confunde P(A|B) com P(B|A).", tema=tema)
exp = step("Explicas claro.", "Com base:\\n{d}", d=diag)
ex = step("Propões exercício curto.", "Tema: {tema}", tema=tema)
sol_aluno = "0.3"
corr = step("Corriges.", "Enunciado:{ex}\\nResposta aluno:{sol}", ex=ex, sol=sol_aluno)
print(diag, exp, ex, corr, sep="\\n---\\n")
"""
            ),
        ]

    elif tipo == "audit":
        cells += [
            md_cell("## Classificação de risco e ramos"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.1,
)

achado = "Pagamentos duplicados a fornecedor sem dupla verificação em 3 meses."

ris_p = ChatPromptTemplate.from_messages([
    ("system", "Devolve só uma palavra: baixo | medio | alto"),
    ("human", "{achado}"),
])
risco = (ris_p | llm | StrOutputParser()).invoke({"achado": achado}).strip().lower()
print("Risco:", risco)

if "baixo" in risco:
    acao = "Gerar orientação breve ao gestor."
elif "medio" in risco:
    acao = "Solicitar evidências adicionais (extratos, reconciliações)."
else:
    acao = "Encaminhar para revisão humana prioritária."

rel_p = ChatPromptTemplate.from_messages([
    ("system", "Redige relatório curto PT-PT com risco, causa, consequência, recomendação."),
    ("human", "Achado:{a}\\nDecisão:{d}", a=achado, d=acao),
])
print((rel_p | llm | StrOutputParser()).invoke({"a": achado, "d": acao}))
"""
            ),
        ]

    elif tipo == "observe":
        cells += [
            md_cell("## Experimento: latência e custo estimado"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os
import time

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.5,
)

prompts = {
    "curto": "Responde numa palavra.",
    "medio": "Responde com parágrafo.",
    "longo": "Responde com lista numerada de 8 itens.",
}
pergunta = "Liste boas práticas de observabilidade LLM."

logs = []
for nome, sys in prompts.items():
    p = ChatPromptTemplate.from_messages([("system", sys), ("human", pergunta)])
    chain = p | llm | StrOutputParser()
    t0 = time.perf_counter()
    out = chain.invoke({})
    dt = time.perf_counter() - t0
    logs.append({"variante": nome, "latencia_s": round(dt, 3), "chars_out": len(out)})

logs
"""
            ),
        ]

    elif tipo == "local":
        cells += [
            md_cell("## Ollama (opcional) vs mensagem de fallback"),
            code_cell(
                """# Tente: pip install langchain-ollama  (se usar Ollama local)
try:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="llama3.2", temperature=0.2)
    print(llm.invoke("Diz olá em PT."))
except Exception as e:
    print("Ollama indisponível neste ambiente:", e)
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os
    llm = ChatGoogleGenerativeAI(model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""))
    print(llm.invoke("Compara modelo local vs nuvem numa frase."))
"""
            ),
        ]

    elif tipo == "apifact":
        cells += [
            md_cell("## Núcleo das três operações (sem servidor obrigatório)"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.25,
)

def chat(msg: str) -> str:
    p = ChatPromptTemplate.from_messages([
        ("system", "Assistente útil PT-PT."),
        ("human", "{msg}"),
    ])
    return (p | llm | StrOutputParser()).invoke({"msg": msg})

def classificar(txt: str) -> str:
    p = ChatPromptTemplate.from_messages([
        ("system", "Uma etiqueta: suporte | fatura | outro"),
        ("human", "{txt}"),
    ])
    return (p | llm | StrOutputParser()).invoke({"txt": txt})

def resumir(txt: str) -> str:
    p = ChatPromptTemplate.from_messages([
        ("system", "Resume em 2 frases."),
        ("human", "{txt}"),
    ])
    return (p | llm | StrOutputParser()).invoke({"txt": txt})

print(chat("Olá"))
print(classificar("Não recebi fatura"))
print(resumir("Texto " * 40))
"""
            ),
            md_cell("## Testar API real com httpx (opcional)"),
            code_cell(
                """# Com `./run_api.sh --fg` noutro terminal:\\n# import httpx; httpx.post('http://localhost:8000/resumir', json={'texto':'...'})
print("Placeholder — descomente quando a API estiver a correr.")
"""
            ),
        ]

    elif tipo == "ui":
        cells += [
            md_cell("## Mesmo núcleo para duas UIs"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=float(os.environ.get("TEMPERATURA_UI", "0.4")),
)

def agent_core(mensagem: str, tom: str) -> str:
    p = ChatPromptTemplate.from_messages([
        ("system", "Tom: {tom}. Português europeu."),
        ("human", "{m}"),
    ])
    return (p | llm | StrOutputParser()).invoke({"tom": tom, "m": mensagem})

print(agent_core("Explica agentes numa frase.", "técnico"))
"""
            ),
            md_cell("### Como lançar Streamlit / Gradio localmente"),
            md_cell(
                """```bash
# Streamlit
streamlit run app/main.py

# Gradio (adicione um gradio_app.py)
pip install gradio
python gradio_app.py
```"""
            ),
        ]

    elif tipo == "mega":
        cells += [
            md_cell("## Pipeline integrador (protótipo)"),
            code_cell(
                """from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import os

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.25,
)

pedido = "Cliente quer saber prazo contratual e abrir reclamação."

cls = (ChatPromptTemplate.from_template("Classifica intent numa palavra: info | reclamacao | misto\\n{pedido}") | llm | StrOutputParser()).invoke({"pedido": pedido})
ctx = "Contrato: prazo resposta 5 dias úteis para pedidos escritos."
rag = (ChatPromptTemplate.from_template("Contexto:{ctx}\\nResponde objetivamente:\\n{pedido}") | llm | StrOutputParser()).invoke({"ctx": ctx, "pedido": pedido})
rev = (ChatPromptTemplate.from_template("Revisa lacunas:\\n{rag}") | llm | StrOutputParser()).invoke({"rag": rag})
print({"classificacao": cls, "rag": rag, "revisao": rev})
"""
            ),
        ]

    cells.append(md_cell("## Referências\n- `docs/` desta pasta — explicações detalhadas.\n- `app/` — espelho API opcional.\n"))

    return {"cells": cells, "metadata": nb_meta(), "nbformat": 4, "nbformat_minor": 5}


REQ_EXTRA = {
    "rag": "\nlangchain-community>=0.3.0\nchromadb>=0.5.0\n",
    "faiss": "\nsentence-transformers>=3.0.0\nfaiss-cpu>=1.8.0\nnumpy>=1.26.0\n",
    "agent": "",  # langchain-core tools included
    "local": "\nlangchain-ollama>=0.2.0\n",
}

TIPO_REQ = {
    "rag": "rag",
    "faiss": "faiss",
    "local": "local",
}


def patch_requirements(folder: Path, tipo: str) -> None:
    req = folder / "requirements.txt"
    text = req.read_text(encoding="utf-8") if req.is_file() else ""
    key = TIPO_REQ.get(tipo)
    if not key:
        return
    extra = REQ_EXTRA[key]
    if extra.strip() and extra.strip() not in text:
        req.write_text(text.rstrip() + extra + "\n", encoding="utf-8")


def main() -> None:
    for n, folder, nome, tipo in EX:
        d = ROOT / folder
        if not d.is_dir():
            continue
        docs = d / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "arquitetura.md").write_text(doc_arquitetura(n, nome, tipo), encoding="utf-8")
        (docs / "explicacao_teorica.md").write_text(doc_teorica(n, nome, tipo), encoding="utf-8")
        (docs / "passo_a_passo.md").write_text(doc_passo(n, nome, folder), encoding="utf-8")
        (docs / "resultados.md").write_text(doc_resultados(n, nome, tipo), encoding="utf-8")

        nb_path = d / f"exercicio_{n:02d}_sem_ecra.ipynb"
        nb_path.write_text(json.dumps(build_notebook(n, nome, tipo), ensure_ascii=False, indent=2), encoding="utf-8")

        patch_requirements(d, tipo)

    print("Gerado: docs + notebooks + requirements patch onde aplicável.")


if __name__ == "__main__":
    main()
