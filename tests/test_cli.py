import sys
import os
import pytest
import subprocess
from typing import List, Tuple
from charfinder.constants import EXIT_SUCCESS, EXIT_NO_RESULTS, EXIT_INVALID_USAGE, EXIT_ARGPARSE_ERROR


def run_cli(args: List[str]) -> Tuple[str, str, int]:
    if '--color=never' not in args:
        args += ['--color=never']
    result = subprocess.run(
        ['charfinder'] + args,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def test_cli_strict_match() -> None:
    out, err, code = run_cli(['-q', 'heart'])
    assert 'WHITE HEART SUIT' in out
    assert code == EXIT_SUCCESS
    assert 'CODE' in out and 'CHAR' in out and 'NAME' in out


def test_cli_fuzzy_match() -> None:
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy'])
    assert 'GRINNING FACE' in out
    assert 'SCORE' in out
    assert code == EXIT_SUCCESS


def test_cli_threshold_loose() -> None:
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy', '--threshold', '0.5'])
    assert 'GRINNING FACE' in out
    assert code == EXIT_SUCCESS


def test_cli_threshold_strict() -> None:
    out, err, code = run_cli(['-q', 'zzxxyyq', '--fuzzy', '--threshold', '0.95'])
    assert code == EXIT_NO_RESULTS
    assert 'No matches found' in out


def test_cli_invalid_threshold() -> None:
    out, err, code = run_cli(['-q', 'heart', '--fuzzy', '--threshold', '1.5'])
    assert code == EXIT_ARGPARSE_ERROR
    assert 'Threshold must be between 0.0 and 1.0' in err


def test_cli_empty_query() -> None:
    out, err, code = run_cli(['-q', ''])
    assert code == EXIT_INVALID_USAGE
    assert 'empty' in err.lower()
    assert err.strip() != ''


def test_cli_unknown_flag() -> None:
    out, err, code = run_cli(['--doesnotexist'])
    assert code == EXIT_ARGPARSE_ERROR
    assert 'usage' in err.lower()
    assert err.strip() != ''


def test_cli_output_alignment_strict() -> None:
    out, _, code = run_cli(['-q', 'heart', '--quiet'])
    assert code == EXIT_SUCCESS
    lines = [line for line in out.splitlines() if line.strip() and not line.startswith('-')]
    assert any('WHITE HEART SUIT' in line for line in lines)
    assert all(line.startswith('U+') or line.startswith('CODE') for line in lines)


def test_cli_output_alignment_fuzzy() -> None:
    out, _, code = run_cli(['-q', 'grnning', '--quiet', '--fuzzy'])
    assert code == EXIT_SUCCESS
    lines = [line for line in out.splitlines() if line.strip() and not line.startswith('-')]
    assert any('GRINNING FACE' in line for line in lines)
    assert 'SCORE' in out
    for line in lines:
        if line.startswith('U+'):
            parts = line.split()
            assert len(parts) >= 4


def test_cli_hybrid_mode() -> None:
    out, err, code = run_cli(['-q', 'grnning', '--fuzzy', '--match-mode', 'hybrid'])
    assert code == EXIT_SUCCESS
    assert 'SCORE' in out
    assert any(line.startswith('U+') for line in out.splitlines())