import subprocess
import sys
import os
import pytest
from typing import List, Tuple

CLI_SCRIPT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'cli.py'))

def run_cli(args: List[str]) -> Tuple[str, str, int]:
    if not any(arg.startswith("--color") for arg in args):
        args += ["--color=never"]
    result = subprocess.run(
        [sys.executable, CLI_SCRIPT] + args,
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def test_cli_strict_match() -> None:
    out, err, code = run_cli(['-q', 'heart'])
    assert "WHITE HEART SUIT" in out
    assert code == 0

def test_cli_fuzzy_match() -> None:
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy'])
    assert "GRINNING FACE" in out
    assert code == 0

def test_cli_threshold_loose() -> None:
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy', '--threshold', '0.5'])
    assert "GRINNING FACE" in out
    assert code == 0

def test_cli_threshold_strict() -> None:
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy', '--threshold', '0.95'])
    assert code == 2
    assert "GRINNING" not in out

def test_cli_invalid_threshold() -> None:
    out, err, code = run_cli(['-q', 'heart', '--fuzzy', '--threshold', '1.5'])
    assert code != 0
    assert "Threshold must be between 0.0 and 1.0" in err

def test_cli_empty_query() -> None:
    out, err, code = run_cli(['-q', ''])
    assert code != 0
    assert "empty" in err.lower()

def test_cli_unknown_flag() -> None:
    out, err, code = run_cli(['--doesnotexist'])
    assert code != 0
    assert "usage" in err.lower()

def test_cli_output_alignment() -> None:
    out, _, code = run_cli(['-q', 'heart', '--quiet'])
    assert code == 0, "CLI did not exit cleanly"

    lines = [line for line in out.splitlines() if line.strip()]
    assert lines, "No output lines found"

    for line in lines:
        assert line.startswith("U+"), f"Line does not start with 'U+': {line}"

    col_lengths = [len(line.split('\t')) for line in lines]
    assert all(length >= 3 for length in col_lengths)