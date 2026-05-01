"""Treina um classificador leve (regressão logística) sobre **DermaMNIST** e grava `models/clf_derma.joblib`.

Dados: conjunto público **MedMNIST** (DermaMNIST), derivado de imagens dermatoscópicas agregadas
(HAM10000, etc.) — uso académico; ver https://medmnist.com/ .

Uso na pasta do exercício:
  python treinar_classificador.py
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from medmnist import DermaMNIST
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from triagem import CLASSES_DERMA_MNIST

MODELOS_DIR = Path(__file__).resolve().parent / "models"


def _carregar_xy(split: str) -> tuple[np.ndarray, np.ndarray]:
    ds = DermaMNIST(split=split, download=True)
    xs: list[np.ndarray] = []
    ys: list[int] = []
    for i in range(len(ds)):
        img, lab = ds[i]
        if hasattr(img, "convert"):
            arr = np.asarray(img.convert("L"), dtype=np.float32)
        else:
            arr = np.asarray(img, dtype=np.float32)
        if arr.ndim == 3:
            arr = np.squeeze(arr)
        xs.append(arr.reshape(-1) / 255.0)
        ys.append(int(np.asarray(lab).reshape(-1)[0]))
    return np.stack(xs), np.array(ys, dtype=np.int64)


def main() -> None:
    MODELOS_DIR.mkdir(parents=True, exist_ok=True)
    print("[ex10] A descarregar DermaMNIST (primeira vez pode demorar)…", flush=True)
    x_train, y_train = _carregar_xy("train")
    x_val, y_val = _carregar_xy("val")

    # Subconjunto para treino rápido em CPU (pode aumentar para melhor métrica)
    rng = np.random.default_rng(42)
    n = min(5000, len(x_train))
    idx = rng.choice(len(x_train), size=n, replace=False)
    x_sub, y_sub = x_train[idx], y_train[idx]

    x_tr, x_te, y_tr, y_te = train_test_split(
        x_sub, y_sub, test_size=0.15, random_state=42, stratify=y_sub
    )
    clf = LogisticRegression(
        max_iter=300,
        class_weight="balanced",
        solver="lbfgs",
        random_state=42,
    )
    clf.fit(x_tr, y_tr)
    print(classification_report(y_te, clf.predict(x_te), target_names=list(CLASSES_DERMA_MNIST)))

    modelo_path = MODELOS_DIR / "clf_derma.joblib"
    joblib.dump(clf, modelo_path)
    meta = {
        "classes": list(CLASSES_DERMA_MNIST),
        "image_shape": [28, 28],
        "val_samples": len(x_val),
    }
    (MODELOS_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[ex10] Modelo gravado em {modelo_path}", flush=True)


if __name__ == "__main__":
    main()
