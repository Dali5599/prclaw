"""Base LLM Provider Protocol and Prompt Templates for PRClaw."""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from prclaw.diff_parser import FileDiff
from prclaw.models import ReviewFinding


REVIEW_SYSTEM_PROMPT = """You are PRClaw, an expert automated code reviewer.
Analyze the following unified git diff carefully.

Review goals:
1. Detect real security vulnerabilities (OWASP top 10, SQLi, secrets, injection).
2. Spot logic bugs, nil/null dereferences, memory leaks, resource mismanagement.
3. Identify severe performance bottlenecks.
4. Verify tests and edge-case handling.

Always return your findings in valid JSON format:
{
  "findings": [
    {
      "file_path": "path/to/file.py",
      "line_number": 42,
      "rule_id": "SEC001",
      "category": "security",
      "severity": "high",
      "message": "Clear explanation of the problem",
      "suggestion": "Optional fix suggestion",
      "confidence": 0.95
    }
  ]
}
"""


class ProviderConfig(BaseModel):
    """Configuration options for LLM providers."""

    model_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    timeout_seconds: int = 60


class BaseLLMProvider(ABC):
    """Abstract base interface for all PRClaw LLM review providers."""

    def __init__(self, config: ProviderConfig):
        self.config = config

    def format_diff_for_prompt(self, file_diffs: List[FileDiff]) -> str:
        """Format parsed diffs into a clean markdown diff prompt."""
        chunks = []
        for f in file_diffs:
            chunks.append(f"### File: {f.target_path}")
            for h in f.hunks:
                chunks.append(h.header)
                chunks.extend(h.lines)
        return "\n".join(chunks)

    @abstractmethod
    def review_diff(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Execute code review on diff and parse findings."""
        pass
