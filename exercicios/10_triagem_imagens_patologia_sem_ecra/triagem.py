"""Regras de **prioridade** para triagem (combina confiança do classificador e patologia alvo).

A patologia prioritária por defeito é **melanoma** (índice 4 em DermaMNIST / MedMNIST).
Altere com `INDICE_PATOLOGIA_PRIORITARIA` ou variável de ambiente `EX10_PATOLOGIA_INDICE`.
"""

from __future__ import annotations

import os


# Ordem MedMNIST DermaMNIST (7 classes)
CLASSES_DERMA_MNIST: tuple[str, ...] = (
    "actinic_keratoses_and_intraepithelial_carcinoma",
    "basal_cell_carcinoma",
    "benign_keratosis_like_lesions",
    "dermatofibroma",
    "melanoma",
    "melanocytic_nevi",
    "vascular_lesions",
)


def indice_patologia_prioritaria() -> int:
    raw = os.environ.get("EX10_PATOLOGIA_INDICE", "").strip()
    if raw.isdigit():
        return int(raw)
    return 4  # melanoma


def nome_patologia_prioritaria() -> str:
    i = indice_patologia_prioritaria()
    if 0 <= i < len(CLASSES_DERMA_MNIST):
        return CLASSES_DERMA_MNIST[i]
    return "desconhecida"


def calcular_prioridade(
    probabilidades: list[float],
    classe_predita: int,
) -> float:
    """Score 0–100: maior → atendimento mais urgente (heurística pedagógica)."""
    if not probabilidades or classe_predita < 0 or classe_predita >= len(probabilidades):
        return 0.0
    alvo = indice_patologia_prioritaria()
    conf_top = float(probabilidades[classe_predita])
    prob_alvo = float(probabilidades[alvo]) if alvo < len(probabilidades) else 0.0
    score = conf_top * 45.0
    if classe_predita == alvo:
        score += 35.0
    score += prob_alvo * 25.0
    return round(min(100.0, score), 2)
