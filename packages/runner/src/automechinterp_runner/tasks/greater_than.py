"""Greater-Than task: Does the model predict the correct comparison outcome?

Tests whether the model can identify which of two numbers is greater,
using clean/corrupt prompt pairs where the comparison is flipped.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "paraphrase", "structured", "negated"]


def _number_pairs() -> list[tuple[int, int]]:
    """Return pairs of (smaller, larger) single-digit numbers."""
    pairs = []
    for a in range(1, 10):
        for b in range(a + 1, 10):
            pairs.append((a, b))
    return pairs


def _prompts(smaller: int, larger: int, variant: str) -> tuple[str, str]:
    if variant == "paraphrase":
        clean = f"Is {larger} bigger than {smaller}? The answer is"
        corrupt = f"Is {smaller} bigger than {larger}? The answer is"
    elif variant == "structured":
        clean = f"Compare: {smaller} vs {larger}. The larger number is"
        corrupt = f"Compare: {larger} vs {smaller}. The larger number is"
    elif variant == "negated":
        clean = f"It is not the case that {smaller} exceeds {larger}. True or False? Answer:"
        corrupt = f"It is not the case that {larger} exceeds {smaller}. True or False? Answer:"
    else:
        clean = f"The number {larger} is greater than {smaller}. True or False? Answer:"
        corrupt = f"The number {smaller} is greater than {larger}. True or False? Answer:"
    return clean, corrupt


def _get_true_false_tokens(model: Any) -> tuple[int, int]:
    """Get token IDs for ' True' and ' False'."""
    try:
        true_tok = int(model.to_single_token(" True"))
        false_tok = int(model.to_single_token(" False"))
        return true_tok, false_tok
    except Exception:
        try:
            true_tok = int(model.to_single_token(" Yes"))
            false_tok = int(model.to_single_token(" No"))
            return true_tok, false_tok
        except Exception:
            raise ValueError("Cannot find True/False or Yes/No single tokens")


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    true_tok, false_tok = _get_true_false_tokens(model)
    pairs = _number_pairs()
    rng = random.Random(seed)
    rows: list[TaskExample] = []

    for _ in range(n):
        smaller, larger = rng.choice(pairs)
        clean, corrupt = _prompts(smaller, larger, prompt_variant)
        rows.append(
            TaskExample(
                clean_prompt=clean,
                corrupt_prompt=corrupt,
                target_token=true_tok,
                distractor_token=false_tok,
            )
        )
    return rows


def metric(logits: Any, target_token: int, distractor_token: int) -> float:
    value = logits[0, -1, target_token] - logits[0, -1, distractor_token]
    if hasattr(value, "detach"):
        value = value.detach()
    return float(value)


class GreaterThanTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
