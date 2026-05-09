# CODIGO_COMPLETO — RAG multimodal (relatórios + rostos LFW + achados estruturados)

Export estático — mesmo conteúdo que `CODIGO_COMPLETO.txt`. Gerado por `exercicios/gerar_codigo_completo_txt.py`.

~~~text
# ================================================================================
# CODIGO_COMPLETO.txt — export estático do exercício (leitura offline / impressão)
# Gerado por: exercicios/gerar_codigo_completo_txt.py
# Não editar à mão: voltar a correr o script após alterar .py ou .ipynb.
# ================================================================================

# Pasta: rag_auditoria_rostos_sem_ecra

================================================================================
# FICHEIRO: requirements.txt
================================================================================

# Jupyter + RAG multimodal (texto + rostos) + dados estruturados
python-dotenv>=1.0.0,<2
numpy>=1.26.0,<3
pandas>=2.1.0,<3
tabulate>=0.9.0,<1
pyarrow>=15.0.0,<20
pillow>=10.0.0,<12
scikit-learn>=1.3.0,<2
chromadb>=0.5.0,<1
sentence-transformers>=3.0.0,<4
torch>=2.2.0,<3
langchain-core>=0.3.0
langchain-google-genai>=2.0.0

================================================================================
# FICHEIRO: create_notebook.py
================================================================================

#!/usr/bin/env python3
"""Gera exercicio_rag_auditoria_sem_ecra.ipynb — executar uma vez após clonar."""

from __future__ import annotations

import json
from pathlib import Path


def md(s: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [s]}


def code(s: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [s],
    }


META = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"},
}

INTRO = r"""# RAG + busca semântica — relatórios de auditoria, rostos (LFW) e dados estruturados

**Objetivo:** integrar num pipeline único:
- relatórios Markdown fictícios (PT-PT);
- tabela estruturada (`findings.parquet`);
- imagens de rostos do conjunto público **Labeled Faces in the Wild (LFW)** descarregado via `sklearn`;
- **RAG** textual (Chroma + MiniLM multilingue);
- **busca semântica de imagens** (CLIP: texto ↔ imagem);
- **relatório final** com Gemini.

> **Nota ética:** o LFW contém rostos de figuras públicas; os relatórios aqui são **simulados**. Uso apenas pedagógico.

Execute as células **em ordem**. A primeira descarga do LFW pode demorar (rede).
"""

C1 = r"""from pathlib import Path
import json
import os
import re
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
from dotenv import load_dotenv

ROOT = Path.cwd().resolve()
REPO = ROOT.parent.parent
load_dotenv(REPO / ".env", override=False)
DATA = ROOT / "data" / "generated"
ROSTOS = DATA / "rostos"
RELS = DATA / "relatorios"
CHROMA = DATA / "chroma_audit"

for p in (ROSTOS, RELS, CHROMA):
    p.mkdir(parents=True, exist_ok=True)

assert os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"), (
    "Defina GOOGLE_API_KEY na raiz do repositório para a síntese final."
)
print("ROOT:", ROOT)
print("DATA:", DATA)
"""

C2 = r"""# 1) Banco de rostos: LFW (limite por pessoa para o exercício ser leve)
from sklearn.datasets import fetch_lfw_people

print("A descarregar LFW (pode demorar na primeira vez)...")
lfw = fetch_lfw_people(
    min_faces_per_person=55,
    resize=0.55,
    color=True,
    download_if_missing=True,
)

imgs = lfw.images  # (N, h, w, 3) float em [0,1] tipicamente
targets = lfw.target
names_internal = lfw.target_names
print("Amostras:", imgs.shape[0], "| labels únicos:", len(names_internal))
"""

C3 = r"""# 2) Exportar PNG + manifest (person_code anónimo no cenário de auditoria)
from PIL import Image

MAX_PER_LABEL = 14
manifest: list[dict] = []

for label_idx in np.unique(targets):
    idxs = np.where(targets == label_idx)[0][:MAX_PER_LABEL]
    code = f"PERS_{int(label_idx):03d}"
    for k, i in enumerate(idxs):
        arr = imgs[i]
        if arr.max() <= 1.0:
            arr = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
        else:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        fn = ROSTOS / f"{code}_{k:02d}.png"
        Image.fromarray(arr, mode="RGB").save(fn)
        manifest.append(
            {
                "person_code": code,
                "label_idx": int(label_idx),
                "image_path": str(fn.relative_to(ROOT)),
                "image_filename": fn.name,
                "lfw_reference_name": str(names_internal[label_idx]),
            }
        )

with open(DATA / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

len(manifest), manifest[:2]
"""

