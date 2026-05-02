# Arquitetura — RAG auditoria + rostos + dados estruturados

## Objetivo pedagógico

Combinar num único fluxo:

1. **Relatórios de auditoria** (texto livre, PT-PT) com achados e referências a identidades anonimizadas.
2. **Dados estruturados** (`findings.parquet` / CSV) filtráveis (risco, valor, área, `person_code`).
3. **Imagens de rostos** do conjunto público **LFW** (Laboratory Faces in the Wild), ligadas por `person_code` a registos fictícios de auditoria.
4. **RAG textual** — chunks dos relatórios indexados com modelo multilingue.
5. **Busca semântica de imagens** — embeddings CLIP no espaço imagem↔texto para recuperar rostos relevantes a partir de perguntas em linguagem natural.

## Fluxo de dados

```text
LFW (download) ─► PNG + manifest.json (rostos + meta)
                         │
                         ├──► Chroma coleção `rostos_clip` (vetores CLIP imagem)
                         │
Relatórios .md gerados ─► chunks ─► Chroma `relatorios_pt` (MiniLM multilingue)

findings.parquet ◄──► merge por person_code ◄──► manifest

Query utilizador ─► dupla recuperação (texto + imagem CLIP texto)
                         │
                         └──► síntese Gemini + junção com filtros pandas (estruturado)
```

## Por que duas coleções vetoriais?

- Textos longos em português beneficiam de **MiniLM multilingue**.
- CLIP alinha **pergunta textual** com **aparência facial** no mesmo espaço latente (demonstração didática; não é reconhecimento biométrico certificado).

## Artefactos em `data/generated/`

| Caminho | Conteúdo |
|---------|-----------|
| `rostos/*.png` | Recortes exportados do LFW |
| `manifest.json` | `person_code`, caminho imagem, índice interno LFW |
| `relatorios/*.md` | Relatórios de auditoria fictícios |
| `findings.parquet` | Tabela estruturada de achados |
| `chroma_audit/` | Persistência Chroma (opcional; regenerável) |
