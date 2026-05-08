"""Gendered Pronoun Resolution task.

Tests whether the model correctly resolves gendered pronouns (he/she)
to the appropriate antecedent by using clean/corrupt pairs where
genders are swapped.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


# the legacy ``base`` variant
# (``"{male} and {female} went to the park. Then he walked to"``) cannot
# distinguish gender-binding from positional first-named-entity bias because
# both clean and corrupt prompts contain exactly one male antecedent. It is
# rewritten here to a structure where the swap actually changes which
# antecedent is the dominant referent of "he", restoring a real
# gender-resolution signal.
PROMPT_VARIANTS = ["base", "paraphrase", "relative_clause", "possessive"]

_MALE_NAMES = ["John", "James", "David", "Robert", "Michael"]
_FEMALE_NAMES = ["Mary", "Sarah", "Lisa", "Karen", "Laura"]


def _single_token_ids(model: Any, names: list[str]) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for name in names:
        try:
            tok = int(model.to_single_token(f" {name}"))
            rows.append((name, tok))
        except Exception:
            continue
    return rows


def _get_pronoun_tokens(model: Any) -> tuple[int, int] | None:
    """Return (he_tok, she_tok) or ``None`` when either is multi-token.

    : returning ``None`` here lets ``sample_examples`` raise a
    structured error so the runner can convert the failure into a
    ``not_evaluated`` cell. The previous implementation raised mid-call
    while every other task in the package handles missing tokens by
    skipping the example.
    """
    try:
        he_tok = int(model.to_single_token(" he"))
        she_tok = int(model.to_single_token(" she"))
        return he_tok, she_tok
    except Exception:
        return None


def _prompts(male: str, female: str, variant: str) -> tuple[str, str, str]:
    """Returns (clean, corrupt, expected_pronoun_gender)."""
    if variant == "paraphrase":
        clean = f"After {male} talked to {female}, she went to see"
        corrupt = f"After {female} talked to {male}, she went to see"
        return clean, corrupt, "female"
    elif variant == "relative_clause":
        clean = f"{male}, who met {female} yesterday, said that he would return to"
        corrupt = f"{female}, who met {male} yesterday, said that he would return to"
        return clean, corrupt, "male"
    elif variant == "possessive":
        clean = f"{female} borrowed {male}'s car. Later, he asked for"
        corrupt = f"{male} borrowed {female}'s car. Later, he asked for"
        return clean, corrupt, "male"
    else:
        # Restructured ``base`` variant. The dependent clause's subject is
        # now the *second-mentioned* entity, so swapping male/female changes
        # which antecedent is the dominant referent for "he" — disentangling
        # the gender mechanism from positional bias.
        clean = f"After meeting {female}, {male} said that he"
        corrupt = f"After meeting {male}, {female} said that he"
        return clean, corrupt, "male"


def _assert_token_parity(model: Any, clean: str, corrupt: str) -> None:
    try:
        clean_len = int(model.to_tokens(clean).shape[-1])
        corrupt_len = int(model.to_tokens(corrupt).shape[-1])
    except Exception:
        return
    if clean_len != corrupt_len:
        raise ValueError(
            f"gendered_pronoun: clean/corrupt token-length mismatch "
            f"(clean={clean_len}, corrupt={corrupt_len})"
        )


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    pronoun_tokens = _get_pronoun_tokens(model)
    if pronoun_tokens is None:
        raise ValueError(
            "gendered_pronoun: tokenizer does not single-tokenize ' he' or "
            "' she'; this task is not evaluable on the current model."
        )
    he_tok, she_tok = pronoun_tokens
    male_ids = _single_token_ids(model, _MALE_NAMES)
    female_ids = _single_token_ids(model, _FEMALE_NAMES)

    if len(male_ids) < 2 or len(female_ids) < 2:
        raise ValueError("Not enough single-token names for gendered pronoun task")

    rng = random.Random(seed)
    rows: list[TaskExample] = []

    for _ in range(n):
        male_name, _ = rng.choice(male_ids)
        female_name, _ = rng.choice(female_ids)
        clean, corrupt, gender = _prompts(male_name, female_name, prompt_variant)
        _assert_token_parity(model, clean, corrupt)

        if gender == "male":
            target_tok, distractor_tok = he_tok, she_tok
        else:
            target_tok, distractor_tok = she_tok, he_tok

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


class GenderedPronounTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
