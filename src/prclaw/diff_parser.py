"""Diff Parser and Hunk Models for PRClaw."""

import re
from typing import List, Optional
from pydantic import BaseModel, Field


class DiffHunk(BaseModel):
    """Represents a single unified diff hunk @@ -x,y +a,b @@."""

    old_start: int = Field(..., description="Starting line in the old file")
    old_lines: int = Field(1, description="Number of lines in the old hunk")
    new_start: int = Field(..., description="Starting line in the new file")
    new_lines: int = Field(1, description="Number of lines in the new hunk")
    header: str = Field(..., description="Full hunk header line")
    lines: List[str] = Field(default_factory=list, description="Raw lines inside this hunk")

    @property
    def added_lines(self) -> List[str]:
        """Lines added in this hunk (+)."""
        return [l[1:] for l in self.lines if l.startswith("+") and not l.startswith("+++")]

    @property
    def removed_lines(self) -> List[str]:
        """Lines removed in this hunk (-)."""
        return [l[1:] for l in self.lines if l.startswith("-") and not l.startswith("---")]


class FileDiff(BaseModel):
    """Represents changes to a single file in a git diff."""

    old_path: Optional[str] = None
    new_path: Optional[str] = None
    is_new: bool = False
    is_deleted: bool = False
    is_binary: bool = False
    hunks: List[DiffHunk] = Field(default_factory=list)

    @property
    def target_path(self) -> str:
        """Get valid current file path."""
        return self.new_path or self.old_path or "unknown"


HUNK_HEADER_RE = re.compile(
    r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@(.*)$"
)


def parse_unified_diff(diff_text: str) -> List[FileDiff]:
    """Parse a full git unified diff into structured FileDiff models."""
    if not diff_text or not diff_text.strip():
        return []

    files: List[FileDiff] = []
    current_file: Optional[FileDiff] = None
    current_hunk: Optional[DiffHunk] = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            if current_hunk and current_file:
                current_file.hunks.append(current_hunk)
                current_hunk = None
            if current_file:
                files.append(current_file)

            parts = line.split()
            old_p = parts[2][2:] if len(parts) > 2 and parts[2].startswith("a/") else None
            new_p = parts[3][2:] if len(parts) > 3 and parts[3].startswith("b/") else None
            current_file = FileDiff(old_path=old_p, new_path=new_p)

        elif line.startswith("new file mode"):
            if current_file:
                current_file.is_new = True

        elif line.startswith("deleted file mode"):
            if current_file:
                current_file.is_deleted = True

        elif line.startswith("Binary files "):
            if current_file:
                current_file.is_binary = True

        elif line.startswith("@@"):
            if current_hunk and current_file:
                current_file.hunks.append(current_hunk)
                current_hunk = None

            m = HUNK_HEADER_RE.match(line)
            if m:
                o_start = int(m.group(1))
                o_lines = int(m.group(2)) if m.group(2) else 1
                n_start = int(m.group(3))
                n_lines = int(m.group(4)) if m.group(4) else 1
                current_hunk = DiffHunk(
                    old_start=o_start,
                    old_lines=o_lines,
                    new_start=n_start,
                    new_lines=n_lines,
                    header=line,
                    lines=[],
                )
        elif current_hunk is not None:
            current_hunk.lines.append(line)

    if current_hunk and current_file:
        current_file.hunks.append(current_hunk)
    if current_file:
        files.append(current_file)

    return files
