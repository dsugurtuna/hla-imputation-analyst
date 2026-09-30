"""Fixtures: minimal SNP2HLA run directories built in a temporary folder."""

from pathlib import Path

import pytest


def _make_run(root: Path, *, window: int = 1000) -> Path:
    root.mkdir()
    (root / "SNP2HLA.csh").write_text(
        f"#!/bin/csh\nset MEM = 2000\nset WIN = {window}\n"
    )
    (root / "run.bgl.log").write_text(
        "java -Xmx2000m -jar beagle.jar unphased=run.MHC.QC.bgl out=run.IMPUTED\n"
        "finished with 0 errors\n"
    )
    (root / "run.MHC.QC.bgl").write_text("I id S1 S1 S2 S2\nM rs1 A G G G\n")
    for suffix in (".bgl.phased", ".bgl.gprobs", ".bgl.r2", ".dosage"):
        (root / f"run{suffix}").write_text("x\n")
    return root


@pytest.fixture
def sample_batch_dir(tmp_path: Path) -> Path:
    """A complete run with SNP2HLA's final outputs."""
    return _make_run(tmp_path / "batch_001")


@pytest.fixture
def reference_batch_dir(tmp_path: Path) -> Path:
    """A complete run that used a different Beagle window."""
    return _make_run(tmp_path / "batch_ref", window=500)


@pytest.fixture
def failed_batch_dir(tmp_path: Path) -> Path:
    """A run whose Beagle step ran out of memory."""
    batch_dir = tmp_path / "batch_failed"
    batch_dir.mkdir()
    (batch_dir / "run.bgl.log").write_text(
        "Start Beagle\njava.lang.OutOfMemoryError: Java heap space\n"
    )
    return batch_dir
