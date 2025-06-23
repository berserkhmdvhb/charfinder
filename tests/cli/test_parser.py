"""Tests for cli/parser.py."""

from unittest.mock import patch
from charfinder.cli.parser import create_parser


@patch.dict("sys.modules", {"argcomplete": None})
def test_parser_skips_argcomplete_if_not_installed() -> None:
    """Should not fail if argcomplete is missing."""
    parser = create_parser()
    assert parser is not None


def test_parser_contains_required_arguments() -> None:
    """Parser should include key arguments like --fuzzy and --threshold."""
    parser = create_parser()
    args = parser.parse_args(["--fuzzy", "--threshold", "0.75", "heart"])
    assert args.fuzzy is True
    assert args.threshold == 0.75
    assert args.positional_query == ["heart"]
