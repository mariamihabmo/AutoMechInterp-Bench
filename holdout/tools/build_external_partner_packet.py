"""Assemble a ready-to-send packet for recruiting an external blinded author.

This does not create external evidence by itself. It packages the exact files an
external partner needs so the remaining blocker is reduced to human recruitment,
not repo assembly friction.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from .package_holdout_submission import current_contract_pin

ROOT = Path(__file__).resolve().parents[2]
PACKET_DIR = ROOT / "holdout" / "external_partner_packet"
OUT_ZIP = ROOT / "holdout" / "external_partner_packet.zip"
REPRO = ROOT / "main" / "output" / "repro"
OUT_MD = REPRO / "external_partner_packet.md"
OUT_JSON = REPRO / "external_partner_packet.json"


def main() -> int:
    # hard-fail with a clear list of
    # missing source paths before any copying, so a partial packet cannot be
    # silently shipped. Without this guard, a refactor that moves any
    # ``docs/reference/*.md`` file would produce a packet missing the
    # corresponding instruction page; external partners would receive an
    # incomplete onboarding kit and the failure would only surface when an
    # author asked where the missing instructions were.
    expected_sources = [
        ROOT / "holdout" / "EXTERNAL_AUTHOR_QUICKSTART.md",
        ROOT / "holdout" / "CUSTODIAN_RUNBOOK.md",
        ROOT / "holdout" / "README.md",
        ROOT / "holdout" / "attestation_schema.json",
        ROOT / "docs" / "reference" / "claim_bundle_spec_v1.md",
        ROOT / "docs" / "reference" / "community_submission_guide.md",
        ROOT / "docs" / "reference" / "external_bundle_invitation.md",
        ROOT / "docs" / "reference" / "holdout_stress_governance_plan.md",
        ROOT / "docs" / "reference" / "independent_agnostic_negative_spec.md",
        ROOT / "docs" / "reference" / "independent_researcher_external_evidence_playbook.md",
        ROOT / "methodology" / "blinded_holdout_protocol.md",
        ROOT / "methodology" / "independent_agnostic_stress_protocol.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in expected_sources if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "build_external_partner_packet: missing expected source files "
            f"({len(missing)}): {missing}. Refusing to build a partial packet."
        )
    if PACKET_DIR.exists():
        shutil.rmtree(PACKET_DIR)
    PACKET_DIR.mkdir(parents=True, exist_ok=True)

    files_to_copy = {
        ROOT / "holdout" / "EXTERNAL_AUTHOR_QUICKSTART.md": PACKET_DIR / "EXTERNAL_AUTHOR_QUICKSTART.md",
        ROOT / "holdout" / "CUSTODIAN_RUNBOOK.md": PACKET_DIR / "CUSTODIAN_RUNBOOK.md",
        ROOT / "holdout" / "README.md": PACKET_DIR / "HOLDOUT_README.md",
        ROOT / "holdout" / "attestation_schema.json": PACKET_DIR / "attestation_schema.json",
        ROOT / "docs" / "reference" / "claim_bundle_spec_v1.md": PACKET_DIR / "claim_bundle_spec_v1.md",
        ROOT / "docs" / "reference" / "community_submission_guide.md": PACKET_DIR / "community_submission_guide.md",
        ROOT / "docs" / "reference" / "external_bundle_invitation.md": PACKET_DIR / "external_bundle_invitation.md",
        ROOT / "docs" / "reference" / "holdout_stress_governance_plan.md": PACKET_DIR / "holdout_stress_governance_plan.md",
        ROOT / "docs" / "reference" / "independent_agnostic_negative_spec.md": PACKET_DIR / "independent_agnostic_negative_spec.md",
        ROOT / "docs" / "reference" / "independent_researcher_external_evidence_playbook.md": PACKET_DIR / "independent_researcher_external_evidence_playbook.md",
        ROOT / "methodology" / "blinded_holdout_protocol.md": PACKET_DIR / "blinded_holdout_protocol.md",
        ROOT / "methodology" / "independent_agnostic_stress_protocol.md": PACKET_DIR / "independent_agnostic_stress_protocol.md",
    }
    for src, dst in files_to_copy.items():
        shutil.copy2(src, dst)

    contract_pin = current_contract_pin()
    (PACKET_DIR / "contract_pin.json").write_text(json.dumps(contract_pin, indent=2, sort_keys=True) + "\n")

    template = {
        "submission_id": "<CUSTODIAN_OPAQUE_ID>",
        "submission_kind": "external_blinded",
        "submitted_at_utc": "<AUTO_FILLED_BY_PACKAGER_OR_CUSTODIAN>",
        "author_institution": "<INSTITUTION>",
        "contract_pin": contract_pin,
        "attestation_text": "BLINDED EXTERNAL AUTHORING. This bundle was authored against the public AutoMechInterp contract specification without consulting any AutoMechInterp maintainer about acceptance heuristics, accepted-claim examples, or unpublished thresholds during authoring, and it was not pre-evaluated against the pinned evaluator before sealed submission to the Custodian.",
        "attestation_signature": "<CUSTODIAN_SIGNATURE>",
    }
    (PACKET_DIR / "attestation_template.json").write_text(json.dumps(template, indent=2, sort_keys=True) + "\n")

    commands = f'''# Package the sealed submission\npython -m holdout.tools.package_holdout_submission \\\n  --bundle-dir /path/to/your/bundle \\\n  --submission-dir holdout/submissions/<SUBMISSION_ID> \\\n  --submission-id <SUBMISSION_ID> \\\n  --submission-kind external_blinded \\\n  --author-institution "Your Institution" \\\n  --attestation-signature "<custodian-scheme-signature>"\n\n# Run author-side preflight\npython -m holdout.tools.preflight_submission \\\n  --submission-dir holdout/submissions/<SUBMISSION_ID>\n\n# Current contract pin\n# evaluator_version={contract_pin['evaluator_version']}\n# constants_sha256={contract_pin['constants_sha256']}\n'''
    (PACKET_DIR / "commands.sh").write_text(commands)

    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(PACKET_DIR.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(path.relative_to(PACKET_DIR.parent)))

    REPRO.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "holdout/tools/build_external_partner_packet.py",
        "packet_dir": str(PACKET_DIR.relative_to(ROOT)),
        "packet_zip": str(OUT_ZIP.relative_to(ROOT)),
        "contract_pin": contract_pin,
        "files": sorted(str(p.relative_to(PACKET_DIR.parent)) for p in PACKET_DIR.rglob("*") if p.is_file()),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = [
        "# External Partner Packet",
        "",
        "This packet is the repo's ready-to-send recruitment bundle for a genuine external blinded author.",
        "It does not count as external evidence by itself; it removes packaging friction so the blocker is reduced to recruitment and custody.",
        "",
        f"- Packet directory: `{payload['packet_dir']}`",
        f"- Packet zip: `{payload['packet_zip']}`",
        f"- Evaluator pin: `{contract_pin['evaluator_version']}`",
        f"- Constants SHA-256: `{contract_pin['constants_sha256']}`",
        "",
        "## Included files",
        "",
    ]
    for name in payload["files"]:
        lines.append(f"- `{name}`")
    OUT_MD.write_text("\n".join(lines).rstrip() + "\n")
    print(str(OUT_JSON))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
