import re
from pathlib import Path

from .models import BeagleCommand


class LogParser:
    """Parses Beagle and SNP2HLA log files to extract execution details."""

    BEAGLE_CMD_PATTERN = re.compile(r"java\s+(.*?)\s+-jar\s+(.*?)\s+(.*)")
    MEMORY_PATTERN = re.compile(r"-Xmx(\w+)")

    @staticmethod
    def parse_beagle_log(log_path: Path) -> BeagleCommand | None:
        """
        Parses a Beagle log file to reconstruct the execution command.

        Args:
            log_path: Path to the log file.

        Returns:
            BeagleCommand object if found, None otherwise.
        """
        if not log_path.exists():
            return None

        try:
            with open(log_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Look for the command line invocation
            # This is a heuristic based on common log formats
            match = LogParser.BEAGLE_CMD_PATTERN.search(content)
            if match:
                jvm_args = match.group(1)
                jar_name = match.group(2)
                prog_args = match.group(3)

                # Extract memory setting
                mem_match = LogParser.MEMORY_PATTERN.search(jvm_args)
                memory = mem_match.group(1) if mem_match else None

                # Parse key=value arguments
                args_dict = {}
                for arg in prog_args.split():
                    if "=" in arg:
                        key, value = arg.split("=", 1)
                        args_dict[key] = value

                return BeagleCommand(
                    raw_command=match.group(0),
                    jar_path=jar_name,
                    memory_setting=memory,
                    arguments=args_dict,
                )

            # Fallback: Try to find lines starting with "Command:" or similar
            # (Implementation can be expanded based on specific log formats)

        except Exception as e:
            # Log error in a real app
            print(f"Error parsing log {log_path}: {e}")
            return None

        return None


class ScriptParser:
    """Parses shell scripts (SNP2HLA.csh) to extract configuration."""

    @staticmethod
    def extract_parameters(script_path: Path) -> dict[str, str]:
        """Extracts key parameters from the SNP2HLA script."""
        params = {}
        if not script_path.exists():
            return params

        try:
            with open(script_path) as f:
                for line in f:
                    line = line.strip()
                    # Simple variable assignment parsing (set var = val)
                    if line.startswith("set ") and "=" in line:
                        parts = line.split("=")
                        key = parts[0].replace("set", "").strip()
                        val = parts[1].strip()
                        params[key] = val
        except Exception:
            pass

        return params
