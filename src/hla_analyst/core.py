import os
from datetime import datetime
from pathlib import Path

from .models import BatchMetrics, ComparisonResult, FileInfo, FileType, ImputationStatus
from .parsers import LogParser


class BatchAnalyzer:
    """Core logic for analyzing HLA imputation batches."""

    REQUIRED_ARTIFACTS = [".MHC.QC.bgl", ".dosage", ".bgl.phased"]

    def __init__(self, batch_dir: Path):
        self.batch_dir = Path(batch_dir)
        if not self.batch_dir.exists():
            raise FileNotFoundError(f"Batch directory not found: {self.batch_dir}")

    def analyze(self) -> BatchMetrics:
        """Performs a complete analysis of the batch."""

        metrics = BatchMetrics(
            batch_id=self.batch_dir.name, status=ImputationStatus.UNKNOWN
        )

        # 1. Scan for files
        self._scan_files(metrics)

        # 2. Analyze Logs
        self._analyze_logs(metrics)

        # 3. Validate Inputs
        self._validate_inputs(metrics)

        # 4. Determine Status
        self._determine_status(metrics)

        return metrics

    def _scan_files(self, metrics: BatchMetrics):
        """Scans the directory for relevant files."""
        for root, _, files in os.walk(self.batch_dir):
            for file in files:
                file_path = Path(root) / file
                f_info = self._get_file_info(file_path)

                if file.endswith(".log"):
                    f_info.file_type = FileType.LOG
                    metrics.logs.append(f_info)
                elif file.endswith(".sh") or file.endswith(".csh"):
                    f_info.file_type = FileType.SCRIPT
                    metrics.input_files.append(
                        f_info
                    )  # Scripts are inputs to the process
                elif any(file.endswith(ext) for ext in self.REQUIRED_ARTIFACTS):
                    f_info.file_type = FileType.ARTIFACT
                    metrics.output_files.append(f_info)
                elif file.endswith(".bgl"):
                    f_info.file_type = FileType.INPUT
                    metrics.input_files.append(f_info)

    def _get_file_info(self, path: Path) -> FileInfo:
        stat = path.stat()
        return FileInfo(
            path=path,
            exists=True,
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            file_type=FileType.UNKNOWN,
        )

    def _analyze_logs(self, metrics: BatchMetrics):
        """Parses logs to extract commands and errors."""
        for log_file in metrics.logs:
            # Prioritize Beagle logs
            if "beagle" in log_file.path.name.lower():
                command = LogParser.parse_beagle_log(log_file.path)
                if command:
                    metrics.command = command

            # Scan for errors
            try:
                with open(log_file.path, errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if "error" in line.lower():
                            metrics.errors.append(
                                f"{log_file.path.name}:{i} - {line.strip()}"
                            )
                        if "warning" in line.lower():
                            metrics.warnings.append(
                                f"{log_file.path.name}:{i} - {line.strip()}"
                            )
            except Exception:
                metrics.warnings.append(
                    f"Could not read log file: {log_file.path.name}"
                )

    def _validate_inputs(self, metrics: BatchMetrics):
        """Validates input file formats."""
        for input_file in metrics.input_files:
            if input_file.path.name.endswith(".QC.bgl"):
                try:
                    with open(input_file.path) as f:
                        header = f.readline()
                        cols = len(header.split())
                        if cols < 3:
                            metrics.errors.append(
                                f"Input file {input_file.path.name} has too few columns: {cols}"
                            )
                except Exception:
                    metrics.errors.append(
                        f"Could not validate input file: {input_file.path.name}"
                    )

    def _determine_status(self, metrics: BatchMetrics):
        """Determines the overall status of the batch."""
        if metrics.errors:
            metrics.status = ImputationStatus.FAILURE
            return

        # Check for required artifacts
        found_artifacts = {f.path.name for f in metrics.output_files}
        # This is a simplified check; in reality, we'd check for specific patterns
        # matching the input prefix.
        if not metrics.output_files:
            metrics.warnings.append("No output artifacts found.")

        if metrics.warnings:
            metrics.status = ImputationStatus.WARNING
        else:
            metrics.status = ImputationStatus.SUCCESS

    def compare_with(self, other_batch_dir: Path) -> ComparisonResult:
        """Compares this batch with another batch."""
        other_analyzer = BatchAnalyzer(other_batch_dir)
        # For now, just compare scripts

        my_script = self.batch_dir / "SNP2HLA.csh"
        other_script = other_batch_dir / "SNP2HLA.csh"

        identical = False
        if my_script.exists() and other_script.exists():
            import filecmp

            identical = filecmp.cmp(my_script, other_script)

        return ComparisonResult(
            source_batch=self.batch_dir.name,
            target_batch=other_batch_dir.name,
            identical_scripts=identical,
            missing_files_in_target=[],  # To be implemented
            parameter_diffs={},  # To be implemented
        )
