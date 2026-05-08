"""Sentiment Direction task.

Tests whether the model predicts the correct sentiment direction
(positive vs negative) for sentiment-laden prompts, using
clean/corrupt pairs where sentiment-bearing words are swapped.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "review", "statement", "contrast"]

_POSITIVE_WORDS = ["great", "wonderful", "excellent", "amazing", "fantastic"]
_NEGATIVE_WORDS = ["terrible", "horrible", "awful", "dreadful", "atrocious"]


def _get_sentiment_tokens(model: Any) -> tuple[int, int]:
    """Get token IDs for positive/negative sentiment markers."""
    for pos, neg in [(" good", " bad"), (" positive", " negative"), (" great", " terrible")]:
        try:
            pos_tok = int(model.to_single_token(pos))
            neg_tok = int(model.to_single_token(neg))
            return pos_tok, neg_tok
        except Exception:
            continue
    raise ValueError("Cannot find single-token sentiment markers")


def _prompts(pos_word: str, neg_word: str, variant: str) -> tuple[str, str]:
    if variant == "review":
        clean = f"This movie was {pos_word}. Overall, the experience was"
        corrupt = f"This movie was {neg_word}. Overall, the experience was"
    elif variant == "statement":
        clean = f"I had a {pos_word} day today. My mood is"
        corrupt = f"I had a {neg_word} day today. My mood is"
    elif variant == "contrast":
        clean = f"Unlike the {neg_word} start, the ending was truly {pos_word}. In summary, it was"
        corrupt = f"Unlike the {pos_word} start, the ending was truly {neg_word}. In summary, it was"
    else:
        clean = f"The food was {pos_word}. I thought it was"
        corrupt = f"The food was {neg_word}. I thought it was"
    return clean, corrupt


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    pos_tok, neg_tok = _get_sentiment_tokens(model)
    rng = random.Random(seed)
    rows: list[TaskExample] = []

    for _ in range(n):
        pos_word = rng.choice(_POSITIVE_WORDS)
        neg_word = rng.choice(_NEGATIVE_WORDS)
        clean, corrupt = _prompts(pos_word, neg_word, prompt_variant)

        rows.append(
            TaskExample(
                clean_prompt=clean,
                corrupt_prompt=corrupt,
                target_token=pos_tok,
                distractor_token=neg_tok,
            )
        )
    return rows


def metric(logits: Any, target_token: int, distractor_token: int) -> float:
    value = logits[0, -1, target_token] - logits[0, -1, distractor_token]
    if hasattr(value, "detach"):
        value = value.detach()
    return float(value)


class SentimentTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
