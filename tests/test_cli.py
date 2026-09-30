from typer.testing import CliRunner

from hla_analyst.cli import app

runner = CliRunner()


def test_cli_analyze(sample_batch_dir):
    result = runner.invoke(app, ["analyze", str(sample_batch_dir)])
    assert result.exit_code == 0
    assert "Status: SUCCESS" in result.stdout


def test_cli_analyze_json(sample_batch_dir, tmp_path):
    output_file = tmp_path / "report.json"
    result = runner.invoke(
        app,
        [
            "analyze",
            str(sample_batch_dir),
            "--format",
            "json",
            "--output",
            str(output_file),
        ],
    )
    assert result.exit_code == 0
    assert output_file.exists()


def test_cli_validate_success(sample_batch_dir):
    result = runner.invoke(app, ["validate", str(sample_batch_dir)])
    assert result.exit_code == 0


def test_cli_validate_failure(failed_batch_dir):
    result = runner.invoke(app, ["validate", str(failed_batch_dir)])
    assert result.exit_code == 1
