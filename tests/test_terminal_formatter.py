"""Tests for PRClaw terminal formatter."""

import pytest
from prclaw.formatters.terminal import TerminalFormatter
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding, ReviewSummary


def test_terminal_formatter_table_and_render():
    formatter = TerminalFormatter()
    summary = ReviewSummary(total_files_reviewed=2)
    summary.add_finding(
        ReviewFinding(
            file_path="src/main.py",
            line_number=10,
            rule_id="SEC_LEAK",
            category=FindingCategory.SECURITY,
            severity=FindingSeverity.CRITICAL,
            message="Secret token exposed",
            suggestion="Use env var",
        )
    )

    table = formatter.format_summary_table(summary)
    assert table.title == "🦅 PRClaw Review Summary"

    rendered = formatter.render_to_string(summary)
    assert "src/main.py:10" in rendered
    assert "SEC_LEAK" in rendered
    assert "Secret token exposed" in rendered
    assert "Use env var" in rendered
