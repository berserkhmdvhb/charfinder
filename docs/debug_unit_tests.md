## Debuggning Unit Tests

### Print Statements

In following we see examples of adding `print` statements in a unit test to have better visilibity:

#### Example 1

```python
@pytest.mark.parametrize("suppress_echo", [True, False])
def test_handlers_always_include_filters(
    temp_log_dir: Path,
    suppress_echo: bool,
) -> None:
    """
    All handlers must include EnvironmentFilter.
    StreamHandler must also include StreamFilter, regardless of echo suppression.
    """
    handlers = setup_logging(
        log_dir=temp_log_dir,
        reset=True,
        return_handlers=True,
        suppress_echo=suppress_echo,
    )
    assert handlers is not None
    for handler in handlers:
        print(f"\nHandler: {handler}")
        print(f"  Type: {type(handler)}")
        print(f"  Filters: {[type(f).__name__ for f in handler.filters]}")
        print(f"  suppress_echo: {suppress_echo}")
        # Always expect EnvironmentFilter
        has_env_filter = any(isinstance(f, EnvironmentFilter) for f in handler.filters)
        print(f"  Has EnvironmentFilter: {has_env_filter}")
        assert has_env_filter, f"{type(handler)} missing EnvironmentFilter"
        # Match only the true StreamHandler, not subclasses
        if type(handler) is logging.StreamHandler:
            has_stream_filter = any(isinstance(f, StreamFilter) for f in handler.filters)
            print(f"  Has StreamFilter: {has_stream_filter}")
            assert has_stream_filter, f"{type(handler)} missing StreamFilter"
        else:
            # All other handlers (e.g. file) must NOT have StreamFilter
            has_stream_filter = any(isinstance(f, StreamFilter) for f in handler.filters)
            print(f"  Has StreamFilter (non-stream): {has_stream_filter}")
            assert not has_stream_filter, f"{type(handler)} should not have StreamFilter"
```

#### Example 2 

```python
def test_unicode_normalization_forms(
    input_text: str,
    expected_by_form: dict[NormalizationForm, str],
    form: NormalizationForm,
) -> None:
    """Test normalization behavior across all Unicode normalization forms."""
    result = normalize(input_text, profile="medium", form=form)
    expected = expected_by_form[form].upper()
    assert result == expected
```


#### Example 3

```python
def test_unicode_normalization_forms(
    input_text: str,
    expected_by_form: dict[NormalizationForm, str],
    form: NormalizationForm,
) -> None:
    """Test normalization behavior across all Unicode normalization forms."""
    result = normalize(input_text, profile="medium", form=form)
    expected = expected_by_form[form].upper()
    # Debug output
    print("\n" + "-" * 40)
    print(f"Input text           : {repr(input_text)}")
    print(f"Normalization form   : {form}")
    print(f"Expected (normalized): {repr(expected)}")
    print(f"Actual result        : {repr(result)}")
    print("-" * 40)
    assert result == expected
```

### Capturing `echo()` outputs

#### Example 1
Example that captures `echo()`  when original function hast `stream` input that is passed to `echo(steram=StringIO())`

```python
def test_resolve_dotenv_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHARFINDER_ROOT_DIR_FOR_TESTS", str(tmp_path))
    assert settings.resolve_dotenv_path() is None
    env_file = tmp_path / ".env"
    env_file.write_text("DUMMY=1\n")
    assert settings.resolve_dotenv_path() == env_file
    fake_path = tmp_path / "nonexistent.env"
    monkeypatch.setenv("DOTENV_PATH", str(fake_path))
    monkeypatch.setenv("CHARFINDER_DEBUG_ENV_LOAD", "1")
    stream = StringIO()
    result = settings.resolve_dotenv_path(stream=stream)
    assert result == fake_path
    assert "DOTENV_PATH is set to" in stream.getvalue()
```

#### Example 2

An example that captures `echo()` without usage of stream input:

```python
def test_fuzzy_match_verbose_logging(
    fuzzy_context: FuzzyMatchContext,
    sample_name_cache: dict[str, dict[str, str]],
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    """Fuzzy match emits verbose logs when verbose=True."""
    fuzzy_context.verbose = True
    fuzzy_context.query = "check"
    fuzzy_context.threshold = 0.5
    fuzzy_context.fuzzy_algo = "token_sort_ratio"
    results = find_fuzzy_matches("check", sample_name_cache, fuzzy_context)
    output = log_stream.getvalue()
    assert results
    assert "trying fuzzy" in output
    assert "threshold=0.5" in output
```

#### Example 3

```python
def test_handle_empty_query_logs_error() -> None:
    with patch("charfinder.cli.handlers.echo") as mock_echo:
        result = handle_empty_query(use_color=False)
        assert result.exit_code == EXIT_INVALID_USAGE
        assert result.match_info is None
        mock_echo.assert_called_once()
        called_msg = mock_echo.call_args[0][0]
        assert "query must not be empty" in called_msg.lower()
```

#### Example 4


```python
@patch("charfinder.cli.utils_runner.echo")
@patch("charfinder.cli.utils_runner.get_version", return_value="TEST_VERSION")
@patch("charfinder.cli.utils_runner.teardown_logger")
@patch("charfinder.cli.utils_runner.handle_find_chars")
@patch("charfinder.cli.utils_runner.get_environment", return_value="DEV")
def test_handle_cli_workflow_success(
    mock_get_environment: MagicMock,
    mock_handle_find_chars: MagicMock,
    mock_teardown_logger: MagicMock,
    mock_get_version: MagicMock,
    mock_echo: MagicMock,
) -> None:
    """Runs CLI workflow successfully and emits correct echo message."""
    args = Namespace(verbose=True, debug=False, color="auto", threshold=0.75)
    mock_handle_find_chars.return_value = MatchResult(exit_code=EXIT_SUCCESS, match_info=None)
    exit_code = utils_runner.handle_cli_workflow(args, query_str="✓", use_color=True)
    assert exit_code == EXIT_SUCCESS
    # Find the echo call that contains the version log
    called_msgs = [call.args[0] for call in mock_echo.call_args_list]
    debug_print = "\n".join(called_msgs)
    print("---- Echo Messages ----")
    print(debug_print)
    print("------------------------")
    assert any("CharFinder TEST_VERSION CLI started" in msg for msg in called_msgs)
```

### Isolate Test Directory

To isolate test directory, use fixture `setup_test_root`:


First in input of test function use like this:
`setup_test_root: Callable[[], Path]`

Then call it like this:

`root = setup_test_root()`
`unicode_file = root / "UnicodeData.txt"`

For logging, it is set like this:


```python
setup_test_root()
logger = get_logger()
setup_logging(log_dir=temp_log_dir, reset=True)
```

But to use like this, you need to insert the fixture in each function.
To apply this at file level, use the wrapper fixture `_use_isolated_root` by putting it on top of test file:

```python
@pytest.fixture(autouse=True)
def _use_isolated_root(setup_test_root: Callable[[], Path]) -> None:
    """Ensure CHARFINDER_ROOT_DIR_FOR_TESTS is isolated for all tests."""
    setup_test_root()
```