C4 = r"""# 3) Dados estruturados (achados) + escrita de relatórios fictícios

rng = np.random.default_rng(42)
codes = sorted({m["person_code"] for m in manifest})
n_findings = 48
rows = []
areas = ["Financeiro", "RH", "Compliance", "TI", "Fornecedores"]
risk_levels = ["baixo", "medio", "alto"]

for fid in range(1, n_findings + 1):
    pc = codes[int(rng.integers(0, len(codes)))]
    rows.append(
        {
            "finding_id": f"ACH-{2025}-{fid:04d}",
            "person_code": pc,
            "valor_euro": float(rng.integers(500, 85000)),
            "risco": risk_levels[int(rng.integers(0, 3))],
            "area": areas[int(rng.integers(0, len(areas)))],
            "data_iso": f"2025-{rng.integers(1, 12):02d}-{rng.integers(1, 28):02d}",
            "descricao_curta": (
                "Discrepância documental; necessita confirmação de controlo interno."
                if fid % 3
                else "Possível conflito de interesses identificado em auditoria amostral."
            ),
        }
    )

df_findings = pd.DataFrame(rows)
df_findings.to_parquet(DATA / "findings.parquet", index=False)
df_findings.to_csv(DATA / "findings.csv", index=False)
df_findings.head()
"""

C5 = r"""# 4) Gerar relatórios Markdown (texto longo) referenciando person_code e achados

def md_report(name: str, title: str, body: str) -> None:
    p = RELS / name
    p.write_text("# " + title + "\n\n" + body + "\n", encoding="utf-8")

high = df_findings[df_findings["risco"] == "alto"].head(8)
lines = []
for _, r in high.iterrows():
    lines.append(
        "- "
        + str(r["finding_id"])
        + " ("
        + str(r["area"])
        + "): envolve **"
        + str(r["person_code"])
        + "**, montante indicativo "
        + f"{float(r['valor_euro']):.0f}"
        + " EUR."
    )
bullet_alto = "\n".join(lines)

rh_lines = "\n".join(
    "- Alerta ligado a **" + c + "** em cruzamento com horas extra." for c in codes[:6]
)

md_report(
    "relatorio_consolidado_q1.md",
    "Auditoria interna — consolidado Q1 2025",
    "## Âmbito\n"
    "Revisão amostral de processos financeiros e RH com cruzamento a bases de fornecedores.\n\n"
    "## Achados de maior exposição\n"
    + bullet_alto
    + "\n\n## Observações sobre identidades visuais\n"
    "Durante entrevistas existiu necessidade de confrontar **registos fotográficos internos** com presenças em reuniões sensíveis.\n"
    "Os códigos **PERS_XXX** mapeiam participantes sob investigação administrativa (fictício).\n\n"
    "## Conclusão preliminar\n"
    "Recomenda-se reforço de segregação de funções e revisão de acessos privilegiados em sistemas de payroll.\n",
)

md_report(
    "relatorio_rh_payroll.md",
    "Auditoria RH — payroll e horas extraordinárias",
    "## Contexto\n"
    "Leitura de batidas incompletas e aprovações duplicadas em centros de custo regionais.\n\n"
    "## Ligações a colaboradores codificados\n"
    + rh_lines
    + "\n\n## Evidências mistas\n"
    "Combinação de **dados estruturados** (exports SAP simulados) e **notas de campo** anexadas ao processo.\n\n"
    "## Pedido de diligências\n"
    "Validação cruzada com imagens de presença em atos internos e reconciliação com `findings.parquet`.\n",
)

md_report(
    "relatorio_ti_acessos.md",
    "Auditoria TI — trilhos de auditoria e contas privilegiadas",
    "## Achados\n"
    "Contas de serviço com MFA inconsistente; partilha de credenciais em equipas terceirizadas.\n\n"
    "## Correlação multimodal\n"
    "Equipa técnica correlacionou **logs** com **material visual** de reuniões de passagem de bastão de administração de sistemas.\n\n"
    "## Recomendações\n"
    "Rotação de segredos; revisão de RBAC; monitorização contínua com alertas por desvio estatístico.\n",
)

list(RELS.glob("*.md"))
"""

