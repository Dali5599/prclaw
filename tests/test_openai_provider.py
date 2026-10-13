"""Tests for PRClaw OpenAI & Gemini provider."""

import json
from unittest.mock import MagicMock, patch
import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingSeverity
from prclaw.providers.base import ProviderConfig
from prclaw.providers.openai_provider import OpenAICompatibleProvider


def test_openai_provider_defaults():
    provider = OpenAICompatibleProvider()
    assert provider.config.model_name == "gpt-4o"
    assert provider.config.base_url == "https://api.openai.com/v1"


def test_parse_findings_openai():
    provider = OpenAICompatibleProvider()
    data = json.dumps({
        "findings": [
            {
                "file_path": "api/routes.py",
                "line_number": 12,
                "rule_id": "PERF01",
                "category": "performance",
                "severity": "medium",
                "message": "N+1 query detected",
            }
        ]
    })
    findings = provider.parse_findings(data)
    assert len(findings) == 1
    assert findings[0].file_path == "api/routes.py"
    assert findings[0].severity == FindingSeverity.MEDIUM


@patch("httpx.Client.post")
def test_review_diff_openai_mocked(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({"findings": [{"file_path": "a.py", "rule_id": "SEC99", "message": "leak"}]})
                }
            }
        ]
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    hunk = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=["+ key=123"])
    fd = FileDiff(old_path="a.py", new_path="a.py", hunks=[hunk])

    provider = OpenAICompatibleProvider(ProviderConfig(model_name="gpt-4o", api_key="sk-fake"))
    findings = provider.review_diff([fd])
    assert len(findings) == 1
    assert findings[0].rule_id == "SEC99"
