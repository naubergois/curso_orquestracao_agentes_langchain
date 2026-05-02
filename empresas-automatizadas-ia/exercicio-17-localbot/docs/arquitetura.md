# Arquitetura — Exercício 17: LocalBot

## Visão técnica
Ollama expõe API compatível OpenAI em `localhost:11434`. LangChain `ChatOllama` ou endpoint compatível.

Notebook tenta `ChatOllama`; se falhar, documenta fallback Gemini apenas para não bloquear.
