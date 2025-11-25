from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

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
    last_modified: Optional[datetime] = None
    file_type: FileType

class BeagleCommand(BaseModel):
    raw_command: str
    jar_path: Optional[str] = None
    memory_setting: Optional[str] = None
    arguments: Dict[str, str] = Field(default_factory=dict)

class BatchMetrics(BaseModel):
    batch_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    status: ImputationStatus
    input_files: List[FileInfo] = Field(default_factory=list)
    output_files: List[FileInfo] = Field(default_factory=list)
    logs: List[FileInfo] = Field(default_factory=list)
    command: Optional[BeagleCommand] = None
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ComparisonResult(BaseModel):
    source_batch: str
    target_batch: str
    identical_scripts: bool
    missing_files_in_target: List[str]
    parameter_diffs: Dict[str, Any]
