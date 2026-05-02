# Explicação teórica — RAG Jurídico

## RAG (*Retrieval-Augmented Generation*)

Em vez de confiar só na memória paramétrica do LLM, o sistema **recupera** primeiro troços de documentos da empresa e só depois **gera** a resposta condicionada a esse contexto. Isto reduz invenção de factos (*hallucination*) relativamente ao corpus fornecido — desde que o retriever devolva os troços certos.

## LlamaIndex vs «RAW» vector DB

LlamaIndex abstrai **leitura de ficheiros**, construção do **índice** e **query engines** (retriever + síntese). ChromaDB aqui é o **backend** de armazenamento vectorial; LlamaIndex gere a serialização e as consultas.

## Métricas de relevância

O campo `score` por trecho depende da configuração do vector store / similaridade. Use-o para **ordenar** trechos para o utilizador final (desafio extra), não como prova jurídica.

## Limitações pedagógicas

Documentos são **fictícios**. Não usar como fundamento real para casos concretos sem revisão profissional.
