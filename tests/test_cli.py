from pathlib import Path

from typer.testing import CliRunner

from hla_analyst.cli import app

runner = CliRunner()
DATA = Path(__file__).resolve().parent.parent / "data"


def test_cli_analyze(sample_batch_dir: Path) -> None:
    result = runner.invoke(app, ["analyze", str(sample_batch_dir)])
    assert result.exit_code == 0
    assert "Status: SUCCESS" in result.stdout
    assert "Required outputs found: 4/4" in result.stdout


def test_cli_analyze_json(sample_batch_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    args = ["analyze", str(sample_batch_dir), "--format", "json", "--output", str(out)]
    result = runner.invoke(app, args)
    assert result.exit_code == 0
    assert '"status": "SUCCESS"' in out.read_text()


def test_cli_text_report_is_written(sample_batch_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "report.txt"
    runner.invoke(app, ["analyze", str(sample_batch_dir), "-o", str(out)])
    assert out.read_text().startswith("Batch: batch_001\nStatus: SUCCESS")


def test_html_report_escapes_log_content(
    failed_batch_dir: Path, tmp_path: Path
) -> None:
    (failed_batch_dir / "run.bgl.log").write_text("error <script>alert(1)</script>\n")
    out = tmp_path / "report.html"
    runner.invoke(app, ["analyze", str(failed_batch_dir), "-f", "html", "-o", str(out)])
    html = out.read_text()
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_cli_validate_success(sample_batch_dir: Path) -> None:
    assert runner.invoke(app, ["validate", str(sample_batch_dir)]).exit_code == 0


def test_cli_validate_failure(failed_batch_dir: Path) -> None:
    assert runner.invoke(app, ["validate", str(failed_batch_dir)]).exit_code == 1


def test_cli_validate_missing_dir(tmp_path: Path) -> None:
    assert runner.invoke(app, ["validate", str(tmp_path / "nope")]).exit_code == 2


def test_example_data_compare() -> None:
    result = runner.invoke(
        app,
        [
            "analyze",
            str(DATA / "failed_batch"),
            "--compare",
            str(DATA / "sample_batch"),
        ],
    )
    assert result.exit_code == 0
    assert "Status: FAILURE" in result.stdout
    assert "set WIN: this=500 reference=1000" in result.stdout
    assert "missing here but present in reference: *.dosage" in result.stdout
