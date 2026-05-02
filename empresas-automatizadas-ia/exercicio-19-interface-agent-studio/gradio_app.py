"""Interface Gradio — Exercício 19."""

from __future__ import annotations

import os
from pathlib import Path

import gradio as gr
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT.parent.parent / ".env", override=False)
load_dotenv(_ROOT / ".env", override=True)

from app.agent_shared import responder  # noqa: E402


def ui_fn(mensagem: str, modelo: str, tom: str, temperatura: float) -> str:
    if not os.environ.get("GOOGLE_API_KEY"):
        return "Erro: GOOGLE_API_KEY não definido."
    if not mensagem.strip():
        return "Escreva uma mensagem."
    return responder(mensagem.strip(), modelo, float(temperatura), tom)


demo = gr.Interface(
    fn=ui_fn,
    inputs=[
        gr.Textbox(lines=6, label="Mensagem"),
        gr.Dropdown(["gemini-2.0-flash", "gemini-1.5-flash"], value="gemini-2.0-flash", label="Modelo"),
        gr.Dropdown(["profissional", "didático", "informal"], value="profissional", label="Tom"),
        gr.Slider(0, 1, value=0.3, step=0.05, label="Temperatura"),
    ],
    outputs=gr.Textbox(label="Resposta"),
    title="Interface Agent Studio (Gradio)",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("GRADIO_PORT", "7860")))
