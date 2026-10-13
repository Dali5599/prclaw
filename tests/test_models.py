"""Tests for PRClaw models and findings."""

import pytest
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding, ReviewSummary


def test_review_finding_creation_and_blocking():
    finding_crit = ReviewFinding(
        file_path="src/auth.py",
        line_number=42,
        rule_id="SEC001",
        category=FindingCategory.SECURITY,
        severity=FindingSeverity.CRITICAL,
        message="Hardcoded API secret found",
        suggestion="os.environ.get( SECRET)",
    )
    assert finding_crit.is_blocking is True
    assert finding_crit.category == FindingCategory.SECURITY
    assert finding_crit.severity == FindingSeverity.CRITICAL
    assert finding_crit.confidence == 0.9

    finding_info = ReviewFinding(
        file_path="src/readme.md",
        rule_id="STYLE01",
        category=FindingCategory.STYLE,
        severity=FindingSeverity.INFO,
        message="Trailing whitespace",
    )
    assert finding_info.is_blocking is False


def test_review_summary_aggregation():
    summary = ReviewSummary(total_files_reviewed=3)
    assert summary.total_findings == 0
    assert summary.has_blocking_issues is False

    f1 = ReviewFinding(
        file_path="app.py",
        rule_id="BUG01",
        category=FindingCategory.BUG,
        severity=FindingSeverity.LOW,
        message="Unused import",
    )
    summary.add_finding(f1)
    assert summary.total_findings == 1
    assert summary.has_blocking_issues is False

    f2 = ReviewFinding(
        file_path="db.py",
        rule_id="SEC02",
        category=FindingCategory.SECURITY,
        severity=FindingSeverity.HIGH,
        message="SQL Injection potential",
    )
    summary.add_finding(f2)
    assert summary.total_findings == 2
    assert summary.has_blocking_issues is True
