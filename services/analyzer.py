"""Toxicity analysis service: calls external ML model or local mock scorer."""

from __future__ import annotations

import config

TOXIC_KEYWORDS = ("hate", "kill", "stupid", "idiot", "damn", "fuck", "shit")


def _mock_analyze(text: str) -> dict:
    lowered = text.lower()
    hits = sum(1 for word in TOXIC_KEYWORDS if word in lowered)
    toxicity = min(100.0, hits * 25.0)
    return {
        "toxicity": toxicity,
        "severe_toxicity": toxicity * 0.8,
        "obscene": toxicity * 0.6,
        "identity_attack": toxicity * 0.5,
        "insult": toxicity * 0.7,
        "threat": toxicity * 0.4,
        "sexual_explicit": 0.0,
        "average": toxicity,
    }


def _max_toxicity(result: dict) -> float:
    return max(
        result.get("toxicity") or 0,
        result.get("severe_toxicity") or 0,
        result.get("obscene") or 0,
        result.get("identity_attack") or 0,
        result.get("insult") or 0,
        result.get("threat") or 0,
        result.get("sexual_explicit") or 0,
        result.get("average") or 0,
    )


def analyze_text(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("Text is required")

    if config.ANALYZER_URL == "mock":
        result = _mock_analyze(text)
    else:
        import requests

        response = requests.post(
            config.ANALYZER_URL,
            json={"text": text},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("success") or not payload.get("result"):
            raise RuntimeError("Invalid analyzer response")
        result = payload["result"]

    score = _max_toxicity(result)
    return {
        "success": True,
        "result": result,
        "toxicity_score": score,
        "is_profane": score >= 70,
    }

