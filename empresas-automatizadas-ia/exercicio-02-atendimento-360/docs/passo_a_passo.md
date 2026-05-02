# Passo a passo — Exercício 02: Atendimento 360

## 1. Ambiente

1. Na **raiz do repositório do curso**, configure `.env` com `GOOGLE_API_KEY` (Gemini).
2. Na pasta `exercicio-02-atendimento-360`, execute `./run.sh` para Jupyter Lab.

## 2. Notebook (sem ecrã)

Abra e execute na ordem **`exercicio_02_sem_ecra.ipynb`** (kernel Python 3).

Secções:

1. Ambiente e `OUT_GEN` (`app/data/generated`).
2. Loop com memória (exemplo *João*) + export JSON.
3. Lote de conversas simuladas → `conversas_simuladas.json`.
4. Modelos Pydantic.
5. Extração estruturada por conversa → `relatorios/extracao_*.json`.
6. Relatório agregado → `RELATORIO_LOTE.md` e `RELATORIO_LOTE.json`.
7. DataFrame + gráficos consolidados e projeções → `extracoes_consolidado.csv`, `.parquet`, PNG e `projecao_volume_urgencia.csv`.

## 3. Streamlit (com ecrã)

```bash
./run_streamlit.sh
```

Abra `http://localhost:8501`. Teste limpar conversa e exportar `.txt` / `.json`.

## 4. Artefactos gerados

Ficheiros sob `app/data/generated/` (ignorados pelo Git exceto `.gitkeep`) e, na raiz do exercício, `historico_export.json` após correr a demo *João*. Não commite dados reais de clientes.

## 5. Parar containers

```bash
docker compose -f docker-compose.jupyter.yml down
# ou, se usou Streamlit:
docker compose down
```
