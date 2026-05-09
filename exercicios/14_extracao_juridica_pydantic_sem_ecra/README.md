# Exercício 14 — extração jurídica com LangChain + Pydantic (sem ecrã)

Este exercício demonstra como:

- ler um documento jurídico textual;
- usar `LangChain` para extração estruturada;
- validar/organizar os dados com `Pydantic`;
- produzir uma análise automática de risco contratual.

## Ficheiros

- `documento_juridico_exemplo.txt`: contrato de exemplo.
- `extracao_juridica.py`: pipeline de extração + análise.
- `requirements.txt`: dependências.
- `run.sh`: instala dependências e executa o exercício.

## Pré-requisito

Defina `DEEPSEEK_API_KEY` no `.env` na raiz do repositório.

Opcional:

- `DEEPSEEK_MODEL` (default: `deepseek-chat`)
- `DEEPSEEK_API_BASE` (default: `https://api.deepseek.com`)

## Executar (Jupyter)

```bash
cd exercicios/14_extracao_juridica_pydantic_sem_ecra
./run.sh
```

Abre automaticamente o notebook `exercicio_14_sem_ecra.ipynb`.

## Resultado esperado

No notebook, execute as células para obter:

1. JSON estruturado (`ContratoEstruturado`) com partes, valores, prazo, foro e cláusulas.
2. Uma análise resumida com pontos fortes, alertas e riscos identificados.
