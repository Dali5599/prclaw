"""OpenAI and Gemini Compatible Provider for PRClaw."""

import json
import os
from typing import List, Optional
import httpx
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding
from prclaw.providers.base import BaseLLMProvider, ProviderConfig, REVIEW_SYSTEM_PROMPT


class OpenAICompatibleProvider(BaseLLMProvider):
    """Integrates with OpenAI API or Gemini (via OpenAI-compatible endpoint)."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, config: Optional[ProviderConfig] = None):
        cfg = config or ProviderConfig(
            model_name=self.DEFAULT_MODEL,
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=self.DEFAULT_BASE_URL,
            temperature=0.1,
        )
        if not cfg.base_url:
            cfg.base_url = self.DEFAULT_BASE_URL
        super().__init__(cfg)

    def _call_chat_completions(self, prompt: str) -> str:
        """Send request to /chat/completions endpoint."""
        url = f"{self.config.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key or ''}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.model_name,
            "messages": [
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"},
        }

        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def parse_findings(self, raw_json: str) -> List[ReviewFinding]:
        """Parse json output into ReviewFinding models."""
        if not raw_json:
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

            results.append(
                ReviewFinding(
                    file_path=item.get("file_path", "unknown"),
                    line_number=item.get("line_number"),
                    rule_id=item.get("rule_id", "OPENAI01"),
                    category=cat,
                    severity=sev,
                    message=item.get("message", "Issue detected"),
                    suggestion=item.get("suggestion"),
                    confidence=float(item.get("confidence", 0.9)),
                )
            )

        return results

    def review_diff(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Review diffs using OpenAI / Gemini endpoint."""
        if not file_diffs:
            return []

        diff_text = self.format_diff_for_prompt(file_diffs)
        user_prompt = f"Review the following code changes:\n\n{diff_text}"

        try:
            raw_response = self._call_chat_completions(user_prompt)
            return self.parse_findings(raw_response)
        except Exception as e:
            return [
                ReviewFinding(
                    file_path=file_diffs[0].target_path if file_diffs else "general",
                    rule_id="SYS_OPENAI_ERR",
                    category=FindingCategory.BUG,
                    severity=FindingSeverity.INFO,
                    message=f"OpenAI review call failed: {e}",
                    confidence=1.0,
                )
            ]
