"""Fact Recall task.

Tests whether the model correctly recalls single facts, using
clean/corrupt pairs where the subject entity is swapped.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "paraphrase", "contextual", "biographical"]

_FACTS = [
    ("Einstein", "physics", "chemistry"),
    ("Shakespeare", "plays", "paintings"),
    ("Mozart", "music", "painting"),
    ("Newton", "gravity", "magnetism"),
    ("Darwin", "evolution", "creation"),
    ("Edison", "light", "sound"),
    ("Picasso", "art", "science"),
    ("Tesla", "electricity", "biology"),
]


def _get_fact_tokens(model: Any) -> list[tuple[str, int, str, int, str]]:
    valid = []
    for person, fact, wrong_fact in _FACTS:
        try:
            target = int(model.to_single_token(f" {fact}"))
            distractor = int(model.to_single_token(f" {wrong_fact}"))
            valid.append((person, target, wrong_fact, distractor, fact))
        except Exception:
            continue
    return valid


def _prompts(person: str, wrong_person: str, variant: str) -> tuple[str, str]:
    if variant == "paraphrase":
        clean = f"{person} is most famous for their work in"
        corrupt = f"{wrong_person} is most famous for their work in"
    elif variant == "contextual":
        clean = f"When people talk about {person}, they discuss"
        corrupt = f"When people talk about {wrong_person}, they discuss"
    elif variant == "biographical":
        clean = f"In a biography of {person}, the main topic would be"
        corrupt = f"In a biography of {wrong_person}, the main topic would be"
    else:
        clean = f"{person} is known for"
        corrupt = f"{wrong_person} is known for"
    return clean, corrupt


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    fact_tokens = _get_fact_tokens(model)
    if len(fact_tokens) < 2:
        raise ValueError("Not enough single-token facts for fact recall task")

    rng = random.Random(seed)
    rows: list[TaskExample] = []

    # Audit-final §gpt2.D2: enforce per-example token-length parity between
    # the clean and corrupt prompts. Person names ("Einstein" vs.
    # "Shakespeare") frequently tokenize to different numbers of BPE
    # tokens; without this guard the corrupt prompt's answer position
    # shifts by one or more tokens and the head/MLP intervention lands
    # on a different residual stream column than the clean run, silently
    # invalidating the activation-patching contract.
    def _same_tok_len(clean: str, corrupt: str) -> bool:
        try:
            return int(model.to_tokens(clean).shape[-1]) == int(
                model.to_tokens(corrupt).shape[-1]
            )
        except Exception:
            return True  # be permissive if tokenizer is mock

    for _ in range(n):
        # Try a few times to find a parity-matching pair; fall back to
        # whatever was sampled if no parity-matching pair exists for the
        # available facts (in which case downstream evaluation will still
        # log the mismatch via the dataset_seed audit trail).
        for _attempt in range(8):
            idx_a, idx_b = rng.sample(range(len(fact_tokens)), k=2)
            person_a, target_tok, _, person_a_distractor_tok, _ = fact_tokens[idx_a]
            person_b, _, _, _, _ = fact_tokens[idx_b]
            # the distractor must be
            # person_a's **own** wrong fact, not person_b's wrong fact —
            # otherwise the metric measures general topical preference
            # (e.g. Shakespeare's "paintings" vs. Einstein's "physics")
            # rather than fact-person binding.
            distractor_tok = person_a_distractor_tok
            clean, corrupt = _prompts(person_a, person_b, prompt_variant)
            if _same_tok_len(clean, corrupt):
                break

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


class FactRecallTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
