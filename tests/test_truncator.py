"""Tests for PRClaw truncator and token budgeter."""

import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.truncator import TokenBudgeter


def test_estimate_tokens():
    budgeter = TokenBudgeter(max_tokens=100)
    assert budgeter.estimate_tokens("") == 0
    assert budgeter.estimate_tokens("hello world") == 3


def test_truncate_hunk_lines():
    budgeter = TokenBudgeter()
    lines = [f"+ line {i}" for i in range(100)]
    truncated, was_trunc = budgeter.truncate_hunk_lines(lines, max_lines=20)
    assert was_trunc is True
    assert len(truncated) == 21  # 10 + 1 note + 10
    assert "omitted by PRClaw" in truncated[10]


def test_truncate_diffs_over_budget():
    budgeter = TokenBudgeter(max_tokens=20)  # max_chars = 80
    long_lines = [f"+ long text line {i} with plenty of tokens" for i in range(50)]
    hunk = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=long_lines)
    file_diff = FileDiff(old_path="a.py", new_path="a.py", hunks=[hunk])

    budgeted, was_trunc = budgeter.truncate_diffs([file_diff])
    assert was_trunc is True
    assert len(budgeted) == 1
    assert "Token Budget Reached" in budgeted[0].hunks[0].lines[0]
