from pathlib import Path

def test_logs_are_only_created_in_test_env(tmp_path: Path) -> None:
    """Ensure test code creates logs in logs/TEST only, not in DEV/PROD/etc."""
    from shutil import copytree
    import tempfile

    log_root = Path.cwd() / "logs"
    pre_existing_dirs = {p.name for p in log_root.iterdir() if p.is_dir()} if log_root.exists() else set()

    # Run your test logic here that triggers log creation
    # (In real usage, this test should be run after test-triggering log creation)

    post_existing_dirs = {p.name for p in log_root.iterdir() if p.is_dir()}

    # Check that logs/TEST was created
    assert "TEST" in post_existing_dirs, "Expected logs/TEST directory missing"

    # Check that no unexpected log directories were added
    new_dirs = post_existing_dirs - pre_existing_dirs
    unexpected_dirs = new_dirs - {"TEST"}
    assert not unexpected_dirs, f"Unexpected log directories created by tests: {unexpected_dirs}"
