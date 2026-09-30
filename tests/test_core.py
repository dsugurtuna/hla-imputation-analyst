from pathlib import Path

import pytest

from hla_analyst.core import BatchAnalyzer
from hla_analyst.models import ImputationStatus


def test_analyze_success(sample_batch_dir: Path) -> None:
    metrics = BatchAnalyzer(sample_batch_dir).analyze()
    assert metrics.status == ImputationStatus.SUCCESS
    assert metrics.missing_artifacts == []
    assert len(metrics.output_files) == 4
    assert metrics.command is not None
    assert metrics.command.memory_setting == "2000m"


def test_analyze_failure(failed_batch_dir: Path) -> None:
    metrics = BatchAnalyzer(failed_batch_dir).analyze()
    assert metrics.status == ImputationStatus.FAILURE
    assert any("OutOfMemoryError" in e for e in metrics.errors)
    assert "*.dosage" in metrics.missing_artifacts


def test_intermediate_mhc_bgl_is_not_required(sample_batch_dir: Path) -> None:
    # SNP2HLA's default cleanup deletes <OUTPUT>.MHC.* files.
    (sample_batch_dir / "run.MHC.QC.bgl").unlink()
    assert BatchAnalyzer(sample_batch_dir).analyze().status == ImputationStatus.SUCCESS


def test_missing_output_is_a_failure(sample_batch_dir: Path) -> None:
    (sample_batch_dir / "run.bgl.r2").unlink()
    metrics = BatchAnalyzer(sample_batch_dir).analyze()
    assert metrics.status == ImputationStatus.FAILURE
    assert metrics.missing_artifacts == ["*.bgl.r2"]


@pytest.mark.parametrize(
    ("line", "is_error"),
    [
        ("finished with 0 errors", False),
        ("No errors found", False),
        ("ERROR: file not found", True),
        ("java.lang.OutOfMemoryError: Java heap space", True),
        ('Exception in thread "main"', True),
        ("terrorism", False),
    ],
)
def test_error_detection(tmp_path: Path, line: str, is_error: bool) -> None:
    run = tmp_path / "run"
    run.mkdir()
    (run / "x.log").write_text(line + "\n")
    errors = [e for e in BatchAnalyzer(run).analyze().errors if "x.log" in e]
    assert bool(errors) is is_error


def test_validate_inputs_missing_cols(tmp_path: Path) -> None:
    batch_dir = tmp_path / "bad_input"
    batch_dir.mkdir()
    (batch_dir / "test.QC.bgl").write_text("col1 col2")
    metrics = BatchAnalyzer(batch_dir).analyze()
    assert any("too few columns" in e for e in metrics.errors)


def test_validate_inputs_odd_genotype_columns(tmp_path: Path) -> None:
    batch_dir = tmp_path / "odd"
    batch_dir.mkdir()
    (batch_dir / "x.MHC.QC.bgl").write_text("I id S1 S1 S2\n")
    metrics = BatchAnalyzer(batch_dir).analyze()
    assert any("odd number of genotype columns" in e for e in metrics.errors)


def test_compare_reports_parameter_diffs_and_missing_outputs(
    failed_batch_dir: Path, reference_batch_dir: Path
) -> None:
    (failed_batch_dir / "SNP2HLA.csh").write_text("set MEM = 2000\nset WIN = 1000\n")
    result = BatchAnalyzer(failed_batch_dir).compare_with(reference_batch_dir)
    assert not result.identical_scripts
    assert result.parameter_diffs == {"WIN": {"this": "1000", "reference": "500"}}
    assert "*.dosage" in result.missing_vs_reference


def test_missing_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        BatchAnalyzer(tmp_path / "nope")
