"""Tests for PRClaw Ollama provider."""

import json
from unittest.mock import MagicMock, patch
import httpx
import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingCategory, FindingSeverity
from prclaw.providers.base import ProviderConfig
from prclaw.providers.ollama_provider import OllamaProvider


def test_ollama_provider_defaults():
    provider = OllamaProvider()
    assert provider.config.model_name == "qwen2.5-coder:32b"
    assert provider.config.base_url == "http://127.0.0.1:11434"


def test_parse_findings_json():
    provider = OllamaProvider()
    sample_json = json.dumps({
        "findings": [
            {
                "file_path": "src/db.py",
                "line_number": 15,
                "rule_id": "SEC01",
                "category": "security",
                "severity": "critical",
                "message": "Potential SQL Injection",
                "confidence": 0.95,
            }
        ]
    })
    findings = provider.parse_findings_json(sample_json)
    assert len(findings) == 1
    f = findings[0]
    assert f.file_path == "src/db.py"
    assert f.severity == FindingSeverity.CRITICAL
    assert f.category == FindingCategory.SECURITY
    assert f.is_blocking is True


@patch("httpx.Client.post")
def test_review_diff_mocked(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "response": json.dumps({
            "findings": [
                {
                    "file_path": "test.py",
                    "rule_id": "BUG01",
                    "category": "bug",
                    "severity": "medium",
                    "message": "Logic error",
                }
            ]
        })
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    hunk = DiffHunk(old_start=1, new_start=1, header="@@ -1 +1 @@", lines=["+ test"])
    fd = FileDiff(old_path="test.py", new_path="test.py", hunks=[hunk])

    provider = OllamaProvider()
    findings = provider.review_diff([fd])
    assert len(findings) == 1
    assert findings[0].rule_id == "BUG01"
