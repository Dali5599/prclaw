"""Test Coverage and Missing Test Detector for PRClaw."""

from typing import List, Set
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding


class TestCoverageDetector:
    """Detects when core business logic files are modified without corresponding test changes."""

    def __init__(self, min_added_lines_threshold: int = 15):
        self.min_added_lines_threshold = min_added_lines_threshold

    def is_source_file(self, path: str) -> bool:
        """Identify if file is substantive source code."""
        p_lower = path.lower()
        if p_lower.startswith("tests/") or "test" in p_lower:
            return False
        if p_lower.endswith((".py", ".ts", ".tsx", ".js", ".go", ".rs", ".java")):
            return True
        return False

    def is_test_file(self, path: str) -> bool:
        """Identify if file is an automated test."""
        p_lower = path.lower()
        return (
            p_lower.startswith("tests/")
            or p_lower.startswith("test/")
            or "test_" in p_lower
            or "_test." in p_lower
            or ".spec." in p_lower
            or ".test." in p_lower
        )

    def evaluate_diffs(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Verify that significant source changes are accompanied by test changes."""
        source_files_with_changes: Set[str] = set()
        has_any_test_changes = False

        for f in file_diffs:
            target = f.target_path
            if self.is_test_file(target):
                has_any_test_changes = True
                continue

            if self.is_source_file(target):
                added_lines_count = sum(len(h.added_lines) for h in f.hunks)
                if added_lines_count >= self.min_added_lines_threshold:
                    source_files_with_changes.add(target)

        findings: List[ReviewFinding] = []
        if source_files_with_changes and not has_any_test_changes:
            for src_path in sorted(source_files_with_changes):
                findings.append(
                    ReviewFinding(
                        file_path=src_path,
                        rule_id="TEST_MISSING_COVERAGE",
                        category=FindingCategory.TEST,
                        severity=FindingSeverity.MEDIUM,
                        message=(
                            f"File '{src_path}' contains substantial new code but the pull request "
                            "includes no corresponding test modifications."
                        ),
                        suggestion="Add automated unit or integration tests in tests/ to verify new logic.",
                        confidence=0.85,
                    )
                )

        return findings
