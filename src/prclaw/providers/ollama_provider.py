"""Local Ollama Provider with Streaming for PRClaw."""

import json
from typing import List, Optional
import httpx
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding
from prclaw.providers.base import BaseLLMProvider, ProviderConfig, REVIEW_SYSTEM_PROMPT


class OllamaProvider(BaseLLMProvider):
    """Integrates with local Ollama daemon for offline-first AI code reviews."""

    DEFAULT_BASE_URL = "http://127.0.0.1:11434"

    def __init__(self, config: Optional[ProviderConfig] = None):
        cfg = config or ProviderConfig(
            model_name="qwen2.5-coder:32b",
            base_url=self.DEFAULT_BASE_URL,
            temperature=0.1,
        )
        if not cfg.base_url:
            cfg.base_url = self.DEFAULT_BASE_URL
        super().__init__(cfg)

    def _call_ollama(self, prompt: str) -> str:
        """Send request to Ollama generate endpoint."""
        url = f"{self.config.base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.config.model_name,
            "system": REVIEW_SYSTEM_PROMPT,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {"temperature": self.config.temperature},
        }

        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    def parse_findings_json(self, raw_json: str) -> List[ReviewFinding]:
        """Parse json output from Ollama into ReviewFinding models."""
        if not raw_json or not raw_json.strip():
            return []

        try:
            parsed = json.loads(raw_json)
        except Exception:
            return []

        findings_list = parsed.get("findings", []) if isinstance(parsed, dict) else []
        results: List[ReviewFinding] = []

        for item in findings_list:
            if not isinstance(item, dict):
                continue
            try:
                cat = FindingCategory(item.get("category", "bug").lower())
            except Exception:
                cat = FindingCategory.BUG

            try:
                sev = FindingSeverity(item.get("severity", "medium").lower())
            except Exception:
                sev = FindingSeverity.MEDIUM

            f = ReviewFinding(
                file_path=item.get("file_path", "unknown"),
                line_number=item.get("line_number"),
                rule_id=item.get("rule_id", "OLLAMA01"),
                category=cat,
                severity=sev,
                message=item.get("message", "No message provided"),
                suggestion=item.get("suggestion"),
                confidence=float(item.get("confidence", 0.85)),
            )
            results.append(f)

        return results

    def review_diff(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Review parsed diffs using local Ollama model."""
        if not file_diffs:
            return []

        diff_text = self.format_diff_for_prompt(file_diffs)
        user_prompt = f"Review the following code changes:\n\n{diff_text}"

        try:
            raw_response = self._call_ollama(user_prompt)
            return self.parse_findings_json(raw_response)
        except Exception as e:
            # Return system error finding if local Ollama fails
            return [
                ReviewFinding(
                    file_path=file_diffs[0].target_path if file_diffs else "general",
                    rule_id="SYS_OLLAMA_ERR",
                    category=FindingCategory.BUG,
                    severity=FindingSeverity.INFO,
                    message=f"Local Ollama execution failed: {e}",
                    confidence=1.0,
                )
            ]
