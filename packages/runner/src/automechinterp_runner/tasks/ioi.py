"""IOI task module — wrapped to satisfy the V7 TaskModule interface."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "paraphrase", "structural", "adversarial"]


def _candidate_names() -> list[str]:
    return [
        "John", "Mary", "James", "Sarah", "David",
        "Lisa", "Robert", "Karen", "Michael", "Laura",
    ]


def _single_token_name_ids(model: Any) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for name in _candidate_names():
        try:
            token_id = int(model.to_single_token(f" {name}"))
        except Exception:
            continue
        rows.append((name, token_id))
    if len(rows) < 4:
        raise ValueError("Not enough single-token names for IOI prompt generation")
    return rows


def _prompts(a: str, b: str, variant: str) -> tuple[str, str]:
    if variant == "paraphrase":
        clean = f"After {a} met {b}, {b} handed a gift to"
        corrupt = f"After {a} met {b}, {a} handed a gift to"
    elif variant == "structural":
        clean = f"{b} was waiting for {a}. Then {a} passed the ball to"
        corrupt = f"{b} was waiting for {a}. Then {b} passed the ball to"
    elif variant == "adversarial":
        clean = f"It was {b} who saw {a}, and later {a} sent a letter to"
        corrupt = f"It was {b} who saw {a}, and later {b} sent a letter to"
    else:
        # default to base template
        clean = f"When {a} and {b} went to the store, {b} gave a book to"
        corrupt = f"When {a} and {b} went to the store, {a} gave a book to"
    return clean, corrupt


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")
    try:
        names = _single_token_name_ids(model)
    except ValueError as e:
        # bubble up a structured task-level
        # error so the runner converts the failure into a ``not_evaluated``
        # cell rather than aborting the whole bundle.
        raise ValueError(f"ioi: cannot sample examples: {e}") from e
    if len(names) < 2:
        raise ValueError(
            f"ioi: not enough single-token names ({len(names)}) for "
            "rng.sample(..., k=2). Need >= 2 entries."
        )
    rng = random.Random(seed)
    rows: list[TaskExample] = []
    for _ in range(n):
        (a, a_tok), (b, b_tok) = rng.sample(names, k=2)
        clean_prompt, corrupt_prompt = _prompts(a=a, b=b, variant=prompt_variant)
        # Token-parity guard: most interventions assume aligned positions.
        try:
            clean_len = int(model.to_tokens(clean_prompt).shape[-1])
            corrupt_len = int(model.to_tokens(corrupt_prompt).shape[-1])
            if clean_len != corrupt_len:
                continue  # skip mis-aligned pair; loop continues to next sample
        except Exception:
            # Tokenizer hiccup (e.g., custom vocab, BOS variant): skip the
            # example rather than appending an unverified pair. Silent fall-
            # through here would let mis-aligned positions reach downstream
            # interventions.
            continue
        rows.append(
            TaskExample(
                clean_prompt=clean_prompt,
                corrupt_prompt=corrupt_prompt,
                target_token=a_tok,
                distractor_token=b_tok,
            )
        )
    if not rows:
        raise ValueError("ioi: produced zero token-aligned examples after sampling")
    return rows


def metric(logits: Any, target_token: int, distractor_token: int) -> float:
    value = logits[0, -1, target_token] - logits[0, -1, distractor_token]
    if hasattr(value, "detach"):
        value = value.detach()
    return float(value)


class IOITaskModule:
    """Wrapper satisfying TaskModule protocol."""
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
