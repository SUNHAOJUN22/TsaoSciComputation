from __future__ import annotations

import re
from dataclasses import dataclass

from ..registries import workflows

TOKEN_RE = re.compile("[a-z0-9]+|[一-鿿]+", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class RouteDecision:
    workflow: str
    score: float
    matched_terms: tuple[str, ...]
    alternatives: tuple[tuple[str, float], ...]
    explanation: str


def _tokens(text: str) -> set[str]:
    lowered = text.casefold().replace("_", " ").replace("-", " ")
    return set(TOKEN_RE.findall(lowered))


def route_question(question: str) -> RouteDecision:
    if not question.strip():
        raise ValueError("question must be non-empty")
    text = question.casefold()
    tokens = _tokens(question)
    scored: list[tuple[str, float, tuple[str, ...]]] = []
    for w in workflows():
        matches = []
        score = 0.0
        for term in w["keywords"]:
            normalized = term.casefold()
            if normalized in text:
                matches.append(term)
                score += 3.0
            else:
                parts = _tokens(normalized)
                overlap = parts & tokens
                if overlap:
                    matches.extend(sorted(overlap))
                    score += float(len(overlap))
        slug_terms = set(w["slug"].split("-"))
        score += 0.35 * len(slug_terms & tokens)
        scored.append((w["slug"], score, tuple(dict.fromkeys(matches))))
    scored.sort(key=lambda x: (-x[1], x[0]))
    best = scored[0]
    if best[1] <= 0:
        best = ("scale-selection", 0.0, ())
    alternatives = tuple(((slug, score) for slug, score, _ in scored[1:4]))
    return RouteDecision(
        best[0],
        best[1],
        best[2],
        alternatives,
        f"Selected {best[0]} from matched terms: {', '.join(best[2]) or 'none; clarification required'}",
    )
