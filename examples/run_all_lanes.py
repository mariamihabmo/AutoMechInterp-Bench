#!/usr/bin/env python3
"""Test all 5 discovery lanes on the same task and compare their outputs.

Usage:
    python run_all_lanes.py
    python run_all_lanes.py --task ioi_v0 --model gpt2-small --budget 5

No GPU required — all lanes operate in mock/adapter mode.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "evaluator" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "runner" / "src"))

from automechinterp_runner.providers.circuits_sweep import CircuitSweepProvider
from automechinterp_runner.providers.openai_autointerp import OpenAIAutoInterpProvider
from automechinterp_runner.providers.efficient_neuron_explanations import EfficientNeuronExplanationsProvider
from automechinterp_runner.providers.sae_autointerp import SAEAutoInterpProvider
from automechinterp_runner.providers.petri_behavioral import PetriBehavioralProvider
from automechinterp_runner.providers import list_providers


# Sample neuron explanations (simulated)
MOCK_NEURON_EXPLANATIONS = [
    {"layer": 5, "neuron": 200, "explanation_text": "Fires on closing brackets and parentheses", "simulation_score": 0.85},
    {"layer": 7, "neuron": 412, "explanation_text": "Activates on proper names in object position", "simulation_score": 0.72},
    {"layer": 3, "neuron": 89, "explanation_text": "Responds to sentiment-bearing adjectives", "simulation_score": 0.68},
]

# Sample SAE features (simulated)
MOCK_SAE_FEATURES = [
    {"sae_id": "gpt2_resid_sae", "layer": 6, "feature_id": 1234, "description": "Detects indirect object position", "site": "resid_post"},
    {"sae_id": "gpt2_resid_sae", "layer": 8, "feature_id": 5678, "description": "Tracks name binding across clauses", "site": "resid_post"},
]

# Sample behavioral candidates (simulated)
MOCK_BEHAVIORAL_CANDIDATES = [
    {"component_type": "head", "layer": 9, "head": 6, "site": "z", "predicted_direction": "increase", "min_effect": 0.05},
    {"component_type": "mlp_neuron", "layer": 4, "neuron": 300, "predicted_direction": "increase", "min_effect": 0.02},
]


def main():
    parser = argparse.ArgumentParser(description="Compare all 5 discovery lanes")
    parser.add_argument("--task", default="ioi_v0")
    parser.add_argument("--model", default="gpt2-small")
    parser.add_argument("--budget", type=int, default=5)
    args = parser.parse_args()

    protocol = {
        "protocol_id": "lane_comparison_001",
        "frozen": True,
        "unit_of_work": {
            "task_id": args.task,
            "model_id": args.model,
            "metric_id": "logit_diff",
        },
    }

    print(f"\n{'='*70}")
    print(f"  Discovery Lane Comparison")
    print(f"  Task: {args.task}  |  Model: {args.model}  |  Budget: {args.budget}")
    print(f"{'='*70}\n")
    print(f"  Registered providers: {list_providers()}\n")

    lanes = [
        ("Lane A: Circuit Sweep", CircuitSweepProvider(mode="mock", top_k=args.budget)),
        ("Lane B1: OpenAI AutoInterp", OpenAIAutoInterpProvider(explanations=MOCK_NEURON_EXPLANATIONS)),
        ("Lane B2: Efficient AutoInterp", EfficientNeuronExplanationsProvider(explanations=MOCK_NEURON_EXPLANATIONS)),
        ("Lane B3: SAE AutoInterp", SAEAutoInterpProvider(features=MOCK_SAE_FEATURES)),
        ("Lane C: Petri Behavioral", PetriBehavioralProvider(candidates=MOCK_BEHAVIORAL_CANDIDATES)),
    ]

    all_hypotheses = []

    for lane_name, provider in lanes:
        hypotheses = provider.propose(protocol, budget=args.budget)
        all_hypotheses.extend(hypotheses)

        print(f"  {lane_name}: {provider.name} v{provider.version}")
        print(f"    Hypotheses generated: {len(hypotheses)}")

        for h in hypotheses:
            comp = h["candidate_components"][0]
            comp_type = comp["component_type"]
            claim_short = h["claim_text"][:80]
            print(f"    → [{comp_type}] {claim_short}...")

            # Verify schema completeness
            required = {"hypothesis_id", "protocol_id", "task_id", "model_id",
                       "metric_id", "claim_text", "candidate_components",
                       "predicted_effect_direction", "predicted_min_effect",
                       "predicted_specificity_ratio"}
            missing = required - set(h.keys())
            if missing:
                print(f"      ⚠️ MISSING REQUIRED FIELDS: {missing}")
            else:
                print(f"      ✅ Schema valid")

            # Check provenance
            if h.get("provider_id") and h.get("discovery_lane"):
                print(f"      Provenance: {h['provider_id']} / lane={h['discovery_lane']}")
            else:
                print(f"      ⚠️ Missing provenance metadata")

        print()

    # Summary
    print(f"{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Total hypotheses across all lanes: {len(all_hypotheses)}")

    comp_types = {}
    for h in all_hypotheses:
        ct = h["candidate_components"][0]["component_type"]
        comp_types[ct] = comp_types.get(ct, 0) + 1
    print(f"  Component type breakdown:")
    for ct, count in sorted(comp_types.items()):
        print(f"    {ct}: {count}")

    # Save combined output
    output_dir = ROOT / "examples" / "output" / "lane_comparison"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "all_hypotheses.json"
    output_path.write_text(json.dumps(all_hypotheses, indent=2))
    print(f"\n  All hypotheses saved to: {output_path}")


if __name__ == "__main__":
    main()
