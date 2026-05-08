"""Task registry for Stage-2 runner.

V7: Provides a unified interface for all task modules and a registry
that maps task_id to the appropriate module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class TaskExample:
    """Standard example format that all task modules must produce."""
    clean_prompt: str
    corrupt_prompt: str
    target_token: int
    distractor_token: int


class TaskModule(Protocol):
    """Protocol that all task modules must satisfy."""

    def sample_examples(
        self, model: Any, n: int, seed: int, prompt_variant: str,
    ) -> list[TaskExample]: ...

    def metric(
        self, logits: Any, target_token: int, distractor_token: int,
    ) -> float: ...

    PROMPT_VARIANTS: list[str]


# Task registry: maps task_id to lazy-loadable module
_TASK_MODULES: dict[str, Any] = {}


def register_task(task_id: str, module: Any) -> None:
    """Register a task module."""
    _TASK_MODULES[task_id] = module


def get_task_module(task_id: str) -> Any:
    """Get task module by task_id, with lazy loading."""
    if task_id in _TASK_MODULES:
        return _TASK_MODULES[task_id]

    # Lazy-load built-in task modules
    if task_id == "ioi_v0":
        from .ioi import IOITaskModule
        mod = IOITaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "greater_than_v0":
        from .greater_than import GreaterThanTaskModule
        mod = GreaterThanTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "gendered_pronoun_v0":
        from .gendered_pronoun import GenderedPronounTaskModule
        mod = GenderedPronounTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "country_capital_v0":
        from .country_capital import CountryCapitalTaskModule
        mod = CountryCapitalTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "sentiment_v0":
        from .sentiment import SentimentTaskModule
        mod = SentimentTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "docstring_v0":
        from .docstring import DocstringTaskModule
        mod = DocstringTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "fact_recall_v0":
        from .fact_recall import FactRecallTaskModule
        mod = FactRecallTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod
    elif task_id == "arithmetic_v0":
        from .arithmetic import ArithmeticTaskModule
        mod = ArithmeticTaskModule()
        _TASK_MODULES[task_id] = mod
        return mod

    raise KeyError(f"Unknown task_id: {task_id}. Available: {list_tasks()}")


def list_tasks() -> list[str]:
    """List all available task IDs."""
    builtin = [
        "ioi_v0", "greater_than_v0", "gendered_pronoun_v0",
        "country_capital_v0", "sentiment_v0", "docstring_v0",
        "fact_recall_v0", "arithmetic_v0",
    ]
    return sorted(set(builtin) | set(_TASK_MODULES.keys()))
