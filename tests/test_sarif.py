"""Tests for PRClaw SARIF formatter."""

import json
import pytest
from prclaw.formatters.sarif import SarifFormatter
from prclaw.models import FindingSeverity, ReviewFinding, ReviewSummary


def test_sarif_formatting():
    formatter = SarifFormatter()
    summary = ReviewSummary()
    summary.add_finding(
        ReviewFinding(
            file_path="src/sql.py",
            line_number=25,
            rule_id="SEC_SQLI",
            severity=FindingSeverity.CRITICAL,
            message="SQL Injection detected",
        )
    )

    sarif = formatter.format_sarif(summary)
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1

    driver = sarif["runs"][0]["tool"]["driver"]
    assert driver["name"] == "PRClaw"
    assert len(driver["rules"]) == 1
    assert driver["rules"][0]["id"] == "SEC_SQLI"

    results = sarif["runs"][0]["results"]
    assert len(results) == 1
    assert results[0]["ruleId"] == "SEC_SQLI"
    assert results[0]["level"] == "error"
    assert results[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "src/sql.py"
    assert results[0]["locations"][0]["physicalLocation"]["region"]["startLine"] == 25

    json_str = formatter.render_json(summary)
    assert json.loads(json_str) == sarif
