from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from .config import MAX_DOCUMENT_BYTES
from .document_processing import extract_text
from .normalization import tokenize
from .reference import PathwayReference
from .scoring import score_tokens
from .storage import AuditStore


def _document_id(path: Path, mode: str) -> str:
    if mode == "name":
        return path.stem
    if mode != "hash":
        raise ValueError("document_id_mode must be 'hash' or 'name'")
    if path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError("document exceeds the configured size limit")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"cv_{digest.hexdigest()[:16]}"


def process_cv_directory(
    cv_dir: Path,
    references: dict[str, PathwayReference],
    *,
    variants: dict[str, str],
    output_dir: Path,
    document_id_mode: str = "hash",
    audit_db: Path | None = None,
) -> list[dict[str, object]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    token_dir = output_dir / "tokens"
    token_dir.mkdir(parents=True, exist_ok=True)
    store = AuditStore(audit_db) if audit_db else None

    rows: list[dict[str, object]] = []
    matrix: dict[str, dict[str, int]] = {}
    all_reference_tokens = sorted({token for ref in references.values() for token in ref.tokens})

    for path in sorted(p for p in cv_dir.iterdir() if p.is_file() and not p.name.startswith(".")):
        doc_id = _document_id(path, document_id_mode)
        text = extract_text(path)
        # Historical V1 did not remove stop words from CVs: only the reference vocabulary is filtered.
        tokenized = tokenize(text, stopwords=(), variants=variants)
        matrix[doc_id] = {token: int(token in tokenized.frequencies) for token in all_reference_tokens}

        (token_dir / f"{doc_id}.json").write_text(
            json.dumps(
                {"document_id": doc_id, "frequencies": tokenized.frequencies},
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        document_rows: list[dict[str, object]] = []
        for pathway_id, ref in references.items():
            score = score_tokens(tokenized.tokens, ref.tokens, ref.weights)
            row = {
                "document_id": doc_id,
                "pathway_id": pathway_id,
                "pathway_title": ref.pathway_title,
                "boolean_score": score.boolean_score,
                "weighted_score": score.weighted_score,
                "matched_tokens": " | ".join(score.matched_tokens),
                "missing_tokens": " | ".join(score.missing_tokens),
            }
            rows.append(row)
            document_rows.append(row)

        if store:
            store.replace_document_results(doc_id, document_rows)

    rows.sort(key=lambda row: (str(row["document_id"]), -float(row["weighted_score"]), -float(row["boolean_score"])))
    pd.DataFrame(rows).to_csv(output_dir / "matching_results.csv", index=False)

    matrix_df = pd.DataFrame.from_dict(matrix, orient="index").fillna(0).astype(int)
    matrix_df.index.name = "document_id"
    matrix_df.reindex(sorted(matrix_df.columns), axis=1).to_csv(output_dir / "boolean_matrix.csv")
    return rows
