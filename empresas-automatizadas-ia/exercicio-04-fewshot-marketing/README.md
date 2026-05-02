# Exercício 04 — FewShot Marketing

## Empresa simulada

A **FewShot Marketing** cria campanhas publicitárias aprendendo o **estilo da marca por exemplos** (few-shot), em vez de depender só de instruções vagas.

## Problema de negócio

Empresas querem que a IA escreva textos **parecidos com a sua identidade**, sem soar a **corporate genérico** («robô que acabou de descobrir o LinkedIn»).

## Frameworks obrigatórios

| Framework | Papel |
|-----------|--------|
| **LangChain** | `ChatPromptTemplate` — monta **system + human** com blocos few-shot fixos e variáveis de briefing. |
| **Instructor** | `instructor.from_provider("google/…")` + `create(..., response_model=Campanha)` — força e **re-valida** saída Pydantic. |
| **Pydantic** | Schema `Campanha` + pedido `GerarCampanhaEntrada` + validadores (`hashtags`, tamanhos). |
| **Docker** | `Dockerfile` + `docker-compose.yml` (API **8000**); Jupyter em `docker-compose.jupyter.yml`. |

## O que é *few-shot* neste exercício

**Few-shot prompting** = incluir **exemplos completos** (aqui, três campanhas fictícias com estrutura semelhante à saída desejada) **no contexto** enviado ao modelo. O modelo tende a:

- imitar **ritmo**, **densidade** e **tipo de promessa** dos exemplos;
- manter **coerência** entre título, corpo e CTA;
- reduzir respostas «vazias» quando comparado com um prompt de uma linha.

Não é treino fino dos pesos — é **condicionamento por contexto**. Em produção, os exemplos viriam de campanhas aprovadas pela marca (com permissões e revisão humana).

## Modelo de saída (`Campanha`)

Definido em [`app/schemas/campanha.py`](app/schemas/campanha.py): `titulo`, `publico_alvo`, `tom`, `texto_post`, `chamada_para_acao`, `hashtags`.

## API

Após `./run_api.sh`:

- `GET /health`
- `GET /campanhas/estilos` — textos dos presets (`livre`, `formal`, `engracado`, `tecnico`, `provocativo`)
- `POST /campanhas/gerar` — corpo JSON (exemplo):

```json
{
  "produto": "curso de agentes inteligentes",
  "tom": "didático e sarcástico",
  "publico": "profissionais de tecnologia",
  "estilo": "livre"
}
```

**Desafio extra:** altere `estilo` para `formal`, `engracado`, `tecnico` ou `provocativo` (mantém `tom` como nuance adicional).

## Notebook (sem ecrã)

```bash
./run.sh
```

Abrir [`exercicio_04_sem_ecra.ipynb`](exercicio_04_sem_ecra.ipynb) — contém **Pydantic**, **few-shot**, **Instructor** e **LangChain** **inline** (sem `from app…`); `app/` espelha para a API.

## Variáveis de ambiente

- `GOOGLE_API_KEY` no `.env` na **raiz do repositório do curso**.
- Opcional: `GEMINI_MODEL_EX04` (senão `GEMINI_MODEL`, senão `gemini-2.0-flash`). Ver [`.env.example`](.env.example).

## Documentação

- [`docs/arquitetura.md`](docs/arquitetura.md), [`docs/explicacao_teorica.md`](docs/explicacao_teorica.md), [`docs/passo_a_passo.md`](docs/passo_a_passo.md), [`docs/resultados.md`](docs/resultados.md)

## Código principal

- [`app/services/gerador_campanha.py`](app/services/gerador_campanha.py) — few-shot + chamada Instructor  
- [`app/main.py`](app/main.py) — rotas FastAPI

## 13. Testes automatizados

Os testes do monorepo vivem na raiz [`empresas-automatizadas-ia/tests/`](../tests/) e validam sobretudo **`GET /health`** desta API (quando existe FastAPI em `app/main.py`).

```bash
cd ..    # raiz `empresas-automatizadas-ia/` (pasta que contém `tests/` e `scripts/`)
pip install -r requirements-dev.txt
./scripts/install_test_deps.sh   # ou apenas: pip install -r requirements.txt (nesta pasta)
pytest tests -m "not integration"
```

- **Integração** (Gemini real): `pytest tests -m integration` — requer `GOOGLE_API_KEY`.

Guia completo: [`docs/GUIA_TESTES.md`](../docs/GUIA_TESTES.md).

### Troubleshooting

| Sintoma | O que verificar |
|--------|------------------|
| `ModuleNotFoundError` | Instalar o `requirements.txt` **desta** pasta; para a suíte inteira usar `./scripts/install_test_deps.sh`. |
| Conflitos de versão entre empresas | Usar um **venv por exercício** ou correr testes dentro do **Dockerfile** desse exercício. |
| Ex. 07 — `/buscar` falha | Criar o índice FAISS com `scripts/criar_indice.py` antes de testes que chamem `/buscar`. |
| Ex. 09 / LangGraph | Manter `langgraph>=0.2,<0.3` com `langchain-core` 0.3.x (ver `GUIA_TESTES.md`). |
