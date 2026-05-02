"""Embeddings com Hugging Face Transformers (mean pooling) — PT multilingue."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


def _mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    summed = torch.sum(last_hidden_state * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


class EmbedderHF:
    """Modelo sentence-transformers compatível via Transformers nativo."""

    def __init__(
        self,
        model_id: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    ) -> None:
        self.model_id = model_id
        self._tok = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModel.from_pretrained(model_id)
        self._model.eval()

    @torch.inference_mode()
    def encode(self, texts: list[str], batch_size: int = 16) -> np.ndarray:
        out_vecs: list[np.ndarray] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            enc = self._tok(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            outs = self._model(**enc)
            pooled = _mean_pool(outs.last_hidden_state, enc["attention_mask"])
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            out_vecs.append(pooled.cpu().numpy().astype("float32"))
        return np.vstack(out_vecs)


def caminho_indices() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "indices"


def caminho_documentos() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "documentos"
