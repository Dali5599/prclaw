"""GitHub PR Comments API Client for PRClaw."""

import os
from typing import List, Optional
import httpx
from prclaw.models import ReviewFinding, ReviewSummary


class GitHubClient:
    """Interacts with GitHub REST API to post review comments on Pull Requests."""

    DEFAULT_API_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None, base_url: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = (base_url or self.DEFAULT_API_URL).rstrip("/")

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def format_pr_summary_markdown(self, summary: ReviewSummary) -> str:
        """Create high-level markdown comment for a PR."""
        status_badge = "🚨 **BLOCKING ISSUES DETECTED**" if summary.has_blocking_issues else "✅ **ALL QUALITY CHECKS PASSED**"
        lines = [
            f"## 🦅 PRClaw Review Report",
            f"",
            f"{status_badge}",
            f"",
            f"- **Files Reviewed:** {summary.total_files_reviewed}",
            f"- **Total Findings:** {summary.total_findings}",
            f"- **Analysis Time:** {summary.execution_time_seconds:.2f}s",
            f"",
        ]

        if summary.findings:
            lines.append("### Findings Details:")
            for f in summary.findings:
                loc = f"`{f.file_path}`" + (f":{f.line_number}" if f.line_number else "")
                lines.append(f"- **[{f.severity.upper()}]** {loc} - {f.message}")
                if f.suggestion:
                    lines.append(f"  > *Suggestion:* `{f.suggestion}`")
        else:
            lines.append("🎉 Clean code! No security risks or bugs detected.")

        return "\n".join(lines)

    def post_issue_comment(self, repo: str, pull_number: int, body: str) -> dict:
        """Post general comment on pull request issue thread."""
        url = f"{self.base_url}/repos/{repo}/issues/{pull_number}/comments"
        with httpx.Client(headers=self.headers, timeout=30) as client:
            resp = client.post(url, json={"body": body})
            resp.raise_for_status()
            return resp.json()

    def post_review(self, repo: str, pull_number: int, commit_id: str, summary: ReviewSummary) -> dict:
        """Submit a formal Pull Request review with comments."""
        event = "REQUEST_CHANGES" if summary.has_blocking_issues else "COMMENT"
        body = self.format_pr_summary_markdown(summary)

        url = f"{self.base_url}/repos/{repo}/pulls/{pull_number}/reviews"
        payload = {
            "commit_id": commit_id,
            "body": body,
            "event": event,
            "comments": [],
        }

        with httpx.Client(headers=self.headers, timeout=30) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
