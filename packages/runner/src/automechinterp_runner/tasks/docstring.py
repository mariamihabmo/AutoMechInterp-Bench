"""Docstring Completion task.

Tests whether the model correctly completes a function docstring
based on the function signature, using clean/corrupt pairs where
the function name is swapped.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "detailed", "brief", "returns"]

_FUNCTIONS = [
    ("add", "sum", "subtract"),
    ("multiply", "product", "divide"),
    ("sort", "sorted", "shuffle"),
    ("reverse", "reversed", "forward"),
    ("count", "total", "skip"),
    ("find", "search", "ignore"),
    ("read", "load", "write"),
    ("open", "start", "close"),
]


def _get_action_tokens(model: Any) -> list[tuple[str, int, str, int]]:
    """Get (func_name, target_tok, wrong_name, wrong_tok) tuples."""
    valid = []
    for func, action, wrong_action in _FUNCTIONS:
        try:
            target = int(model.to_single_token(f" {action}"))
            distractor = int(model.to_single_token(f" {wrong_action}"))
            valid.append((func, target, wrong_action, distractor))
        except Exception:
            continue
    return valid


def _prompts(func_name: str, wrong_func: str, variant: str) -> tuple[str, str]:
    if variant == "detailed":
        clean = f'def {func_name}(x, y):\n    """This function will'
        corrupt = f'def {wrong_func}(x, y):\n    """This function will'
    elif variant == "brief":
        clean = f"# {func_name}: this will"
        corrupt = f"# {wrong_func}: this will"
    elif variant == "returns":
        clean = f"def {func_name}(data):\n    # Returns the"
        corrupt = f"def {wrong_func}(data):\n    # Returns the"
    else:
        clean = f'def {func_name}(data):\n    """'
        corrupt = f'def {wrong_func}(data):\n    """'
    return clean, corrupt


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    action_tokens = _get_action_tokens(model)
    if len(action_tokens) < 2:
        raise ValueError("Not enough single-token function actions for docstring task")

    rng = random.Random(seed)
    rows: list[TaskExample] = []

    for _ in range(n):
        func_name, target_tok, wrong_func, distractor_tok = rng.choice(action_tokens)
        clean, corrupt = _prompts(func_name, wrong_func, prompt_variant)

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


class DocstringTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
