# How To Add A New Gate

## 1) Define gate intent

Write a one-sentence risk statement: what failure mode the new gate prevents.

## 2) Specify inputs and outcomes

Define required inputs and how the gate emits `pass`, `fail`, or `not_evaluated`.

## 3) Implement evaluator logic

Add computation and diagnostics in evaluator code.

## 4) Integrate classifier logic

Ensure tier classification handles the gate consistently and without duplicated logic branches.

## 5) Add tests

At minimum cover:

- pass case
- fail case
- not-evaluated case
- interaction with tier outcomes

## 6) Document migration impact

If acceptance behavior changes, document it in governance/changelog and note backward-compatibility implications.
