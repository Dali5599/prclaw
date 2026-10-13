"""Provider Factory and Fallback Chain for PRClaw."""

from typing import List, Optional
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding
from prclaw.providers.anthropic_provider import AnthropicProvider
from prclaw.providers.base import BaseLLMProvider, ProviderConfig
from prclaw.providers.ollama_provider import OllamaProvider
from prclaw.providers.openai_provider import OpenAICompatibleProvider


class ProviderFactory:
    """Creates provider instances based on name and config."""

    @staticmethod
    def create(name: str, config: Optional[ProviderConfig] = None) -> BaseLLMProvider:
        name_lower = name.lower()
        if name_lower in ("ollama", "local"):
            return OllamaProvider(config)
        elif name_lower in ("anthropic", "claude"):
            return AnthropicProvider(config)
        elif name_lower in ("openai", "gpt", "gemini"):
            return OpenAICompatibleProvider(config)
        else:
            raise ValueError(f"Unknown LLM provider: {name}. Supported: ollama, anthropic, openai")


class FallbackChainProvider(BaseLLMProvider):
    """Executes a primary provider with seamless fallback to backup providers."""

    def __init__(self, providers: List[BaseLLMProvider]):
        if not providers:
            raise ValueError("FallbackChainProvider requires at least one provider")
        self.providers = providers
        # Use primary provider's config
        super().__init__(providers[0].config)

    def review_diff(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Try each provider in order until one succeeds without fatal errors."""
        errors = []
        for p in self.providers:
            try:
                findings = p.review_diff(file_diffs)
                # Check if only system errors were returned
                has_fatal_err = any(
                    f.rule_id.startswith("SYS_") and f.severity == FindingSeverity.INFO
                    for f in findings
                )
                if not has_fatal_err or len(findings) > 1:
                    return findings
                errors.append(f"{p.__class__.__name__}: {findings[0].message}")
            except Exception as e:
                errors.append(f"{p.__class__.__name__}: {e}")

        # If all failed, return aggregated error finding
        return [
            ReviewFinding(
                file_path=file_diffs[0].target_path if file_diffs else "general",
                rule_id="SYS_ALL_PROVIDERS_FAILED",
                category=FindingCategory.BUG,
                severity=FindingSeverity.INFO,
                message=f"All providers in fallback chain failed: {'; '.join(errors)}",
                confidence=1.0,
            )
        ]
