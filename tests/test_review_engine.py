"""Tests for PRClaw review engine orchestrator."""

from unittest.mock import MagicMock
import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingSeverity, ReviewFinding
from prclaw.review_engine import ReviewEngine


def test_review_engine_static_and_llm():
    mock_provider = MagicMock()
    mock_provider.review_diff.return_value = [
        ReviewFinding(
            file_path="src/api.py",
            rule_id="LLM_DEEP_CHECK",
            severity=FindingSeverity.LOW,
            message="Improve documentation",
        )
    ]

    hunk = DiffHunk(
        old_start=1,
        new_start=1,
        header="@@ -1,1 +1,2 @@",
        lines=["+ AWS_SECRET =  AKIAIOSFODNN7EXAMPLE"],
    )
    fd = FileDiff(new_path="src/api.py", hunks=[hunk])

    engine = ReviewEngine(provider=mock_provider, enable_static_rules=True, enable_llm=True)
    summary = engine.review([fd])

    assert summary.total_files_reviewed == 1
    # 1 static sec rule + 1 LLM finding (total >= 2)
    assert summary.total_findings >= 2
    assert summary.has_blocking_issues is True  # AWS secret is critical
    assert summary.execution_time_seconds >= 0.0


def test_review_engine_filters_non_reviewable():
    fd_bin = FileDiff(new_path="image.png", is_binary=True)
    engine = ReviewEngine(enable_static_rules=True, enable_llm=False)
    summary = engine.review([fd_bin])

    assert summary.total_files_reviewed == 0
    assert summary.total_findings == 0
