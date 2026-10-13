"""Anthropic Claude Provider for PRClaw."""

import json
import os
from typing import List, Optional
import httpx
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding
from prclaw.providers.base import BaseLLMProvider, ProviderConfig, REVIEW_SYSTEM_PROMPT


class AnthropicProvider(BaseLLMProvider):
    """Integrates with Anthropic Claude (or FCC proxy) for deep semantic reviews."""

    DEFAULT_API_URL = "https://api.anthropic.com/v1/messages"
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self, config: Optional[ProviderConfig] = None):
        cfg = config or ProviderConfig(
            model_name=self.DEFAULT_MODEL,
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            base_url=self.DEFAULT_API_URL,
            temperature=0.1,
        )
        if not cfg.base_url:
            cfg.base_url = self.DEFAULT_API_URL
        super().__init__(cfg)

    def _call_claude(self, prompt: str) -> str:
        """Send messages request to Anthropic API."""
        headers = {
            "x-api-key": self.config.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": self.config.model_name,
            "system": REVIEW_SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": self.config.temperature,
        }

        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            resp = client.post(self.config.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            texts = [
                b.get("text", "")
                for b in data.get("content", [])
                if b.get("type") == "text"
            ]
            return "".join(texts)

    def parse_findings(self, raw_text: str) -> List[ReviewFinding]:
        """Extract JSON block from Claude response."""
        if not raw_text:
            return []

        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start == -1 or end <= start:
            return []

        try:
            parsed = json.loads(raw_text[start:end + 1])
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

            results.append(
                ReviewFinding(
                    file_path=item.get("file_path", "unknown"),
                    line_number=item.get("line_number"),
                    rule_id=item.get("rule_id", "CLAUDE01"),
                    category=cat,
                    severity=sev,
                    message=item.get("message", "Issue flagged by Claude"),
                    suggestion=item.get("suggestion"),
                    confidence=float(item.get("confidence", 0.9)),
                )
            )

        return results

    def review_diff(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Review diffs using Anthropic Claude."""
        if not file_diffs:
            return []

        diff_text = self.format_diff_for_prompt(file_diffs)
        user_prompt = f"Review the following code changes and output JSON findings:\n\n{diff_text}"

        try:
            response_text = self._call_claude(user_prompt)
            return self.parse_findings(response_text)
        except Exception as e:
            return [
                ReviewFinding(
                    file_path=file_diffs[0].target_path if file_diffs else "general",
                    rule_id="SYS_CLAUDE_ERR",
                    category=FindingCategory.BUG,
                    severity=FindingSeverity.INFO,
                    message=f"Claude review failed: {e}",
                    confidence=1.0,
                )
            ]
