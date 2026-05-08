from pathlib import Path

from automechinterp_evaluator.cli import build_parser


def test_cli_report_generation(bundle_dir: Path, tmp_path: Path) -> None:
    parser = build_parser()
    out = tmp_path / "report.md"
    args = parser.parse_args(["report", "--bundle", str(bundle_dir), "--output", str(out)])
    rc = args.func(args)
    assert rc == 0
    text = out.read_text()
    assert "Stage-Gate Report" in text
    assert "h_ioi_name_movers" in text


def test_cli_init_template(tmp_path: Path) -> None:
    parser = build_parser()
    out_dir = tmp_path / "bundle"
    args = parser.parse_args(["init-template", "--output-dir", str(out_dir)])
    rc = args.func(args)
    assert rc == 0
    assert (out_dir / "protocol.yaml").exists()
    assert (out_dir / "hypothesis.jsonl").exists()
    assert (out_dir / "evaluation_result.json").exists()
