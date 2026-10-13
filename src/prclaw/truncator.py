"""Diff Context Truncator and Token Budgeter for PRClaw."""

from typing import List, Tuple
from prclaw.diff_parser import FileDiff, DiffHunk


class TokenBudgeter:
    """Estimates token counts and truncates large diffs to fit context windows."""

    CHARS_PER_TOKEN = 4.0

    def __init__(self, max_tokens: int = 12000):
        self.max_tokens = max_tokens
        self.max_chars = int(max_tokens * self.CHARS_PER_TOKEN)

    def estimate_tokens(self, text: str) -> int:
        """Rough heuristic token count based on character length."""
        if not text:
            return 0
        return int(len(text) / self.CHARS_PER_TOKEN) + 1

    def truncate_hunk_lines(self, lines: List[str], max_lines: int = 80) -> Tuple[List[str], bool]:
        """Limit number of lines inside a single hunk if overly large."""
        if len(lines) <= max_lines:
            return lines, False

        half = max_lines // 2
        omitted = len(lines) - max_lines
        truncated = (
            lines[:half]
            + [f"... ({omitted} lines omitted by PRClaw budgeter) ..."]
            + lines[-half:]
        )
        return truncated, True

    def truncate_diffs(self, file_diffs: List[FileDiff]) -> Tuple[List[FileDiff], bool]:
        """Ensure total diff representation stays within token budget."""
        total_chars = 0
        budgeted_files: List[FileDiff] = []
        truncated_overall = False

        for f in file_diffs:
            file_hunks: List[DiffHunk] = []
            for h in f.hunks:
                hunk_text = "\n".join(h.lines)
                if total_chars + len(hunk_text) > self.max_chars:
                    truncated_overall = True
                    # Add truncation marker hunk
                    marker_hunk = DiffHunk(
                        old_start=h.old_start,
                        new_start=h.new_start,
                        header="@@ ... @@",
                        lines=["+ ... [PRClaw Token Budget Reached: Remaining Diff Truncated] ..."],
                    )
                    file_hunks.append(marker_hunk)
                    break
                else:
                    lines, was_trunc = self.truncate_hunk_lines(h.lines)
                    if was_trunc:
                        truncated_overall = True
                    new_h = DiffHunk(
                        old_start=h.old_start,
                        old_lines=h.old_lines,
                        new_start=h.new_start,
                        new_lines=h.new_lines,
                        header=h.header,
                        lines=lines,
                    )
                    file_hunks.append(new_h)
                    total_chars += len("\n".join(lines))

            budgeted_files.append(
                FileDiff(
                    old_path=f.old_path,
                    new_path=f.new_path,
                    is_new=f.is_new,
                    is_deleted=f.is_deleted,
                    is_binary=f.is_binary,
                    hunks=file_hunks,
                )
            )

            if truncated_overall and total_chars >= self.max_chars:
                break

        return budgeted_files, truncated_overall
