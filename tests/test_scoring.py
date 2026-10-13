"""Tests for PRClaw scoring and severity filtering."""

import pytest
from prclaw.models import FindingSeverity, ReviewFinding, ReviewSummary
from prclaw.scoring import ScoringFilter


def test_scoring_filter_cutoffs():
    f_low_conf = ReviewFinding(
        file_path="a.py",
        rule_id="R1",
        severity=FindingSeverity.HIGH,
        message="high sev but low conf",
        confidence=0.5,
    )
    f_info = ReviewFinding(
        file_path="a.py",
        rule_id="R2",
        severity=FindingSeverity.INFO,
        message="info message",
        confidence=0.9,
    )
    f_good = ReviewFinding(
        file_path="a.py",
        rule_id="R3",
        severity=FindingSeverity.MEDIUM,
        message="good finding",
        confidence=0.85,
    )

    filt = ScoringFilter(min_confidence=0.70, min_severity=FindingSeverity.LOW)
    assert filt.should_keep(f_low_conf) is False
    assert filt.should_keep(f_info) is False
    assert filt.should_keep(f_good) is True

    kept = filt.filter_findings([f_low_conf, f_info, f_good])
    assert len(kept) == 1
    assert kept[0].rule_id == "R3"


def test_compute_health_score():
    filt = ScoringFilter()
    summary_clean = ReviewSummary()
    assert filt.compute_health_score(summary_clean) == 100

    summary_dirty = ReviewSummary()
    summary_dirty.add_finding(
        ReviewFinding(file_path="x.py", rule_id="SEC", severity=FindingSeverity.CRITICAL, message="crit")
    )
    summary_dirty.add_finding(
        ReviewFinding(file_path="x.py", rule_id="BUG", severity=FindingSeverity.HIGH, message="high")
    )
    # 100 - 35 - 15 = 50
    assert filt.compute_health_score(summary_dirty) == 50
