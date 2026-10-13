"""Tests for PRClaw git inspector module."""

import subprocess
import pytest
from prclaw.git_inspector import GitInspector


def test_git_inspector_in_current_repo(tmp_path):
    # Initialize a temporary git repository
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "TestUser"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)

    inspector = GitInspector(str(tmp_path))
    assert inspector.is_git_repo() is True

    # Create and commit a file
    hello_file = tmp_path / "hello.py"
    hello_file.write_text("print( v1)\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    # Modify file
    hello_file.write_text("print(v2)\n", encoding="utf-8")
    diffs = inspector.inspect_diff(base_ref=None)
    assert len(diffs) == 1
    assert diffs[0].target_path == "hello.py"
    assert len(diffs[0].hunks) == 1


def test_git_inspector_non_repo(tmp_path):
    inspector = GitInspector(str(tmp_path))
    assert inspector.is_git_repo() is False
    with pytest.raises(RuntimeError):
        inspector.get_current_branch()
