"""Carrega a CNN treinada e produz probabilidades sobre imagens DermaMNIST (28×28)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from cnn_derma import construir_resnet18_transfer, preprocess_flat_para_resnet

MODELOS_DIR = Path(__file__).resolve().parent / "models"
_MODELO: torch.nn.Module | None = None
_META: dict | None = None
_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _meta() -> dict:
    global _META
    if _META is None:
        p = MODELOS_DIR / "meta.json"
        _META = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    return _META


def carregar_classificador(force_reload: bool = False) -> torch.nn.Module:
    global _MODELO
    if _MODELO is not None and not force_reload:
        return _MODELO

    path_name = _meta().get("weights_file", "cnn_derma.pt")
    path = MODELOS_DIR / str(path_name)
    if not path.is_file():
        raise FileNotFoundError(
            f"Modelo em falta: {path}. Corra `python treinar_classificador.py` nesta pasta."
        )
    m = construir_resnet18_transfer(7)
    state = torch.load(path, map_location=_DEVICE)
    m.load_state_dict(state)
    m.eval().to(_DEVICE)
    _MODELO = m
    return _MODELO


def prever_de_vector(imagem_flat_normalizada: np.ndarray) -> dict[str, Any]:
    """`imagem_flat_normalizada`: (784,) floats em [0,1]."""
    modelo = carregar_classificador()
    with torch.no_grad():
        tin = preprocess_flat_para_resnet(imagem_flat_normalizada, _DEVICE)
        logits = modelo(tin)
        proba = torch.softmax(logits, dim=1)[0].cpu().numpy()

    pred = int(np.argmax(proba))
    classes = _meta().get("classes") or []
    return {
        "probabilidades": proba.tolist(),
        "classe_predita": pred,
        "rotulo_predito": classes[pred] if pred < len(classes) else str(pred),
        "confianca_maxima": float(np.max(proba)),
    }


def prever_de_pil_28x28(pil_image) -> dict[str, Any]:
    from PIL import Image

    img = pil_image.convert("L").resize((28, 28))
    arr = np.asarray(img, dtype=np.float32).reshape(-1) / 255.0
    return prever_de_vector(arr)


def vetor_de_amostra_medmnist(split: str, indice: int) -> tuple[np.ndarray, int]:
    """Devolve (x_flat_norm, y_verdadeiro) para uma entrada do DermaMNIST."""
    from medmnist import DermaMNIST

    ds = DermaMNIST(split=split, download=True)
    if indice < 0 or indice >= len(ds):
        raise IndexError(f"Índice {indice} fora do intervalo [0, {len(ds) - 1}]")
    img, label = ds[indice]
    if hasattr(img, "convert"):
        arr = np.asarray(img.convert("L"), dtype=np.float32)
    else:
        arr = np.asarray(img, dtype=np.float32)
    if arr.ndim == 3:
        arr = np.squeeze(arr)
    y = int(np.asarray(label).reshape(-1)[0])
    x = arr.reshape(-1) / 255.0
    return x, y
