"""Tests for PRClaw Anthropic provider."""

import json
from unittest.mock import MagicMock, patch
import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingSeverity
from prclaw.providers.anthropic_provider import AnthropicProvider
from prclaw.providers.base import ProviderConfig


def test_anthropic_provider_defaults():
    provider = AnthropicProvider()
    assert "claude-3-5" in provider.config.model_name
    assert provider.config.base_url == "https://api.anthropic.com/v1/messages"


def test_parse_findings_from_markdown():
    provider = AnthropicProvider()
    raw = """Here is the analysis:
```json
{
  "findings": [
    {
      "file_path": "lib/crypto.py",
      "line_number": 88,
      "rule_id": "SEC_WEAK_HASH",
      "category": "security",
      "severity": "high",
      "message": "Use of MD5 is cryptographically broken",
      "suggestion": "hashlib.sha256()"
    }
  ]
}
```
Done."""
    findings = provider.parse_findings(raw)
    assert len(findings) == 1
    assert findings[0].file_path == "lib/crypto.py"
    assert findings[0].severity == FindingSeverity.HIGH
    assert findings[0].suggestion == "hashlib.sha256()"


@patch("httpx.Client.post")
def test_review_diff_anthropic_mocked(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "content": [
            {
                "type": "text",
                "text": json.dumps({"findings": [{"file_path": "x.py", "rule_id": "BUG02", "message": "error"}]}),
            }
        ]
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    hunk = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=["+ code"])
    fd = FileDiff(old_path="x.py", new_path="x.py", hunks=[hunk])

    provider = AnthropicProvider(ProviderConfig(model_name="claude-3-5-sonnet", api_key="sk-test"))
    findings = provider.review_diff([fd])
    assert len(findings) == 1
    assert findings[0].rule_id == "BUG02"
