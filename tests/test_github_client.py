"""Tests for PRClaw GitHub client."""

from unittest.mock import MagicMock, patch
import pytest
from prclaw.github_client import GitHubClient
from prclaw.models import FindingSeverity, ReviewFinding, ReviewSummary


def test_format_pr_summary_markdown():
    client = GitHubClient(token="ghp_test")
    summary = ReviewSummary(total_files_reviewed=1)
    summary.add_finding(
        ReviewFinding(
            file_path="src/auth.py",
            line_number=20,
            rule_id="SEC_01",
            severity=FindingSeverity.HIGH,
            message="Insecure cookie flag",
        )
    )

    md = client.format_pr_summary_markdown(summary)
    assert "PRClaw Review Report" in md
    assert "BLOCKING ISSUES DETECTED" in md
    assert "`src/auth.py`:20" in md
    assert "Insecure cookie flag" in md


@patch("httpx.Client.post")
def test_post_issue_comment_mocked(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"id": 12345, "html_url": "https://github.com/..."}
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    client = GitHubClient(token="ghp_test")
    res = client.post_issue_comment("owner/repo", 42, "Hello review")
    assert res["id"] == 12345
    mock_post.assert_called_once()
