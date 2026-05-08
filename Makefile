PYTHON ?= python

# Determinism: hash seed pinned for byte-identical Holm/BH tie-break ordering
# (audit-final A8/C5).
export PYTHONHASHSEED := 0

# Determinism: SOURCE_DATE_EPOCH pinned so any artifact writer routed through
# main._bundle_analysis.generated_at_utc() emits a fixed UTC timestamp
# (final_opus_audit.md §1.12). 1700000000 = 2023-11-14T22:13:20Z, the
# canonical "neutral" epoch from the Reproducible Builds convention. Override
# on the command line (``make SOURCE_DATE_EPOCH=...``) when intentionally
# regenerating canonical artifacts that should embed the live wall-clock.
export SOURCE_DATE_EPOCH ?= 1700000000

.PHONY: test test-evaluator test-runner audit docs community-summary breadth findings runtime stress rerun figures quality-dashboard download-models external-packet repro-check

test:
	$(PYTHON) -m pytest packages/evaluator/tests packages/runner/tests -q

test-evaluator:
	$(PYTHON) -m pytest packages/evaluator/tests -q

test-runner:
	$(PYTHON) -m pytest packages/runner/tests -q

# critical_audit.md §3.3 (2026-05-05): single-command reproducibility check.
# Re-runs the 43-command reproducibility audit in --check mode (no artifact
# rewrites) and exits non-zero if any canonical artifact has drifted from
# its committed bytes. Intended for CI and pre-release sanity checks.
# (final_critical_gpt_audit.md F2, 2026-05-06: previously omitted --check,
# silently rewriting artifacts and masking drift.)
repro-check:
	$(PYTHON) main/reproducibility_audit.py --check

breadth:
	$(PYTHON) main/summarize_benchmark_breadth.py

findings:
	$(PYTHON) main/field_level_findings.py

runtime:
	$(PYTHON) main/runtime_cost_report.py --reruns 3

community-summary:
	$(PYTHON) main/community_value_summary.py

stress:
	$(PYTHON) main/stress_test_ablation.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small --per-family 10
	$(PYTHON) main/stress_test_agnostic.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small --count 40
	$(PYTHON) main/stress_test_red_team.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small --adaptive-attempts 10 --near-miss-count 5

audit:
	$(PYTHON) main/reproducibility_audit.py

figures:
	$(PYTHON) main/generate_publication_figures.py

quality-dashboard:
	$(PYTHON) main/quality_progress_dashboard.py --run-health-checks

docs:
	$(PYTHON) scripts/generate_docs_from_json.py

rerun:
	$(PYTHON) main/rerun.py --bundle-dir main/output/real_multi_task/ioi_v0_gpt2-small --reruns 3

# ---------------------------------------------------------------------------
# Vendored-artifact regeneration (audit-final §1.14)
# ---------------------------------------------------------------------------

# Fetch model weights from HuggingFace into model_cache/ rather than committing.
# Requires HUGGINGFACE_HUB_TOKEN if a model is gated.
download-models:
	$(PYTHON) -c "from transformers import AutoModelForCausalLM; \
		[AutoModelForCausalLM.from_pretrained(m, cache_dir='model_cache') \
		for m in ('gpt2','gpt2-medium','EleutherAI/pythia-70m')]"

# Build the external-author submission packet (zip) from the source tree
# under holdout/external_partner_packet/. The zip itself is gitignored so
# that the released artifact is always derived from the current source.
external-packet:
	cd holdout && $(PYTHON) tools/build_external_partner_packet.py
