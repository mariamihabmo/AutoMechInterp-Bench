"""Arithmetic task.

Tests whether the model can perform simple addition, using
clean/corrupt pairs where one operand is changed.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "worded", "equation", "story"]


def _get_number_tokens(model: Any) -> dict[int, int]:
    """Map small numbers to their single-token IDs."""
    valid: dict[int, int] = {}
    for num in range(0, 20):
        for prefix in [f" {num}", f"{num}"]:
            try:
                tok = int(model.to_single_token(prefix))
                valid[num] = tok
                break
            except Exception:
                continue
    return valid


def _prompts(a: int, b: int, wrong_b: int, variant: str) -> tuple[str, str]:
    if variant == "worded":
        clean = f"What is {a} plus {b}? The answer is"
        corrupt = f"What is {a} plus {wrong_b}? The answer is"
    elif variant == "equation":
        clean = f"{a} + {b} ="
        corrupt = f"{a} + {wrong_b} ="
    elif variant == "story":
        clean = f"Alice has {a} apples and Bob gives her {b} more. Now she has"
        corrupt = f"Alice has {a} apples and Bob gives her {wrong_b} more. Now she has"
    else:
        clean = f"Calculate: {a} + {b} ="
        corrupt = f"Calculate: {a} + {wrong_b} ="
    return clean, corrupt


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    number_tokens = _get_number_tokens(model)
    if len(number_tokens) < 10:
        raise ValueError("Not enough single-token numbers for arithmetic task")

    rng = random.Random(seed)
    rows: list[TaskExample] = []
    available_nums = sorted(number_tokens.keys())

    for _ in range(n):
        # Pick a, b such that a+b is in our token set
        attempts = 0
        while attempts < 100:
            a = rng.choice([x for x in available_nums if x < 10])
            b = rng.choice([x for x in available_nums if x < 10])
            correct = a + b
            if correct in number_tokens:
                # Find a wrong_b that produces a different (valid) result
                wrong_candidates = [
                    wb for wb in available_nums
                    if wb != b and wb < 10 and (a + wb) in number_tokens and (a + wb) != correct
                ]
                if wrong_candidates:
                    wrong_b = rng.choice(wrong_candidates)
                    break
            attempts += 1
        else:
            continue

        clean, corrupt = _prompts(a, b, wrong_b, prompt_variant)
        target_tok = number_tokens[correct]
        distractor_tok = number_tokens[a + wrong_b]

        rows.append(
            TaskExample(
                clean_prompt=clean,
                corrupt_prompt=corrupt,
                target_token=target_tok,
                distractor_token=distractor_tok,
            )
        )
    return rows


def metric(logits: Any, target_token: int, distractor_token: int) -> float:
    value = logits[0, -1, target_token] - logits[0, -1, distractor_token]
    if hasattr(value, "detach"):
        value = value.detach()
    return float(value)


class ArithmeticTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
