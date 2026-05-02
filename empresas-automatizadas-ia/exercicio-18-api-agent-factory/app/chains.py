"""Chains LangChain expostas como API."""

from __future__ import annotations

import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


def _chat():
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash").replace("models/", "")
    return ChatGoogleGenerativeAI(model=model, temperature=0.2)


def chain_chat() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", "És assistente corporativo em PT-PT."),
            ("human", "{mensagem}"),
        ]
    )


def chain_classificar() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", 'Classifica intenção em JSON com chaves: "rotulo" e "justificativa". Rotulos: suporte,vendas,financeiro,outro.'),
            ("human", "{texto}"),
        ]
    )


def chain_resumir() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", "Resume em PT-PT com marcadores, preservando números e datas."),
            ("human", "{texto}"),
        ]
    )


def run_chat(mensagem: str) -> str:
    llm = _chat()
    prompt = chain_chat()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"mensagem": mensagem})


def run_classificar(texto: str) -> str:
    llm = _chat()
    prompt = chain_classificar()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"texto": texto})


def run_resumir(texto: str) -> str:
    llm = _chat()
    prompt = chain_resumir()
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"texto": texto})