C6 = r"""# 5) Chunking dos relatórios (sobreposição leve)

def chunk_text(text: str, size: int = 520, overlap: int = 80) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += size - overlap
    return [c for c in chunks if len(c) > 40]

all_chunks: list[tuple[str, str, int]] = []
for fp in sorted(RELS.glob("*.md")):
    raw = fp.read_text(encoding="utf-8")
    for j, ch in enumerate(chunk_text(raw)):
        all_chunks.append((fp.name, ch, j))

len(all_chunks), all_chunks[0][1][:120]
"""

C7 = r"""# 6) Modelos de embedding: texto multilingue + CLIP (imagem + texto na mesma espaço imagem)
from sentence_transformers import SentenceTransformer

print("A carregar MiniLM multilingue...")
text_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

print("A carregar CLIP...")
clip_model = SentenceTransformer("clip-ViT-B-32")

text_model.encode(["teste embed"]).shape, "ok"
"""

C8 = r"""# 7) Índices Chroma (persistente em data/generated/chroma_audit)
from PIL import Image
import chromadb
from chromadb.config import Settings

# Evita telemetria PostHog (incompatibilidades de versão geram ruído nos logs).
client = chromadb.PersistentClient(
    path=str(CHROMA),
    settings=Settings(anonymized_telemetry=False),
)

try:
    client.delete_collection("relatorios_pt")
except Exception:
    pass
try:
    client.delete_collection("rostos_clip")
except Exception:
    pass

col_txt = client.create_collection(
    name="relatorios_pt",
    metadata={"hnsw:space": "cosine"},
)
col_img = client.create_collection(
    name="rostos_clip",
    metadata={"hnsw:space": "cosine"},
)

ids_txt = [f"txt_{i}" for i in range(len(all_chunks))]
docs_txt = [c[1] for c in all_chunks]
meta_txt = [{"fonte": c[0], "chunk_idx": c[2]} for c in all_chunks]
emb_txt = text_model.encode(docs_txt, show_progress_bar=True, batch_size=32).tolist()
col_txt.add(ids=ids_txt, documents=docs_txt, metadatas=meta_txt, embeddings=emb_txt)

img_paths = [ROOT / m["image_path"] for m in manifest]
ids_img = [m["person_code"] + "_" + m["image_filename"].replace(".png", "") for m in manifest]
pil_images = [Image.open(p) for p in img_paths]
emb_img = clip_model.encode(pil_images, batch_size=16, show_progress_bar=True).tolist()
meta_img = [
    {
        "person_code": m["person_code"],
        "path": m["image_path"],
        "lfw_reference_name": m["lfw_reference_name"],
    }
    for m in manifest
]
col_img.add(ids=ids_img, embeddings=emb_img, metadatas=meta_img, documents=[f"face:{m['person_code']}" for m in manifest])

print("Coleções indexadas:", col_txt.count(), col_img.count())
"""

C9 = r"""# 8) Função de consulta unificada: semântica texto + CLIP + merge com dados estruturados

def auditar_consulta(pergunta: str, k_txt: int = 6, k_img: int = 6) -> dict:
    q_txt = text_model.encode([pergunta]).tolist()[0]
    q_clip = clip_model.encode([pergunta]).tolist()[0]

    # Chroma exige n_results <= número de vectores na coleção (evita aviso e edge cases).
    n_txt = min(max(1, k_txt), max(1, col_txt.count()))
    n_img = min(max(1, k_img), max(1, col_img.count()))
    rt = col_txt.query(query_embeddings=[q_txt], n_results=n_txt)
    ri = col_img.query(query_embeddings=[q_clip], n_results=n_img)

    # Chroma devolve cada entrada de metadados como dict plano (person_code no topo).
    def _person_code(meta):
        if not meta:
            return None
        if "person_code" in meta:
            return meta["person_code"]
        nested = meta.get("metadata")
        if isinstance(nested, dict) and "person_code" in nested:
            return nested["person_code"]
        return None

    faces_meta = ri["metadatas"][0] or []
    pessoas = {_person_code(m) for m in faces_meta}
    pessoas.discard(None)
    df_hit = df_findings[df_findings["person_code"].isin(pessoas)]

    return {
        "pergunta": pergunta,
        "trechos_relatorio": list(zip(rt["documents"][0], rt["metadatas"][0])),
        "rostos_metadados": ri["metadatas"][0],
        "achados_estruturados_filtrados": df_hit,
    }

res = auditar_consulta(
    "Que achados de alto risco mencionam payroll ou RH e que colaboradores aparecem em imagens relacionadas?"
)
len(res["trechos_relatorio"]), res["achados_estruturados_filtrados"].shape
"""

