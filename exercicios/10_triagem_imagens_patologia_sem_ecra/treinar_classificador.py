"""
Treino **CNN** (ResNet18 + transfer learning ImageNet) no **DermaMNIST** (MedMNIST).

- Fase 1: só camada `fc` (backbone congelado).
- Fase 2: descongela `layer4` + `fc` com learning rate menor.

Saídas:
- `models/cnn_derma.pt` — state_dict do modelo
- `models/cnn_derma_meta.json` — hiperparâmetros e métricas
- `models/meta.json` — compatível com `classificador.py` (classes, forma da imagem, etc.)
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from medmnist import DermaMNIST
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight
from torch.utils.data import DataLoader, TensorDataset

from cnn_derma import (
    construir_resnet18_transfer,
    congelar_exceto_fc,
    descongelar_layer4,
    preprocess_flat_para_resnet,
)
from triagem import CLASSES_DERMA_MNIST

N_CLASSES = 7


def carregar_xy(split: str) -> tuple[np.ndarray, np.ndarray]:
    """Cada imagem → vector (784,) em [0,1]."""
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


def _one_epoch(
    modelo: nn.Module,
    loader: DataLoader,
    device: torch.device,
    criterion: nn.Module,
    optimizer: optim.Optimizer | None,
    treino: bool,
) -> tuple[float, float]:
    if treino:
        modelo.train()
    else:
        modelo.eval()
    loss_acc = 0.0
    correct = 0
    total = 0
    with torch.set_grad_enabled(treino):
        for xb, yb in loader:
            yb = yb.to(device)
            t_in = preprocess_flat_para_resnet(xb.numpy(), device)
            if treino and optimizer is not None:
                optimizer.zero_grad(set_to_none=True)
            logits = modelo(t_in)
            loss = criterion(logits, yb)
            if treino and optimizer is not None:
                loss.backward()
                optimizer.step()
            loss_acc += loss.item() * xb.size(0)
            pred = logits.argmax(dim=1)
            correct += (pred == yb).sum().item()
            total += xb.size(0)
    return loss_acc / max(total, 1), correct / max(total, 1)


def _evaluate(
    modelo: nn.Module,
    x_val: np.ndarray,
    y_val: np.ndarray,
    device: torch.device,
    batch_size: int,
) -> tuple[list[int], list[int]]:
    modelo.eval()
    y_pred: list[int] = []
    y_true: list[int] = []
    n = len(x_val)
    with torch.no_grad():
        for start in range(0, n, batch_size):
            sl = slice(start, min(start + batch_size, n))
            xb = x_val[sl]
            yb = y_val[sl]
            t_in = preprocess_flat_para_resnet(xb, device)
            logits = modelo(t_in)
            preds = logits.argmax(dim=1).cpu().numpy().tolist()
            y_pred.extend(preds)
            y_true.extend(yb.tolist())
    return y_true, y_pred


def main() -> None:
    t0 = time.perf_counter()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    out_dir = Path(__file__).resolve().parent / "models"
    out_dir.mkdir(parents=True, exist_ok=True)
    path_pt = out_dir / "cnn_derma.pt"
    path_train_meta = out_dir / "cnn_derma_meta.json"
    path_app_meta = out_dir / "meta.json"

    print("[ex10] A carregar DermaMNIST (primeira vez pode demorar)…", flush=True)
    x_train, y_train = carregar_xy("train")
    x_val, y_val = carregar_xy("val")

    print(
        f"Formas: train {x_train.shape}, val {x_val.shape}. "
        f"Device: {device}.",
        flush=True,
    )

    batch = 64
    ds_tr = TensorDataset(
        torch.from_numpy(x_train).float(), torch.from_numpy(y_train).long()
    )
    ds_val = TensorDataset(
        torch.from_numpy(x_val).float(), torch.from_numpy(y_val).long()
    )
    dl_tr = DataLoader(ds_tr, batch_size=batch, shuffle=True, num_workers=0)
    dl_val = DataLoader(ds_val, batch_size=batch, shuffle=False, num_workers=0)

    modelo = construir_resnet18_transfer(N_CLASSES).to(device)
    congelar_exceto_fc(modelo)

    cw = compute_class_weight("balanced", classes=np.arange(N_CLASSES), y=y_train)
    pesos = torch.tensor(cw, dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=pesos)

    lr_fc = 1e-2
    epochs_fc = 6
    opt = optim.AdamW(modelo.fc.parameters(), lr=lr_fc, weight_decay=1e-4)

    for ep in range(epochs_fc):
        loss_tr, acc_tr = _one_epoch(modelo, dl_tr, device, criterion, opt, True)
        loss_ev, acc_ev = _one_epoch(modelo, dl_val, device, criterion, None, False)
        print(
            f"  [FC] Epoch {ep + 1}/{epochs_fc} | "
            f"train loss={loss_tr:.4f} acc={acc_tr:.4f} | "
            f"val loss={loss_ev:.4f} acc={acc_ev:.4f}",
            flush=True,
        )

    descongelar_layer4(modelo)
    opt2 = optim.AdamW(
        [p for p in modelo.parameters() if p.requires_grad],
        lr=1e-4,
        weight_decay=1e-4,
    )
    epochs_ft = 5
    for ep in range(epochs_ft):
        loss_tr, acc_tr = _one_epoch(modelo, dl_tr, device, criterion, opt2, True)
        loss_ev, acc_ev = _one_epoch(modelo, dl_val, device, criterion, None, False)
        print(
            f"  [FT] Epoch {ep + 1}/{epochs_ft} | "
            f"train loss={loss_tr:.4f} acc={acc_tr:.4f} | "
            f"val loss={loss_ev:.4f} acc={acc_ev:.4f}",
            flush=True,
        )

    y_true, y_pred = _evaluate(modelo, x_val, y_val, device, batch_size=batch)
    relatorio = classification_report(
        y_true,
        y_pred,
        target_names=list(CLASSES_DERMA_MNIST),
        digits=3,
        zero_division=0,
    )
    print("\n=== Relatório (split `val` MedMNIST) ===\n", relatorio, flush=True)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(N_CLASSES)))

    torch.save(modelo.state_dict(), path_pt)

    train_extra = {
        "modelo": "ResNet18 transfer (ImageNet1K_V1) + fc 7 classes",
        "arquivo_pt": path_pt.name,
        "n_classes": N_CLASSES,
        "device_treino": str(device),
        "epochs_fc": epochs_fc,
        "epochs_ft": epochs_ft,
        "lr_fc": lr_fc,
        "lr_ft": 1e-4,
        "batch_size": batch,
        "tempo_s": round(time.perf_counter() - t0, 2),
        "val_accuracy": float(np.mean(np.array(y_true) == np.array(y_pred))),
        "confusion_matrix_val": cm.tolist(),
    }
    path_train_meta.write_text(
        json.dumps(train_extra, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    app_meta = {
        "classes": list(CLASSES_DERMA_MNIST),
        "image_shape": [28, 28],
        "val_samples": int(len(y_val)),
        "weights_file": path_pt.name,
        "backbone": "resnet18_imagenet_transfer",
    }
    path_app_meta.write_text(
        json.dumps(app_meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n[ex10] Modelo: {path_pt}", flush=True)
    print(f"[ex10] Metadados treino: {path_train_meta}", flush=True)
    print(f"[ex10] Metadados app: {path_app_meta}", flush=True)
    print(f"Tempo total: {train_extra['tempo_s']}s", flush=True)


if __name__ == "__main__":
    main()
