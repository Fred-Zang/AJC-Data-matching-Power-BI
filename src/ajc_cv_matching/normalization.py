from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Mapping

from unidecode import unidecode

# Historical V1 deliberately preserved technical tokens containing +, # or dots.
PROTECTED_TOKENS = ("C++", "C#", ".NET", "ASP.NET", "MVC.NET", "ADO.NET")
PLACEHOLDERS = {token: f"XTECHTOKEN{chr(65 + idx)}X" for idx, token in enumerate(PROTECTED_TOKENS)}


@dataclass(frozen=True)
class TokenizedDocument:
    tokens: tuple[str, ...]
    frequencies: Mapping[str, int]


def normalize_text(text: str) -> str:
    """Upper-case, strip accents and normalize punctuation while preserving technical tokens."""
    value = unidecode(str(text).upper())
    value = re.sub(r"C\s*\+\s*\+", "C++", value)
    value = re.sub(r"C\s*#", "C#", value)

    for token, placeholder in PLACEHOLDERS.items():
        value = value.replace(token, placeholder)

    # Keep letters, digits and spaces; punctuation becomes a separator.
    value = re.sub(r"[^A-Z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    for token, placeholder in PLACEHOLDERS.items():
        value = value.replace(placeholder, token)
    return value


def tokenize(
    text: str,
    *,
    stopwords: Iterable[str] = (),
    variants: Mapping[str, str] | None = None,
) -> TokenizedDocument:
    stop = {normalize_text(word) for word in stopwords if str(word).strip()}
    variants = {normalize_text(k): normalize_text(v) for k, v in (variants or {}).items()}

    raw_tokens = [token for token in normalize_text(text).split(" ") if token]
    tokens: list[str] = []
    for token in raw_tokens:
        if token.isdigit() or token in stop:
            continue
        tokens.append(variants.get(token, token))

    frequencies = Counter(tokens)
    return TokenizedDocument(tokens=tuple(tokens), frequencies=dict(frequencies))
