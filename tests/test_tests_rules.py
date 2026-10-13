"""Tests for PRClaw missing test coverage detector."""

import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingCategory, FindingSeverity
from prclaw.rules.tests import TestCoverageDetector


def test_flag_missing_tests_for_large_change():
    detector = TestCoverageDetector(min_added_lines_threshold=5)
    added = [f"+ line {i}" for i in range(10)]
    hunk = DiffHunk(old_start=1, new_start=1, header="@@ -1,1 +1,10 @@", lines=added)
    src_file = FileDiff(new_path="src/service.py", hunks=[hunk])

    findings = detector.evaluate_diffs([src_file])
    assert len(findings) == 1
    assert findings[0].rule_id == "TEST_MISSING_COVERAGE"
    assert findings[0].category == FindingCategory.TEST
    assert findings[0].severity == FindingSeverity.MEDIUM


def test_no_flag_when_tests_are_present():
    detector = TestCoverageDetector(min_added_lines_threshold=5)
    added_src = [f"+ line {i}" for i in range(10)]
    hunk_src = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=added_src)
    src_file = FileDiff(new_path="src/service.py", hunks=[hunk_src])

    added_test = ["+ def test_ok(): pass"]
    hunk_test = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=added_test)
    test_file = FileDiff(new_path="tests/test_service.py", hunks=[hunk_test])

    findings = detector.evaluate_diffs([src_file, test_file])
    assert findings == []


def test_ignore_small_edits():
    detector = TestCoverageDetector(min_added_lines_threshold=10)
    added_src = ["+ line 1", "+ line 2"]
    hunk = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=added_src)
    src_file = FileDiff(new_path="src/service.py", hunks=[hunk])

    findings = detector.evaluate_diffs([src_file])
    assert findings == []
