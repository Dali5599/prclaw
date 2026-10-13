"""Tests for PRClaw security rules evaluator."""

import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingCategory, FindingSeverity
from prclaw.rules.security import SecurityRulesEvaluator


def test_detect_aws_secret():
    evaluator = SecurityRulesEvaluator()
    hunk = DiffHunk(
        old_start=1,
        new_start=10,
        header="@@ -1,1 +10,2 @@",
        lines=["+ AWS_KEY = 'AKIAIOSFODNN7EXAMPLE'"],
    )
    fd = FileDiff(new_path="config.py", hunks=[hunk])
    findings = evaluator.evaluate_diffs([fd])

    assert len(findings) == 1
    assert findings[0].rule_id == "SEC_AWS_KEY"
    assert findings[0].severity == FindingSeverity.CRITICAL
    assert findings[0].line_number == 10
    assert findings[0].category == FindingCategory.SECURITY


def test_detect_sql_injection():
    evaluator = SecurityRulesEvaluator()
    hunk = DiffHunk(
        old_start=1,
        new_start=50,
        header="@@ -1,1 +50,2 @@",
        lines=["+ cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"],
    )
    fd = FileDiff(new_path="db.py", hunks=[hunk])
    findings = evaluator.evaluate_diffs([fd])

    assert len(findings) == 1
    assert findings[0].rule_id == "SEC_RAW_SQL_FORMAT"
    assert findings[0].severity == FindingSeverity.HIGH
    assert findings[0].is_blocking is True


def test_clean_diff_no_findings():
    evaluator = SecurityRulesEvaluator()
    hunk = DiffHunk(
        old_start=1,
        new_start=1,
        header="@@ -1,1 +1,2 @@",
        lines=["+ token = os.getenv('AUTH_TOKEN')"],
    )
    fd = FileDiff(new_path="auth.py", hunks=[hunk])
    assert evaluator.evaluate_diffs([fd]) == []
