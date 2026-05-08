"""Country-Capital factual recall task.

Tests whether the model correctly completes "The capital of [country] is"
with the right capital name, using clean/corrupt pairs with different countries.
"""

from __future__ import annotations

import random
from typing import Any

from . import TaskExample


PROMPT_VARIANTS = ["base", "paraphrase", "fill_blank", "quiz"]

# Country/capital pairs. **All capitals listed here must single-tokenize in
# every model used for cross-model claims** (GPT-2 family, Pythia family,
# Llama family). Multi-token capitals such as "New Delhi" or "Brasilia"
# previously caused the source and transfer models to silently evaluate on
# different example subsets even with identical ``dataset_seed``, confounding
# every cross-model country-capital claim. The list below excludes such
# entries; if a future model tokenizes any of these as multiple tokens,
# :func:`_get_capital_tokens` will reject the example and raise rather than
# silently dropping it .
_COUNTRY_CAPITAL_PAIRS = [
    ("France", "Paris"),
    ("Germany", "Berlin"),
    ("Japan", "Tokyo"),
    ("Italy", "Rome"),
    ("Spain", "Madrid"),
    ("China", "Beijing"),
    ("Russia", "Moscow"),
    ("Canada", "Ottawa"),
]


def _get_capital_tokens(model: Any) -> dict[str, tuple[str, int]]:
    """Return single-token IDs for capitals.

    Raises
    ------
    ValueError
        If any pair fails to single-tokenize in the current model. Failing
        loudly is required for cross-model parity: silently dropping pairs
        causes source and transfer models to evaluate different example sets.
    """
    valid: dict[str, tuple[str, int]] = {}
    failed: list[str] = []
    for country, capital in _COUNTRY_CAPITAL_PAIRS:
        try:
            tok = int(model.to_single_token(f" {capital}"))
            valid[country] = (capital, tok)
        except Exception:
            failed.append(capital)
    if failed:
        raise ValueError(
            "country_capital: capitals failed to single-tokenize "
            f"({', '.join(failed)}); update _COUNTRY_CAPITAL_PAIRS to a set "
            "that single-tokenizes across every supported model so cross-model "
            "claims compare matched example sets."
        )
    return valid


def _prompts(country_a: str, country_b: str, variant: str) -> tuple[str, str]:
    if variant == "paraphrase":
        clean = f"What is the capital city of {country_a}? It is"
        corrupt = f"What is the capital city of {country_b}? It is"
    elif variant == "fill_blank":
        clean = f"{country_a}'s capital city is called"
        corrupt = f"{country_b}'s capital city is called"
    elif variant == "quiz":
        clean = f"Quiz: Name the capital of {country_a}. Answer:"
        corrupt = f"Quiz: Name the capital of {country_b}. Answer:"
    else:
        clean = f"The capital of {country_a} is"
        corrupt = f"The capital of {country_b} is"
    return clean, corrupt


def _assert_token_parity(model: Any, clean: str, corrupt: str) -> None:
    """Raise if clean/corrupt tokenize to different sequence lengths.

    Without parity, ``target_position=-1`` points at different syntactic
    tokens in the two prompts and the metric is undefined.
    """
    try:
        clean_len = int(model.to_tokens(clean).shape[-1])
        corrupt_len = int(model.to_tokens(corrupt).shape[-1])
    except Exception:
        return
    if clean_len != corrupt_len:
        raise ValueError(
            "country_capital: clean/corrupt token-length mismatch "
            f"(clean={clean_len}, corrupt={corrupt_len}) for prompts "
            f"{clean!r} vs {corrupt!r}"
        )


def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    if n <= 0:
        raise ValueError("n must be positive")

    capital_tokens = _get_capital_tokens(model)
    # Deterministic ordering so equal seeds yield identical example sets
    # across processes regardless of dict-iteration order.
    countries = sorted(capital_tokens.keys())

    if len(countries) < 2:
        raise ValueError("Not enough single-token capitals for country-capital task")

    rng = random.Random(seed)
    rows: list[TaskExample] = []

    for _ in range(n):
        country_a, country_b = rng.sample(countries, k=2)
        clean, corrupt = _prompts(country_a, country_b, prompt_variant)
        _assert_token_parity(model, clean, corrupt)
        _, target_tok = capital_tokens[country_a]
        _, distractor_tok = capital_tokens[country_b]

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


class CountryCapitalTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
