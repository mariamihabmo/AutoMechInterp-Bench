# Compared To MIB

[MIB (arXiv:2504.13151)](https://arxiv.org/abs/2504.13151) and AutoMechInterp both raise rigor in mechanistic interpretability, but they answer different research questions.

## High-level framing

- **MIB** emphasizes benchmarking interpretability methods over curated tasks/tracks.
- **AutoMechInterp** emphasizes verifying whether individual submitted claims meet a deterministic evidence contract.

## Side-by-side comparison

| Dimension | MIB | AutoMechInterp |
|---|---|---|
| Main research question | How well do methods perform on benchmark tasks? | Does this claim satisfy evidence requirements under a frozen policy? |
| Typical unit | method-task-track outcome | claim bundle |
| Output style | comparative benchmark scores | gate outcomes + evidence tier + remediation |
| Primary consumer | method developers and benchmark analysts | claim authors, reviewers, reproducibility auditors |
| Ground-truth dependence | generally higher (task curation structure) | lower direct dependence; relies on evidentiary contract |
| Deterministic rerun semantics | benchmark-dependent | explicit, first-class |

## What each tool reveals

### What MIB is very good at

- identifying which methods perform better in controlled benchmark settings
- revealing method strengths/weaknesses across benchmark tracks
- supporting comparative claims about interpretability techniques

### What AutoMechInterp is very good at

- converting concrete claim evidence into deterministic acceptance outcomes
- identifying specific failure families (controls, robustness, statistics)
- supporting external submission workflows with replayable decisions

## Why both are needed

Method quality and claim quality are related but not equivalent.

A method can rank highly in method benchmarks while a particular claim from that method still fails robustness or controls in a verifier contract.

Conversely, a claim may pass a strict verifier even if its discovery method is not top-ranked overall.

## Recommended combined workflow

1. Run method development and method benchmarking (MIB-like objective).
2. Export concrete claim candidates with intervention evidence.
3. Package claims into AutoMechInterp bundle format.
4. Run deterministic stage-gate verification.
5. Publish only claims whose evidence satisfies the verifier contract.

## Decision map

| You need to answer... | Better starting point |
|---|---|
| “Which interpretability method is strongest on benchmark tasks?” | MIB |
| “Is this exact claim evidentially robust enough to publish?” | AutoMechInterp |
| “Which gate families are blocking acceptance most often?” | AutoMechInterp |
| “How do methods rank across benchmark tracks?” | MIB |

## Practical takeaway

The two systems are complementary. MIB is primarily comparative-method benchmarking; AutoMechInterp is claim-level evidentiary verification.

Using both gives stronger end-to-end scientific discipline than using either alone.
