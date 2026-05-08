# How To Add A New Task

## 1) Define task objective

Specify what behavior the task probes and why it is meaningful for mechanistic claim validation.

## 2) Implement runner task module

Add task implementation under `packages/runner/src/automechinterp_runner/tasks/`.

Ensure task registration and command-line discoverability are updated.

## 3) Define slice/control requirements

Document required confirmatory and exploratory slices plus task-specific controls.

## 4) Add tests

Cover:

- task registry loading
- deterministic behavior for fixed seeds
- valid output schema for generated cells

## 5) Produce reference bundle

Create at least one runnable bundle for smoke validation and documentation.

## 6) Update docs

Update concepts, submission checklist, and tutorials if task semantics introduce new requirements.
