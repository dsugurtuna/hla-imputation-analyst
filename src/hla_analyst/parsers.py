"""Parsers for Beagle logs and SNP2HLA csh scripts."""

from __future__ import annotations

import re
from pathlib import Path

from .models import BeagleCommand


class LogParser:
    """Find the Beagle command line in a log file.

    SNP2HLA appends Beagle's output to ``<OUTPUT>.bgl.log``; whether the
    java command itself appears there depends on how the run was launched,
    so this is a best-effort search for the first ``java ... -jar ...`` line.
    """

    BEAGLE_CMD_PATTERN = re.compile(r"java\s+(.*?)\s*-jar\s+(\S+)\s*(.*)")
    MEMORY_PATTERN = re.compile(r"-Xmx(\w+)")

    @staticmethod
    def parse_beagle_log(log_path: Path) -> BeagleCommand | None:
        """Return the first Beagle command found in the log, or None."""
        if not log_path.exists():
            return None
        content = log_path.read_text(encoding="utf-8", errors="ignore")
        match = LogParser.BEAGLE_CMD_PATTERN.search(content)
        if not match:
            return None
        jvm_args, jar_name, prog_args = match.groups()
        mem_match = LogParser.MEMORY_PATTERN.search(jvm_args)
        # Beagle 3 takes key=value arguments (unphased=..., out=..., ...).
        arguments = dict(arg.split("=", 1) for arg in prog_args.split() if "=" in arg)
        return BeagleCommand(
            raw_command=match.group(0).strip(),
            jar_path=jar_name,
            memory_setting=mem_match.group(1) if mem_match else None,
            arguments=arguments,
        )


class ScriptParser:
    """Read ``set NAME = value`` assignments from a csh script."""

    SET_PATTERN = re.compile(r"^\s*set\s+(\w+)\s*=\s*(.*?)\s*(#.*)?$")

    @staticmethod
    def extract_parameters(script_path: Path) -> dict[str, str]:
        """Return csh ``set`` assignments; later assignments win."""
        params: dict[str, str] = {}
        if not script_path.exists():
            return params
        for line in script_path.read_text(errors="ignore").splitlines():
            match = ScriptParser.SET_PATTERN.match(line)
            if match:
                params[match.group(1)] = match.group(2)
        return params
