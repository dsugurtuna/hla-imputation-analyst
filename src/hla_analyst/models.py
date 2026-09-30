from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ImputationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    WARNING = "WARNING"
    UNKNOWN = "UNKNOWN"


class FileType(str, Enum):
    LOG = "log"
    SCRIPT = "script"
    INPUT = "input"
    OUTPUT = "output"
    ARTIFACT = "artifact"
    UNKNOWN = "unknown"


class FileInfo(BaseModel):
    path: Path
    exists: bool
    size_bytes: int = 0
    last_modified: datetime | None = None
    file_type: FileType


class BeagleCommand(BaseModel):
    raw_command: str
    jar_path: str | None = None
    memory_setting: str | None = None
    arguments: dict[str, str] = Field(default_factory=dict)


class BatchMetrics(BaseModel):
    batch_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: ImputationStatus
    input_files: list[FileInfo] = Field(default_factory=list)
    output_files: list[FileInfo] = Field(default_factory=list)
    logs: list[FileInfo] = Field(default_factory=list)
    command: BeagleCommand | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ComparisonResult(BaseModel):
    source_batch: str
    target_batch: str
    identical_scripts: bool
    missing_files_in_target: list[str]
    parameter_diffs: dict[str, Any]
