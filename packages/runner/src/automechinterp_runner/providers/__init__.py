"""Hypothesis provider interface — multi-lane discovery architecture.

Every discovery lane (circuit sweeps, OpenAI autointerp, SAE feature
selectors, Petri behavioral auditing, etc.) implements the same
HypothesisProvider interface, emitting hypothesis.jsonl-compatible dicts
that feed into the Stage-2 runner and Stage-1 evaluator unchanged.

Core principle: one verifier, many discovery lanes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HypothesisProvider(ABC):
    """Abstract base for all hypothesis discovery lanes.

    Every provider must implement ``propose()``, which takes a frozen
    protocol and a claim budget and returns a list of hypothesis dicts
    that conform to the ``hypothesis.jsonl`` schema defined in
    ``automechinterp_evaluator.constants``.

    Providers should set ``name`` and ``version`` as class attributes
    so the evaluator can track which lane generated each claim.
    """

    name: str = "base_provider"
    version: str = "0.0.0"

    @abstractmethod
    def propose(
        self,
        protocol: dict[str, Any],
        budget: int,
    ) -> list[dict[str, Any]]:
        """Generate hypothesis dicts from exploratory analysis.

        Parameters
        ----------
        protocol : dict
            The frozen protocol.yaml contents.
        budget : int
            Maximum number of hypotheses to emit.

        Returns
        -------
        list[dict]
            Hypothesis dicts compatible with ``hypothesis.jsonl`` schema.
            Each dict MUST contain all fields from
            ``REQUIRED_HYPOTHESIS_FIELDS`` in constants.py, plus at
            minimum ``provider_id`` and ``discovery_lane`` in the
            optional metadata fields.
        """
        ...

    def tag_hypotheses(
        self,
        hypotheses: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Stamp provider provenance onto each hypothesis."""
        for h in hypotheses:
            h.setdefault("provider_id", self.name)
            h.setdefault("provider_version", self.version)
            h.setdefault("discovery_lane", self.name)
        return hypotheses


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

_PROVIDER_REGISTRY: dict[str, type[HypothesisProvider]] = {}


def register_provider(cls: type[HypothesisProvider]) -> type[HypothesisProvider]:
    """Decorator to register a provider class by its ``name`` attribute."""
    _PROVIDER_REGISTRY[cls.name] = cls
    return cls


def get_provider(name: str) -> type[HypothesisProvider]:
    """Look up a registered provider class by name."""
    if name not in _PROVIDER_REGISTRY:
        available = ", ".join(sorted(_PROVIDER_REGISTRY)) or "(none)"
        raise KeyError(
            f"Unknown provider '{name}'. Available: {available}"
        )
    return _PROVIDER_REGISTRY[name]


def list_providers() -> list[str]:
    """Return sorted list of registered provider names."""
    return sorted(_PROVIDER_REGISTRY)
