"""ResNet18 com **transfer learning** (ImageNet) para DermaMNIST (7 classes).

As imagens 28×28 são redimensionadas bilinearmente para 224×224, replicadas em 3 canais
e normalizadas com média/desvio ImageNet — padrão típico ao reutilizar backbone CNN.
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def construir_resnet18_transfer(num_classes: int = 7) -> nn.Module:
    pesos = ResNet18_Weights.IMAGENET1K_V1
    m = resnet18(weights=pesos)
    embutida = m.fc.in_features
    m.fc = nn.Linear(embutida, num_classes)
    return m


def preprocess_flat_para_resnet(
    imagem_flat_784: np.ndarray,
    device: torch.device,
) -> torch.Tensor:
    """`(N, 784)` ou `(784,)` em [0,1] → tensor `(N, 3, 224, 224)` normalizado."""
    x = np.asarray(imagem_flat_784, dtype=np.float32)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    n = x.shape[0]
    t = torch.from_numpy(x).view(n, 1, 28, 28)
    t = torch.nn.functional.interpolate(
        t,
        size=(224, 224),
        mode="bilinear",
        align_corners=False,
    )
    t = t.repeat(1, 3, 1, 1).to(device)
    mean = torch.tensor(IMAGENET_MEAN, device=device).view(1, 3, 1, 1)
    std = torch.tensor(IMAGENET_STD, device=device).view(1, 3, 1, 1)
    return (t - mean) / std


def congelar_exceto_fc(modelo: nn.Module) -> None:
    for p in modelo.parameters():
        p.requires_grad = False
    for p in modelo.fc.parameters():
        p.requires_grad = True


def descongelar_layer4(modelo: nn.Module) -> None:
    for p in modelo.layer4.parameters():
        p.requires_grad = True
