"""Tests for PRClaw bug pattern and performance rules."""

import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingCategory, FindingSeverity
from prclaw.rules.bugs import BugAndPerformanceRulesEvaluator


def test_detect_mutable_default():
    evaluator = BugAndPerformanceRulesEvaluator()
    hunk = DiffHunk(
        old_start=1,
        new_start=5,
        header="@@ -1,1 +5,2 @@",
        lines=["+ def append_item(val, target=[]):"],
    )
    fd = FileDiff(new_path="service.py", hunks=[hunk])
    findings = evaluator.evaluate_diffs([fd])

    assert len(findings) == 1
    assert findings[0].rule_id == "BUG_MUTABLE_DEFAULT_ARG"
    assert findings[0].category == FindingCategory.BUG
    assert findings[0].severity == FindingSeverity.MEDIUM


def test_detect_bare_except():
    evaluator = BugAndPerformanceRulesEvaluator()
    hunk = DiffHunk(
        old_start=1,
        new_start=20,
        header="@@ -1,1 +20,2 @@",
        lines=["+ except:"],
    )
    fd = FileDiff(new_path="worker.py", hunks=[hunk])
    findings = evaluator.evaluate_diffs([fd])

    assert len(findings) == 1
    assert findings[0].rule_id == "BUG_BARE_EXCEPT"


def test_detect_linear_lookup_perf():
    evaluator = BugAndPerformanceRulesEvaluator()
    hunk = DiffHunk(
        old_start=1,
        new_start=33,
        header="@@ -1,1 +33,2 @@",
        lines=["+ if item in ['apple', 'banana', 'orange']:"],
    )
    fd = FileDiff(new_path="calc.py", hunks=[hunk])
    findings = evaluator.evaluate_diffs([fd])

    assert len(findings) == 1
    assert findings[0].rule_id == "PERF_UNINDEXED_LINEAR_LOOKUP"
    assert findings[0].category == FindingCategory.PERFORMANCE
