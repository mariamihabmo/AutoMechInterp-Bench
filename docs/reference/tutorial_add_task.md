# Adding a New Task

This tutorial walks you through implementing a new task for the AutoMechInterp pipeline.

## Overview

Every task module must implement the **TaskModule** interface, providing:
1. `sample_examples(model, n, seed, prompt_variant) → list[TaskExample]`
2. `metric(logits, target_token, distractor_token) → float`
3. `PROMPT_VARIANTS: list[str]` — at least 3 variants

## Step-by-Step

### 1. Create the task file

Create `packages/runner/src/automechinterp_runner/tasks/your_task.py`:

```python
from __future__ import annotations
import random
from typing import Any
from . import TaskExample

PROMPT_VARIANTS = ["base", "paraphrase", "structured"]

def sample_examples(model: Any, n: int, seed: int, prompt_variant: str) -> list[TaskExample]:
    """Generate n clean/corrupt prompt pairs with target/distractor tokens."""
    rng = random.Random(seed)
    rows = []
    for _ in range(n):
        # Your logic to create clean and corrupt prompts
        rows.append(TaskExample(
            clean_prompt="...",
            corrupt_prompt="...",
            target_token=target_tok,    # int token ID
            distractor_token=distract_tok,  # int token ID
        ))
    return rows

def metric(logits: Any, target_token: int, distractor_token: int) -> float:
    """Logit difference metric."""
    value = logits[0, -1, target_token] - logits[0, -1, distractor_token]
    if hasattr(value, "detach"):
        value = value.detach()
    return float(value)

class YourTaskModule:
    PROMPT_VARIANTS = PROMPT_VARIANTS
    sample_examples = staticmethod(sample_examples)
    metric = staticmethod(metric)
```

### 2. Register in the task registry

Add to `tasks/__init__.py`:

```python
elif task_id == "your_task_v0":
    from .your_task import YourTaskModule
    mod = YourTaskModule()
    _TASK_MODULES[task_id] = mod
    return mod
```

### 3. Add to constants

Add to `TASK_REGISTRY` in `packages/evaluator/src/automechinterp_evaluator/constants.py`:

```python
"your_task_v0": {
    "name": "Your Task Name",
    "domain": "your_domain",
    "complexity": "medium",
    "module": "automechinterp_runner.tasks.your_task",
},
```

### 4. Create a protocol

```yaml
unit_of_work:
  task_id: your_task_v0
  model_id: gpt2-small
  ...
```

### 5. Key principles

- **Tokenization**: Use `model.to_single_token()` to ensure target/distractor are single tokens
- **Determinism**: Use `random.Random(seed)` for reproducibility
- **3+ variants**: Each variant should change the prompt structure, not just wording
- **Clean/corrupt pairing**: The corrupt prompt should only differ in the key aspect being tested
