import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "evaluator" / "src"))
from automechinterp_evaluator.evaluator import evaluate_bundle

bundle_dir = Path("main/output/real_multi_task/ioi_v0_gpt2-small")
res = evaluate_bundle(bundle_dir)

print("Cross-Model Transfer Effects:")
for report in res["claim_reports"]:
    if report["passed"]:
        hid = report["hypothesis_id"]
        transfer_eff = report["metrics"].get("cross_model_transfer_effect")
        print(f"  {hid}: {transfer_eff}")

print("\nSensitivity Analysis (Passes Cross-Model Gate?):")
thresholds = [0.01, 0.02, 0.05]
for t in thresholds:
    print(f"\nThreshold: {t}")
    for report in res["claim_reports"]:
        if report["passed"]:
            hid = report["hypothesis_id"]
            transfer_eff = report["metrics"].get("cross_model_transfer_effect")
            if transfer_eff is None:
                continue
            same_dir = report["metrics"].get("cross_model_same_direction")
            above_floor = abs(transfer_eff) >= t
            passes = same_dir and above_floor
            print(f"  {hid}: {passes} (abs > {t}: {above_floor})")
