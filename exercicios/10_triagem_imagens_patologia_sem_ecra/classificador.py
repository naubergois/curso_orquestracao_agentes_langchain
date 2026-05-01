"""Carrega o classificador treinado e produz probabilidades sobre imagens DermaMNIST (28×28)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

MODELOS_DIR = Path(__file__).resolve().parent / "models"
_MODELO: Any | None = None
_META: dict | None = None


def _meta() -> dict:
    global _META
    if _META is None:
        p = MODELOS_DIR / "meta.json"
        _META = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    return _META


def carregar_classificador(force_reload: bool = False) -> Any:
    global _MODELO
    if _MODELO is not None and not force_reload:
        return _MODELO
    path = MODELOS_DIR / "clf_derma.joblib"
    if not path.is_file():
        raise FileNotFoundError(
            f"Modelo em falta: {path}. Corra `python treinar_classificador.py` nesta pasta."
        )
    _MODELO = joblib.load(path)
    return _MODELO


def prever_de_vector(imagem_flat_normalizada: np.ndarray) -> dict[str, Any]:
    """`imagem_flat_normalizada`: (784,) floats em [0,1]."""
    clf = carregar_classificador()
    x = np.asarray(imagem_flat_normalizada, dtype=np.float32).reshape(1, -1)
    proba = clf.predict_proba(x)[0]
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
