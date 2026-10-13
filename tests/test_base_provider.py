"""Tests for PRClaw base provider and prompt templates."""

import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import ReviewFinding
from prclaw.providers.base import BaseLLMProvider, ProviderConfig, REVIEW_SYSTEM_PROMPT


class DummyProvider(BaseLLMProvider):
    def review_diff(self, file_diffs):
        return []


def test_provider_config():
    config = ProviderConfig(model_name="test-model", temperature=0.2)
    assert config.model_name == "test-model"
    assert config.temperature == 0.2
    assert config.timeout_seconds == 60


def test_format_diff_for_prompt():
    hunk = DiffHunk(
        old_start=1,
        new_start=1,
        header="@@ -1 +1 @@",
        lines=["- old line", "+ new line"],
    )
    fd = FileDiff(old_path="a.py", new_path="a.py", hunks=[hunk])
    provider = DummyProvider(ProviderConfig(model_name="dummy"))
    prompt = provider.format_diff_for_prompt([fd])

    assert "### File: a.py" in prompt
    assert "@@ -1 +1 @@" in prompt
    assert "+ new line" in prompt


def test_review_system_prompt_structure():
    assert "PRClaw" in REVIEW_SYSTEM_PROMPT
    assert "findings" in REVIEW_SYSTEM_PROMPT
    assert "severity" in REVIEW_SYSTEM_PROMPT
