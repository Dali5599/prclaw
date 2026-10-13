"""Bug Pattern and Performance Rules for PRClaw."""

import re
from typing import List, Pattern, Tuple
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding

BUG_PATTERNS: List[Tuple[str, Pattern, str, str]] = [
    (
        "BUG_MUTABLE_DEFAULT_ARG",
        re.compile(r"def\s+[a-zA-Z0-9_]+\s*\([^)]*?=\s*(\[\]|\{\}|set\(\))"),
        "Mutable default argument (list/dict/set) in function definition can cause persistent state bug",
        "Use None as default value and initialize inside function body.",
    ),
    (
        "BUG_BARE_EXCEPT",
        re.compile(r"except\s*:"),
        "Bare 'except:' catches system exits and interrupts, masking critical failures",
        "Specify exact exception class (e.g. 'except Exception:' or specific subclasses).",
    ),
    (
        "BUG_RESOURCE_LEAK_OPEN",
        re.compile(r"(?i)\b(?:f|file|fp)\s*=\s*open\s*\([^)]+\)(?!\s*with)"),
        "File opened without context manager ('with' block), risking descriptor leak",
        "Use 'with open(...) as f:' pattern.",
    ),
]

PERF_PATTERNS: List[Tuple[str, Pattern, str, str]] = [
    (
        "PERF_STRING_CONCAT_LOOP",
        re.compile(r"for\s+[a-zA-Z0-9_]+\s+in\s+.*?:\s*.*?\b[a-zA-Z0-9_]+\s*\+=\s*['\"]"),
        "String concatenation in a loop has quadratic O(N^2) complexity",
        "Accumulate items in a list and use ''.join(list).",
    ),
    (
        "PERF_UNINDEXED_LINEAR_LOOKUP",
        re.compile(r"if\s+[a-zA-Z0-9_]+\s+in\s+\[.*?\]:"),
        "Linear membership check on list literal inside repetitive block",
        "Use set literal ({...}) for O(1) constant time lookups.",
    ),
]


class BugAndPerformanceRulesEvaluator:
    """Evaluates diffs for typical anti-patterns and performance bottlenecks."""

    def evaluate_file(self, file_diff: FileDiff) -> List[ReviewFinding]:
        findings: List[ReviewFinding] = []

        for hunk in file_diff.hunks:
            current_line_no = hunk.new_start
            for line in hunk.lines:
                if line.startswith("+") and not line.startswith("+++"):
                    added_text = line[1:].strip()

                    # 1. Bug patterns
                    for rule_id, pattern, desc, sugg in BUG_PATTERNS:
                        if pattern.search(added_text):
                            findings.append(
                                ReviewFinding(
                                    file_path=file_diff.target_path,
                                    line_number=current_line_no,
                                    rule_id=rule_id,
                                    category=FindingCategory.BUG,
                                    severity=FindingSeverity.MEDIUM,
                                    message=desc,
                                    suggestion=sugg,
                                    confidence=0.90,
                                )
                            )

                    # 2. Performance patterns
                    for rule_id, pattern, desc, sugg in PERF_PATTERNS:
                        if pattern.search(added_text):
                            findings.append(
                                ReviewFinding(
                                    file_path=file_diff.target_path,
                                    line_number=current_line_no,
                                    rule_id=rule_id,
                                    category=FindingCategory.PERFORMANCE,
                                    severity=FindingSeverity.LOW,
                                    message=desc,
                                    suggestion=sugg,
                                    confidence=0.88,
                                )
                            )

                    current_line_no += 1
                elif not line.startswith("-"):
                    current_line_no += 1

        return findings

    def evaluate_diffs(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        all_findings = []
        for f in file_diffs:
            all_findings.extend(self.evaluate_file(f))
        return all_findings
