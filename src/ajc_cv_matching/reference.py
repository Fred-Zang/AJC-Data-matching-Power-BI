from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .normalization import tokenize


@dataclass(frozen=True)
class PathwayReference:
    pathway_id: str
    pathway_title: str
    modules: tuple[str, ...]
    tokens: tuple[str, ...]
    weights: dict[str, float]


def load_stopwords(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")}


def load_variants(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            variant = (row.get("variant") or "").strip()
            canonical = (row.get("canonical") or "").strip()
            if variant and canonical:
                result[variant] = canonical
    return result


def load_weights(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    result: dict[str, float] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            token = (row.get("token") or "").strip()
            if token:
                result[token] = float(row.get("weight") or 1)
    return result


def build_references(
    catalog_path: Path,
    *,
    stopwords: Iterable[str],
    variants: dict[str, str],
    explicit_weights: dict[str, float] | None = None,
) -> dict[str, PathwayReference]:
    """Build a canonical vocabulary from pathway and module labels.

    V1 principle: training labels define the expected vocabulary. Repeated terms are retained
    as frequencies for audit, while the final matching uses presence and an explicit weight.
    """
    explicit_weights = explicit_weights or {}
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    with catalog_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            pathway_id = (row.get("pathway_id") or "").strip()
            if pathway_id:
                grouped[pathway_id].append(row)

    references: dict[str, PathwayReference] = {}
    for pathway_id, rows in grouped.items():
        pathway_title = (rows[0].get("pathway_title") or pathway_id).strip()
        modules = tuple((row.get("module_title") or "").strip() for row in rows if (row.get("module_title") or "").strip())

        corpus = " ".join([pathway_title, *modules])
        tokenized = tokenize(corpus, stopwords=stopwords, variants=variants)
        counts = Counter(tokenized.tokens)
        unique_tokens = tuple(sorted(counts))
        weights = {token: float(explicit_weights.get(token, 1.0)) for token in unique_tokens}
        references[pathway_id] = PathwayReference(
            pathway_id=pathway_id,
            pathway_title=pathway_title,
            modules=modules,
            tokens=unique_tokens,
            weights=weights,
        )
    return references
