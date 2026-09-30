"""Batch analysis for SNP2HLA / Beagle run directories."""

from __future__ import annotations

import filecmp
import re
from datetime import datetime
from pathlib import Path

from .models import (
    BatchMetrics,
    ComparisonResult,
    FileInfo,
    FileType,
    ImputationStatus,
)
from .parsers import LogParser, ScriptParser

# SNP2HLA's final outputs. <OUTPUT>.MHC.* intermediates (including
# <OUTPUT>.MHC.QC.bgl) are deleted by the script's default cleanup step, so
# they are checked when present but never required.
REQUIRED_ARTIFACTS = (".bgl.phased", ".bgl.gprobs", ".bgl.r2", ".dosage")

# A line is an error if it names an error or exception as a word, or a
# classic Java/OS failure. "0 errors" and "no errors" are not errors.
ERROR_PATTERN = re.compile(
    r"\b(error|exception)\b|OutOfMemoryError|Segmentation fault|Killed",
    re.IGNORECASE,
)
NOT_AN_ERROR = re.compile(r"\b(no|0)\s+errors?\b", re.IGNORECASE)
WARNING_PATTERN = re.compile(r"\bwarning\b", re.IGNORECASE)


class BatchAnalyzer:
    """Health check for one imputation run directory."""

    REQUIRED_ARTIFACTS = REQUIRED_ARTIFACTS

    def __init__(self, batch_dir: Path | str) -> None:
        self.batch_dir = Path(batch_dir)
        if not self.batch_dir.is_dir():
            raise FileNotFoundError(f"Batch directory not found: {self.batch_dir}")

    def analyze(self) -> BatchMetrics:
        """Scan files, read logs, validate Beagle inputs and set a status."""
        metrics = BatchMetrics(
            batch_id=self.batch_dir.name, status=ImputationStatus.UNKNOWN
        )
        self._scan_files(metrics)
        self._analyze_logs(metrics)
        self._validate_inputs(metrics)
        self._determine_status(metrics)
        return metrics

    def _scan_files(self, metrics: BatchMetrics) -> None:
        for path in sorted(p for p in self.batch_dir.rglob("*") if p.is_file()):
            name = path.name
            info = self._file_info(path)
            if name.endswith(".log"):
                info.file_type = FileType.LOG
                metrics.logs.append(info)
            elif name.endswith((".sh", ".csh")):
                info.file_type = FileType.SCRIPT
                metrics.input_files.append(info)
            elif name.endswith(REQUIRED_ARTIFACTS):
                info.file_type = FileType.ARTIFACT
                metrics.output_files.append(info)
            elif name.endswith(".bgl"):
                info.file_type = FileType.INPUT
                metrics.input_files.append(info)
        names = [f.path.name for f in metrics.output_files]
        metrics.missing_artifacts = [
            f"*{suffix}"
            for suffix in REQUIRED_ARTIFACTS
            if not any(n.endswith(suffix) for n in names)
        ]

    @staticmethod
    def _file_info(path: Path) -> FileInfo:
        stat = path.stat()
        return FileInfo(
            path=path,
            exists=True,
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            file_type=FileType.UNKNOWN,
        )

    @staticmethod
    def _is_beagle_log(name: str) -> bool:
        return name.endswith(".bgl.log") or "beagle" in name.lower()

    def _analyze_logs(self, metrics: BatchMetrics) -> None:
        for log in metrics.logs:
            if metrics.command is None and self._is_beagle_log(log.path.name):
                metrics.command = LogParser.parse_beagle_log(log.path)
            text = log.path.read_text(errors="ignore")
            for i, line in enumerate(text.splitlines(), 1):
                where = f"{log.path.name}:{i} - {line.strip()}"
                if ERROR_PATTERN.search(line) and not NOT_AN_ERROR.search(line):
                    metrics.errors.append(where)
                elif WARNING_PATTERN.search(line):
                    metrics.warnings.append(where)

    def _validate_inputs(self, metrics: BatchMetrics) -> None:
        """Check Beagle-format .bgl files have two columns per sample.

        A Beagle 3 unphased file has two leading columns (line type and
        marker or ID) and then two columns per sample, so the total must be
        even and greater than two.
        """
        for f in metrics.input_files:
            if not f.path.name.endswith(".bgl"):
                continue
            with open(f.path, errors="ignore") as fh:
                cols = len(fh.readline().split())
            name = f.path.name
            if cols <= 2:
                metrics.errors.append(f"Input file {name} has too few columns: {cols}")
            elif (cols - 2) % 2:
                metrics.errors.append(
                    f"Input file {name} has an odd number of genotype columns "
                    f"({cols - 2}); Beagle expects two per sample"
                )

    @staticmethod
    def _determine_status(metrics: BatchMetrics) -> None:
        for artifact in metrics.missing_artifacts:
            metrics.errors.append(f"Missing required output: {artifact}")
        if metrics.errors:
            metrics.status = ImputationStatus.FAILURE
        elif metrics.warnings:
            metrics.status = ImputationStatus.WARNING
        else:
            metrics.status = ImputationStatus.SUCCESS

    def compare_with(self, other_batch_dir: Path | str) -> ComparisonResult:
        """Compare this run with a reference run.

        Reports whether SNP2HLA.csh is byte-identical, which ``set``
        parameters differ, and which required outputs the reference has
        that this run lacks.
        """
        other = BatchAnalyzer(other_batch_dir)
        mine = self.batch_dir / "SNP2HLA.csh"
        theirs = other.batch_dir / "SNP2HLA.csh"
        identical = (
            mine.exists()
            and theirs.exists()
            and filecmp.cmp(mine, theirs, shallow=False)
        )
        p_mine = ScriptParser.extract_parameters(mine)
        p_theirs = ScriptParser.extract_parameters(theirs)
        diffs = {
            key: {"this": p_mine.get(key), "reference": p_theirs.get(key)}
            for key in sorted(set(p_mine) | set(p_theirs))
            if p_mine.get(key) != p_theirs.get(key)
        }
        my_missing = set(self.analyze().missing_artifacts)
        their_missing = set(other.analyze().missing_artifacts)
        return ComparisonResult(
            source_batch=self.batch_dir.name,
            target_batch=other.batch_dir.name,
            identical_scripts=identical,
            missing_vs_reference=sorted(my_missing - their_missing),
            parameter_diffs=diffs,
        )
