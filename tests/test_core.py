from hla_analyst.core import BatchAnalyzer
from hla_analyst.models import ImputationStatus


def test_analyze_success(sample_batch_dir):
    analyzer = BatchAnalyzer(sample_batch_dir)
    metrics = analyzer.analyze()

    assert metrics.status == ImputationStatus.SUCCESS
    assert len(metrics.input_files) > 0
    assert len(metrics.output_files) == 3
    assert metrics.command is not None


def test_analyze_failure(failed_batch_dir):
    analyzer = BatchAnalyzer(failed_batch_dir)
    metrics = analyzer.analyze()

    assert metrics.status == ImputationStatus.FAILURE
    assert len(metrics.errors) > 0


def test_validate_inputs_missing_cols(tmp_path):
    batch_dir = tmp_path / "bad_input"
    batch_dir.mkdir()
    (batch_dir / "test.QC.bgl").write_text("col1 col2")  # Too few columns

    analyzer = BatchAnalyzer(batch_dir)
    metrics = analyzer.analyze()

    assert any("too few columns" in e for e in metrics.errors)