C10 = r"""# 9) Baseline keyword vs semântica (demonstração rápida)

def keyword_hits(query: str) -> int:
    q = query.lower()
    return sum(1 for _, doc, _ in all_chunks if any(w in doc.lower() for w in q.split() if len(w) > 3))

print("Keyword-ish hits:", keyword_hits("payroll RH"))
print("Semantic query usa embeddings na função auditar_consulta.")
"""

C11 = r"""# 10) Relatório final com Gemini (síntese + lista de evidências)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

res = auditar_consulta(
    "Síntese executiva: riscos cruzando relatórios financeiros e RH; indica códigos PERS e valores relevantes dos achados estruturados.",
    k_txt=8,
    k_img=8,
)

trechos = "\\n\\n".join(f"[{m['fonte']}] {d[:900]}" for d, m in res["trechos_relatorio"])
rostos = "\\n".join(
    f"- {m['person_code']} | {m['path']} | ref.LFW={m['lfw_reference_name']}"
    for m in res["rostos_metadados"]
)
tab = res["achados_estruturados_filtrados"].to_markdown(index=False) if len(res["achados_estruturados_filtrados"]) else "(sem cruzamento estruturado direto — ver manifest)"

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.2,
)
sys = SystemMessage(
    content=(
        "És auditor senior. Português europeu. Fundamenta só no contexto fornecido; "
        "se faltar dados, declara incerteza. Não inventes montantes."
    )
)
hum = HumanMessage(
    content=f"Pergunta/utilizador:\\n{res['pergunta']}\\n\\nTrechos recuperados:\\n{trechos}\\n\\nRostos recuperados (CLIP):\\n{rostos}\\n\\nAchados estruturados (subset):\\n{tab}"
)
out = llm.invoke([sys, hum])
print(out.content)
"""

cells = [
    md(INTRO),
    code(C1),
    code(C2),
    code(C3),
    code(C4),
    code(C5),
    code(C6),
    code(C7),
    code(C8),
    code(C9),
    code(C10),
    code(C11),
]

nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": META, "cells": cells}

