"""Transparent, deterministic metrics for prompt-evaluation records."""

import re
from collections.abc import Iterable


def concept_coverage(notes: str, expected_concepts: Iterable[str]) -> dict[str, object]:
    """Calculate exact expected-concept coverage; this is not a correctness claim."""

    normalized_notes = notes.casefold()
    concepts = tuple(expected_concepts)
    matched = [concept for concept in concepts if concept.casefold() in normalized_notes]
    percentage = round((len(matched) / len(concepts)) * 100, 2) if concepts else 100.0
    return {"matched": matched, "expected": list(concepts), "percent": percentage}


def readability(notes: str) -> dict[str, float | int]:
    """Return basic text statistics and an approximate Flesch reading-ease score."""

    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", notes)
    sentences = [segment for segment in re.split(r"[.!?]+", notes) if segment.strip()]
    word_count = len(words)
    sentence_count = max(len(sentences), 1)
    syllable_count = sum(_estimate_syllables(word) for word in words)
    score = (
        206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (syllable_count / word_count)
        if word_count
        else 0.0
    )
    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "flesch_reading_ease": round(score, 2),
    }


def difficulty_alignment(notes: str, difficulty: str) -> dict[str, object]:
    """Score observable cues for the requested level, not pedagogical quality."""

    expected_cues = {
        "beginner": ("example", "intuitive", "simple", "plain language"),
        "intermediate": ("formula", "assumption", "worked example", "technical"),
        "advanced": ("optimization", "complexity", "limitation", "mathematical"),
    }
    cues = expected_cues[difficulty]
    normalized_notes = notes.casefold()
    matched = [cue for cue in cues if cue in normalized_notes]
    return {
        "matched_cues": matched,
        "expected_cues": list(cues),
        "percent": round((len(matched) / len(cues)) * 100, 2),
    }


def _estimate_syllables(word: str) -> int:
    groups = re.findall(r"[aeiouy]+", word.casefold())
    return max(len(groups), 1)
