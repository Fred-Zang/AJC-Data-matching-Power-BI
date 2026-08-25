from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class MatchResult:
    boolean_score: float
    weighted_score: float
    matched_tokens: tuple[str, ...]
    missing_tokens: tuple[str, ...]


def score_tokens(
    cv_tokens: Iterable[str],
    expected_tokens: Iterable[str],
    weights: Mapping[str, float] | None = None,
) -> MatchResult:
    """Compute the two transparent scores used by the public reconstruction.

    - boolean_score: percentage of expected tokens present at least once in the CV;
    - weighted_score: same presence matrix, but each expected token carries an explicit weight.

    This is intentionally deterministic. Token frequency is useful for audit but does not create
    hidden relevance in the final score.
    """
    present = set(cv_tokens)
    expected = tuple(dict.fromkeys(expected_tokens))
    if not expected:
        return MatchResult(0.0, 0.0, (), ())

    matched = tuple(token for token in expected if token in present)
    missing = tuple(token for token in expected if token not in present)
    boolean_score = round(100 * len(matched) / len(expected), 2)

    weights = weights or {}
    total_weight = sum(float(weights.get(token, 1.0)) for token in expected)
    matched_weight = sum(float(weights.get(token, 1.0)) for token in matched)
    weighted_score = round(100 * matched_weight / total_weight, 2) if total_weight else 0.0

    return MatchResult(boolean_score, weighted_score, matched, missing)
