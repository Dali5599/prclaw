"""Tests for PRClaw Provider Factory and Fallback Chain."""

from unittest.mock import MagicMock
import pytest
from prclaw.diff_parser import DiffHunk, FileDiff
from prclaw.models import FindingSeverity, ReviewFinding
from prclaw.providers.anthropic_provider import AnthropicProvider
from prclaw.providers.factory import FallbackChainProvider, ProviderFactory
from prclaw.providers.ollama_provider import OllamaProvider
from prclaw.providers.openai_provider import OpenAICompatibleProvider


def test_provider_factory_creations():
    ollama_p = ProviderFactory.create("ollama")
    assert isinstance(ollama_p, OllamaProvider)

    claude_p = ProviderFactory.create("claude")
    assert isinstance(claude_p, AnthropicProvider)

    openai_p = ProviderFactory.create("openai")
    assert isinstance(openai_p, OpenAICompatibleProvider)

    with pytest.raises(ValueError):
        ProviderFactory.create("invalid-provider-xyz")


def test_fallback_chain_success_primary():
    mock_p1 = MagicMock()
    mock_p1.config.model_name = "p1"
    mock_p1.review_diff.return_value = [
        ReviewFinding(file_path="a.py", rule_id="OK01", message="Good finding")
    ]
    mock_p2 = MagicMock()

    chain = FallbackChainProvider([mock_p1, mock_p2])
    res = chain.review_diff([])
    assert len(res) == 1
    assert res[0].rule_id == "OK01"
    mock_p2.review_diff.assert_not_called()


def test_fallback_chain_failover_to_secondary():
    mock_p1 = MagicMock()
    mock_p1.config.model_name = "p1"
    mock_p1.review_diff.return_value = [
        ReviewFinding(
            file_path="a.py",
            rule_id="SYS_P1_ERR",
            severity=FindingSeverity.INFO,
            message="p1 down",
        )
    ]

    mock_p2 = MagicMock()
    mock_p2.review_diff.return_value = [
        ReviewFinding(file_path="a.py", rule_id="RESCUE01", message="Fallback success")
    ]

    chain = FallbackChainProvider([mock_p1, mock_p2])
    res = chain.review_diff([])
    assert len(res) == 1
    assert res[0].rule_id == "RESCUE01"
