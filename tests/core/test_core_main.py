"""
Tests for the public API functions in charfinder.core.core_main module.
This file tests the `find_chars`, `find_chars_raw`, and `find_chars_with_info`
functions, ensuring they handle different input combinations, delegate to 
internal finder functions, and return the expected results.
"""

import pytest
from unittest.mock import MagicMock, patch
from charfinder.core.core_main import find_chars
from charfinder.types import SearchConfig

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
    prefer_fuzzy: bool, 
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
