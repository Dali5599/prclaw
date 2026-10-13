"""Local Git Repository Inspector for PRClaw."""

import subprocess
from pathlib import Path
from typing import List, Optional
from prclaw.diff_parser import FileDiff, parse_unified_diff


class GitInspector:
    """Inspects a local git repository to extract diffs and file status."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()

    def _run_git(self, args: List[str]) -> str:
        """Execute a git command inside the target repo."""
        cmd = ["git"] + args
        res = subprocess.run(
            cmd,
            cwd=str(self.repo_path),
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            cmd_str = " ".join(cmd)
            raise RuntimeError(f"Git command failed ({cmd_str}): {res.stderr.strip()}")
        return res.stdout

    def is_git_repo(self) -> bool:
        """Verify if current path is a valid git repository."""
        try:
            out = self._run_git(["rev-parse", "--is-inside-work-tree"])
            return out.strip() == "true"
        except Exception:
            return False

    def get_current_branch(self) -> str:
        """Get active branch name."""
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"]).strip()

    def get_uncommitted_diff(self) -> str:
        """Get raw diff of unstaged and staged changes."""
        staged = self._run_git(["diff", "--cached"])
        unstaged = self._run_git(["diff"])
        return f"{staged}\n{unstaged}".strip()

    def get_branch_diff(self, base_branch: str = "main") -> str:
        """Get diff comparing current HEAD against base branch."""
        return self._run_git(["diff", f"{base_branch}...HEAD"])

    def inspect_diff(self, base_ref: Optional[str] = None) -> List[FileDiff]:
        """Extract and parse git diff based on reference or local changes."""
        if base_ref:
            raw_diff = self.get_branch_diff(base_ref)
        else:
            raw_diff = self.get_uncommitted_diff()
            if not raw_diff:
                raw_diff = self.get_branch_diff("HEAD~1")
        return parse_unified_diff(raw_diff)
