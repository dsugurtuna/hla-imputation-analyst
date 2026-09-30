from hla_analyst.parsers import LogParser, ScriptParser


def test_parse_beagle_log(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("java -Xmx8g -jar beagle.jar unphased=test.bgl")

    cmd = LogParser.parse_beagle_log(log_file)
    assert cmd is not None
    assert cmd.jar_path == "beagle.jar"
    assert cmd.memory_setting == "8g"
    assert cmd.arguments["unphased"] == "test.bgl"


def test_parse_beagle_log_invalid(tmp_path):
    log_file = tmp_path / "invalid.log"
    log_file.write_text("No java command here")

    cmd = LogParser.parse_beagle_log(log_file)
    assert cmd is None


def test_extract_parameters(tmp_path):
    script_file = tmp_path / "test.csh"
    script_file.write_text("set MEMORY = 32g\nset THREADS = 8")

    params = ScriptParser.extract_parameters(script_file)
    assert params["MEMORY"] == "32g"
    assert params["THREADS"] == "8"