Path(__file__).resolve().parent.joinpath("exercicio_rag_auditoria_sem_ecra.ipynb").write_text(
    json.dumps(nb, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("Notebook escrito.")


================================================================================
# FICHEIRO: exercicio_rag_auditoria_sem_ecra.ipynb
================================================================================

# --- Célula 0 (markdown) ---
# # RAG + busca semântica — relatórios de auditoria, rostos (LFW) e dados estruturados
# 
# **Objetivo:** integrar num pipeline único:
# - relatórios Markdown fictícios (PT-PT);
# - tabela estruturada (`findings.parquet`);
# - imagens de rostos do conjunto público **Labeled Faces in the Wild (LFW)** descarregado via `sklearn`;
# - **RAG** textual (Chroma + MiniLM multilingue);
# - **busca semântica de imagens** (CLIP: texto ↔ imagem);
# - **relatório final** com Gemini.
# 
# > **Nota ética:** o LFW contém rostos de figuras públicas; os relatórios aqui são **simulados**. Uso apenas pedagógico.
# 
# Execute as células **em ordem**. A primeira descarga do LFW pode demorar (rede).

# --- Célula 1 (código) ---
from pathlib import Path
import json
import os
import re
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
from dotenv import load_dotenv

ROOT = Path.cwd().resolve()
REPO = ROOT.parent.parent
load_dotenv(REPO / ".env", override=False)
DATA = ROOT / "data" / "generated"
ROSTOS = DATA / "rostos"
RELS = DATA / "relatorios"
CHROMA = DATA / "chroma_audit"

for p in (ROSTOS, RELS, CHROMA):
    p.mkdir(parents=True, exist_ok=True)

assert os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY"), (
    "Defina GOOGLE_API_KEY na raiz do repositório para a síntese final."
)
print("ROOT:", ROOT)
print("DATA:", DATA)

# --- Célula 2 (código) ---
# 1) Banco de rostos: LFW (limite por pessoa para o exercício ser leve)
from sklearn.datasets import fetch_lfw_people

print("A descarregar LFW (pode demorar na primeira vez)...")
lfw = fetch_lfw_people(
    min_faces_per_person=55,
    resize=0.55,
    color=True,
    download_if_missing=True,
)

imgs = lfw.images  # (N, h, w, 3) float em [0,1] tipicamente
targets = lfw.target
names_internal = lfw.target_names
print("Amostras:", imgs.shape[0], "| labels únicos:", len(names_internal))

# --- Célula 3 (código) ---
# 2) Exportar PNG + manifest (person_code anónimo no cenário de auditoria)
from PIL import Image

MAX_PER_LABEL = 14
manifest: list[dict] = []

for label_idx in np.unique(targets):
    idxs = np.where(targets == label_idx)[0][:MAX_PER_LABEL]
    code = f"PERS_{int(label_idx):03d}"
    for k, i in enumerate(idxs):
        arr = imgs[i]
        if arr.max() <= 1.0:
            arr = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
        else:
            arr = np.clip(arr, 0, 255).astype(np.uint8)
        fn = ROSTOS / f"{code}_{k:02d}.png"
        Image.fromarray(arr, mode="RGB").save(fn)
        manifest.append(
            {
                "person_code": code,
                "label_idx": int(label_idx),
                "image_path": str(fn.relative_to(ROOT)),
                "image_filename": fn.name,
                "lfw_reference_name": str(names_internal[label_idx]),
            }
        )

with open(DATA / "manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)

len(manifest), manifest[:2]

# --- Célula 4 (código) ---
# 3) Dados estruturados (achados) + escrita de relatórios fictícios

rng = np.random.default_rng(42)
codes = sorted({m["person_code"] for m in manifest})
n_findings = 48
rows = []
areas = ["Financeiro", "RH", "Compliance", "TI", "Fornecedores"]
risk_levels = ["baixo", "medio", "alto"]

for fid in range(1, n_findings + 1):
    pc = codes[int(rng.integers(0, len(codes)))]
    rows.append(
        {
            "finding_id": f"ACH-{2025}-{fid:04d}",
            "person_code": pc,
            "valor_euro": float(rng.integers(500, 85000)),
            "risco": risk_levels[int(rng.integers(0, 3))],
            "area": areas[int(rng.integers(0, len(areas)))],
            "data_iso": f"2025-{rng.integers(1, 12):02d}-{rng.integers(1, 28):02d}",
            "descricao_curta": (
                "Discrepância documental; necessita confirmação de controlo interno."
                if fid % 3
                else "Possível conflito de interesses identificado em auditoria amostral."
            ),
        }
    )

df_findings = pd.DataFrame(rows)
df_findings.to_parquet(DATA / "findings.parquet", index=False)
df_findings.to_csv(DATA / "findings.csv", index=False)
df_findings.head()

# --- Célula 5 (código) ---
# 4) Gerar relatórios Markdown (texto longo) referenciando person_code e achados

def md_report(name: str, title: str, body: str) -> None:
    p = RELS / name
    p.write_text("# " + title + "\n\n" + body + "\n", encoding="utf-8")

high = df_findings[df_findings["risco"] == "alto"].head(8)
lines = []
for _, r in high.iterrows():
    lines.append(
        "- "
        + str(r["finding_id"])
        + " ("
        + str(r["area"])
        + "): envolve **"
        + str(r["person_code"])
        + "**, montante indicativo "
        + f"{float(r['valor_euro']):.0f}"
        + " EUR."
    )
bullet_alto = "\n".join(lines)

rh_lines = "\n".join(
    "- Alerta ligado a **" + c + "** em cruzamento com horas extra." for c in codes[:6]
)

md_report(
    "relatorio_consolidado_q1.md",
    "Auditoria interna — consolidado Q1 2025",
    "## Âmbito\n"
    "Revisão amostral de processos financeiros e RH com cruzamento a bases de fornecedores.\n\n"
    "## Achados de maior exposição\n"
    + bullet_alto
    + "\n\n## Observações sobre identidades visuais\n"
    "Durante entrevistas existiu necessidade de confrontar **registos fotográficos internos** com presenças em reuniões sensíveis.\n"
    "Os códigos **PERS_XXX** mapeiam participantes sob investigação administrativa (fictício).\n\n"
    "## Conclusão preliminar\n"
    "Recomenda-se reforço de segregação de funções e revisão de acessos privilegiados em sistemas de payroll.\n",
)

md_report(
    "relatorio_rh_payroll.md",
    "Auditoria RH — payroll e horas extraordinárias",
    "## Contexto\n"
    "Leitura de batidas incompletas e aprovações duplicadas em centros de custo regionais.\n\n"
    "## Ligações a colaboradores codificados\n"
    + rh_lines
    + "\n\n## Evidências mistas\n"
    "Combinação de **dados estruturados** (exports SAP simulados) e **notas de campo** anexadas ao processo.\n\n"
    "## Pedido de diligências\n"
    "Validação cruzada com imagens de presença em atos internos e reconciliação com `findings.parquet`.\n",
)

md_report(
    "relatorio_ti_acessos.md",
    "Auditoria TI — trilhos de auditoria e contas privilegiadas",
    "## Achados\n"
    "Contas de serviço com MFA inconsistente; partilha de credenciais em equipas terceirizadas.\n\n"
    "## Correlação multimodal\n"
    "Equipa técnica correlacionou **logs** com **material visual** de reuniões de passagem de bastão de administração de sistemas.\n\n"
    "## Recomendações\n"
    "Rotação de segredos; revisão de RBAC; monitorização contínua com alertas por desvio estatístico.\n",
)

list(RELS.glob("*.md"))

# --- Célula 6 (código) ---
# 5) Chunking dos relatórios (sobreposição leve)

def chunk_text(text: str, size: int = 520, overlap: int = 80) -> list[str]:
    text = re.sub(r"\s+", " ", text.strip())
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += size - overlap
    return [c for c in chunks if len(c) > 40]

all_chunks: list[tuple[str, str, int]] = []
for fp in sorted(RELS.glob("*.md")):
    raw = fp.read_text(encoding="utf-8")
    for j, ch in enumerate(chunk_text(raw)):
        all_chunks.append((fp.name, ch, j))

len(all_chunks), all_chunks[0][1][:120]

# --- Célula 7 (código) ---
# 6) Modelos de embedding: texto multilingue + CLIP (imagem + texto na mesma espaço imagem)
from sentence_transformers import SentenceTransformer

print("A carregar MiniLM multilingue...")
text_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

print("A carregar CLIP...")
clip_model = SentenceTransformer("clip-ViT-B-32")

text_model.encode(["teste embed"]).shape, "ok"

# --- Célula 8 (código) ---
# 7) Índices Chroma (persistente em data/generated/chroma_audit)
from PIL import Image
import chromadb
from chromadb.config import Settings

# Evita telemetria PostHog (incompatibilidades de versão geram ruído nos logs).
client = chromadb.PersistentClient(
    path=str(CHROMA),
    settings=Settings(anonymized_telemetry=False),
)

try:
    client.delete_collection("relatorios_pt")
except Exception:
    pass
try:
    client.delete_collection("rostos_clip")
except Exception:
    pass

col_txt = client.create_collection(
    name="relatorios_pt",
    metadata={"hnsw:space": "cosine"},
)
col_img = client.create_collection(
    name="rostos_clip",
    metadata={"hnsw:space": "cosine"},
)

ids_txt = [f"txt_{i}" for i in range(len(all_chunks))]
docs_txt = [c[1] for c in all_chunks]
meta_txt = [{"fonte": c[0], "chunk_idx": c[2]} for c in all_chunks]
emb_txt = text_model.encode(docs_txt, show_progress_bar=True, batch_size=32).tolist()
col_txt.add(ids=ids_txt, documents=docs_txt, metadatas=meta_txt, embeddings=emb_txt)

img_paths = [ROOT / m["image_path"] for m in manifest]
ids_img = [m["person_code"] + "_" + m["image_filename"].replace(".png", "") for m in manifest]
pil_images = [Image.open(p) for p in img_paths]
emb_img = clip_model.encode(pil_images, batch_size=16, show_progress_bar=True).tolist()
meta_img = [
    {
        "person_code": m["person_code"],
        "path": m["image_path"],
        "lfw_reference_name": m["lfw_reference_name"],
    }
    for m in manifest
]
col_img.add(ids=ids_img, embeddings=emb_img, metadatas=meta_img, documents=[f"face:{m['person_code']}" for m in manifest])

print("Coleções indexadas:", col_txt.count(), col_img.count())

# --- Célula 9 (código) ---
# 8) Função de consulta unificada: semântica texto + CLIP + merge com dados estruturados

def auditar_consulta(pergunta: str, k_txt: int = 6, k_img: int = 6) -> dict:
    q_txt = text_model.encode([pergunta]).tolist()[0]
    q_clip = clip_model.encode([pergunta]).tolist()[0]

    # Chroma exige n_results <= número de vectores na coleção (evita aviso e edge cases).
    n_txt = min(max(1, k_txt), max(1, col_txt.count()))
    n_img = min(max(1, k_img), max(1, col_img.count()))
    rt = col_txt.query(query_embeddings=[q_txt], n_results=n_txt)
    ri = col_img.query(query_embeddings=[q_clip], n_results=n_img)

    # Chroma devolve cada entrada de metadados como dict plano (person_code no topo).
    def _person_code(meta):
        if not meta:
            return None
        if "person_code" in meta:
            return meta["person_code"]
        nested = meta.get("metadata")
        if isinstance(nested, dict) and "person_code" in nested:
            return nested["person_code"]
        return None

    faces_meta = ri["metadatas"][0] or []
    pessoas = {_person_code(m) for m in faces_meta}
    pessoas.discard(None)
    df_hit = df_findings[df_findings["person_code"].isin(pessoas)]

    return {
        "pergunta": pergunta,
        "trechos_relatorio": list(zip(rt["documents"][0], rt["metadatas"][0])),
        "rostos_metadados": ri["metadatas"][0],
        "achados_estruturados_filtrados": df_hit,
    }

res = auditar_consulta(
    "Que achados de alto risco mencionam payroll ou RH e que colaboradores aparecem em imagens relacionadas?"
)
len(res["trechos_relatorio"]), res["achados_estruturados_filtrados"].shape

# --- Célula 10 (código) ---
# 9) Baseline keyword vs semântica (demonstração rápida)

def keyword_hits(query: str) -> int:
    q = query.lower()
    return sum(1 for _, doc, _ in all_chunks if any(w in doc.lower() for w in q.split() if len(w) > 3))

print("Keyword-ish hits:", keyword_hits("payroll RH"))
print("Semantic query usa embeddings na função auditar_consulta.")

# --- Célula 11 (código) ---
# 10) Relatório final com Gemini (síntese + lista de evidências)

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

res = auditar_consulta(
    "Síntese executiva: riscos cruzando relatórios financeiros e RH; indica códigos PERS e valores relevantes dos achados estruturados.",
    k_txt=8,
    k_img=8,
)

trechos = "\\n\\n".join(f"[{m['fonte']}] {d[:900]}" for d, m in res["trechos_relatorio"])
rostos = "\\n".join(
    f"- {m['person_code']} | {m['path']} | ref.LFW={m['lfw_reference_name']}"
    for m in res["rostos_metadados"]
)
tab = res["achados_estruturados_filtrados"].to_markdown(index=False) if len(res["achados_estruturados_filtrados"]) else "(sem cruzamento estruturado direto — ver manifest)"

llm = ChatGoogleGenerativeAI(
    model=(os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash").replace("models/", ""),
    temperature=0.2,
)
sys = SystemMessage(
    content=(
        "És auditor senior. Português europeu. Fundamenta só no contexto fornecido; "
        "se faltar dados, declara incerteza. Não inventes montantes."
    )
)
hum = HumanMessage(
    content=f"Pergunta/utilizador:\\n{res['pergunta']}\\n\\nTrechos recuperados:\\n{trechos}\\n\\nRostos recuperados (CLIP):\\n{rostos}\\n\\nAchados estruturados (subset):\\n{tab}"
)
out = llm.invoke([sys, hum])
print(out.content)

# --- Célula 12 (código) ---
# --- Célula 13 (código) ---
# --- Célula 14 (código) ---

~~~
