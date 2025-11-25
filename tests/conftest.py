import pytest
from pathlib import Path
import shutil

@pytest.fixture
def sample_batch_dir(tmp_path):
    """Creates a temporary directory with sample batch files for testing."""
    batch_dir = tmp_path / "batch_001"
    batch_dir.mkdir()
    
    # Create a dummy log file
    log_file = batch_dir / "beagle.log"
    log_file.write_text("""
    Start Beagle
    Command: java -Xmx16g -jar beagle.jar unphased=input.bgl out=output
    Finished
    """)
    
    # Create a dummy script
    script_file = batch_dir / "SNP2HLA.csh"
    script_file.write_text("""
    #!/bin/csh
    set MEM = 16g
    java -jar beagle.jar
    """)
    
    # Create a dummy input file
    input_file = batch_dir / "input.QC.bgl"
    input_file.write_text("id1 id2 id3\n1 2 3")
    
    # Create dummy artifacts
    (batch_dir / "output.MHC.QC.bgl").touch()
    (batch_dir / "output.dosage").touch()
    (batch_dir / "output.bgl.phased").touch()
    
    return batch_dir

@pytest.fixture
def failed_batch_dir(tmp_path):
    """Creates a temporary directory representing a failed batch."""
    batch_dir = tmp_path / "batch_failed"
    batch_dir.mkdir()
    
    log_file = batch_dir / "beagle.log"
    log_file.write_text("""
    Start Beagle
    Error: Out of memory
    """)
    
    return batch_dir
