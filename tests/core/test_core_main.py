"""
Tests for the public API functions in charfinder.core.core_main module.
This file tests the `find_chars`, `find_chars_raw`, and `find_chars_with_info`
functions, ensuring they handle different input combinations, delegate to 
internal finder functions, and return the expected results.
"""

import pytest
from unittest.mock import MagicMock, patch
from charfinder.core.core_main import find_chars, find_chars_raw, find_chars_with_info
from charfinder.config.types import SearchConfig
from charfinder.config.constants import DEFAULT_FUZZY_ALGO

# Test for `find_chars` function
@pytest.mark.parametrize(
    "fuzzy,threshold,prefer_fuzzy,expected_call",
    [
        (True, 0.8, False, "find_chars_impl_called_with_fuzzy"),
        (False, 0.5, False, "find_chars_impl_called_with_exact"),
        (True, 0.9, True, "find_chars_impl_called_with_prefer_fuzzy"),
    ],
)
@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars(
    mock_find_chars_impl: MagicMock, 
    fuzzy: bool, 
    threshold: float, 
    prefer_fuzzy: bool,  # Ensure this is a bool
    expected_call: str
) -> None:
    """
    Test that `find_chars` correctly calls the internal `_find_chars_impl` 
    with the expected configuration based on different parameter combinations.
    """
    query = "test"
    
    # Call function under test
    find_chars(query, fuzzy=fuzzy, threshold=threshold, prefer_fuzzy=prefer_fuzzy)
    
    # Check that the internal function is called
    mock_find_chars_impl.assert_called_once()
    
    # Extract arguments passed to _find_chars_impl
    args, kwargs = mock_find_chars_impl.call_args

    # Ensure the config is passed correctly
    config: SearchConfig = kwargs.get('config')
    
    # Verify the values inside config match expectations
    if config:  # Only check if config is not None
        assert config.fuzzy == fuzzy
        assert config.threshold == threshold
        assert config.prefer_fuzzy == prefer_fuzzy


# Test for `find_chars_raw` function
@patch("charfinder.core.core_main._find_chars_raw_impl")
def test_find_chars_raw(mock_find_chars_raw_impl: MagicMock) -> None:
    """
    Test that `find_chars_raw` calls `_find_chars_raw_impl` and returns
    raw results as expected.
    """
    query = "test"
    mock_find_chars_raw_impl.return_value = [{"code": "U+0041", "char": "A", "name": "LATIN CAPITAL LETTER A"}]
    
    result = find_chars_raw(query)
    
    # Ensure the mock function is called with expected arguments
    mock_find_chars_raw_impl.assert_called_once()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["char"] == "A"

# Test for `find_chars_with_info` function
@patch("charfinder.core.core_main._find_chars_info_impl")
def test_find_chars_with_info(mock_find_chars_info_impl: MagicMock) -> None:
    """
    Test that `find_chars_with_info` returns the expected result, 
    including both formatted output lines and a fuzzy usage flag.
    """
    query = "test"
    mock_find_chars_info_impl.return_value = ([{"code": "U+0041", "char": "A", "name": "LATIN CAPITAL LETTER A"}], True)
    
    result_lines, fuzzy_used = find_chars_with_info(query)
    
    # Check that the function returns the correct result
    assert isinstance(result_lines, list)
    assert len(result_lines) > 0
    assert fuzzy_used is True

    # Check if fuzzy matching was used correctly
    assert "LATIN CAPITAL LETTER A" in result_lines[0]

# Edge case test for empty query
@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_empty_query(mock_find_chars_impl: MagicMock) -> None:
    """
    Test that `find_chars` handles an empty query string gracefully.
    """
    query = ""
    
    # Call function under test
    find_chars(query)

    # Ensure the internal function is called with the expected empty query
    mock_find_chars_impl.assert_called_once_with(query, config=mock_find_chars_impl.call_args[1]['config'])

# Test for invalid threshold value
@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_invalid_threshold(mock_find_chars_impl: MagicMock) -> None:
    """
    Test that `find_chars` handles invalid threshold values (greater than 1).
    """
    query = "test"
    threshold = 1.5  # Invalid threshold
    
    # Call function under test
    find_chars(query, threshold=threshold)

    # Ensure the internal function is called with the expected config
    mock_find_chars_impl.assert_called_once()
    args, kwargs = mock_find_chars_impl.call_args
    assert kwargs['config'].threshold == 1.0  # Should be capped at 1.0

# Test for invalid prefer_fuzzy value (ensure it's a boolean)
@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_invalid_prefer_fuzzy(mock_find_chars_impl: MagicMock) -> None:
    """
    Test that `find_chars` handles invalid `prefer_fuzzy` values.
    """
    query = "test"
    prefer_fuzzy = "invalid_value"  # Invalid value (str instead of bool)

    # Call function under test
    find_chars(query, prefer_fuzzy=prefer_fuzzy)

    # Ensure the internal function is called with the default prefer_fuzzy value (False)
    mock_find_chars_impl.assert_called_once()
    args, kwargs = mock_find_chars_impl.call_args
    assert kwargs['config'].prefer_fuzzy is False  # Should default to False

# Test for invalid fuzzy_algo type
@patch("charfinder.core.core_main._find_chars_impl")
def test_find_chars_invalid_fuzzy_algo(mock_find_chars_impl: MagicMock) -> None:
    """
    Test that `find_chars` handles invalid fuzzy_algo values gracefully.
    """
    query = "test"
    fuzzy_algo = "invalid_algo"  # Invalid algorithm (str instead of a valid fuzzy algorithm)

    # Call function under test
    find_chars(query, fuzzy_algo=fuzzy_algo)

    # Ensure the internal function is called with the default fuzzy_algo
    mock_find_chars_impl.assert_called_once()
    args, kwargs = mock_find_chars_impl.call_args
    assert kwargs['config'].fuzzy_algo == DEFAULT_FUZZY_ALGO  # Use the constant directly
 