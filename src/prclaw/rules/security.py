"""Security Rules Evaluator for PRClaw."""

import re
from typing import List, Pattern, Tuple
from prclaw.diff_parser import FileDiff
from prclaw.models import FindingCategory, FindingSeverity, ReviewFinding

SECRET_PATTERNS: List[Tuple[str, Pattern, str]] = [
    (
        "SEC_HARDCODED_JWT",
        re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
        "Hardcoded JSON Web Token (JWT) detected",
    ),
    (
        "SEC_GENERIC_API_KEY",
        re.compile(r"(?i)(?:api_key|apikey|secret_key|secret|password|access_token)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]"),
        "Hardcoded API key or credential secret detected",
    ),
    (
        "SEC_AWS_KEY",
        re.compile(r"(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}"),
        "AWS Access Key ID detected",
    ),
    (
        "SEC_SSH_PRIVATE_KEY",
        re.compile(r"-----BEGIN (?:RSA|OPENSSH|DSA|EC) PRIVATE KEY-----"),
        "SSH/RSA Private Key exposed in diff",
    ),
]

INJECTION_PATTERNS: List[Tuple[str, Pattern, str]] = [
    (
        "SEC_RAW_SQL_FORMAT",
        re.compile(r"(?i)(?:execute|cursor\.execute)\s*\(\s*(?:f['\"]|['\"].*?%s|['\"].*?\.format\()"),
        "Potential SQL Injection: dynamic formatted query passed to database execute",
    ),
    (
        "SEC_SHELL_INJECTION",
        re.compile(r"(?i)(?:os\.system|subprocess\.call|subprocess\.Popen)\s*\(\s*(?:f['\"]|.*?shell\s*=\s*True)"),
        "Potential Command Injection: subprocess call with shell=True or formatted input",
    ),
    (
        "SEC_INSECURE_EVAL",
        re.compile(r"(?i)\b(?:eval|exec)\s*\("),
        "Insecure code execution via eval/exec",
    ),
]


class SecurityRulesEvaluator:
    """Static rule analyzer that checks diffs for high-severity security issues."""

    def evaluate_file(self, file_diff: FileDiff) -> List[ReviewFinding]:
        """Scan all added lines in a file diff against security rules."""
        findings: List[ReviewFinding] = []

        for hunk in file_diff.hunks:
            current_line_no = hunk.new_start
            for line in hunk.lines:
                if line.startswith("+") and not line.startswith("+++"):
                    added_text = line[1:].strip()

                    # 1. Check secrets
                    for rule_id, pattern, desc in SECRET_PATTERNS:
                        if pattern.search(added_text):
                            findings.append(
                                ReviewFinding(
                                    file_path=file_diff.target_path,
                                    line_number=current_line_no,
                                    rule_id=rule_id,
                                    category=FindingCategory.SECURITY,
                                    severity=FindingSeverity.CRITICAL,
                                    message=desc,
                                    suggestion="Load sensitive secrets from environment variables (e.g. os.getenv) or secret managers.",
                                    confidence=0.98,
                                )
                            )

                    # 2. Check injections
                    for rule_id, pattern, desc in INJECTION_PATTERNS:
                        if pattern.search(added_text):
                            findings.append(
                                ReviewFinding(
                                    file_path=file_diff.target_path,
                                    line_number=current_line_no,
                                    rule_id=rule_id,
                                    category=FindingCategory.SECURITY,
                                    severity=FindingSeverity.HIGH,
                                    message=desc,
                                    suggestion="Use parameterized queries or shlex.split with shell=False.",
                                    confidence=0.92,
                                )
                            )

                    current_line_no += 1
                elif not line.startswith("-"):
                    current_line_no += 1

        return findings

    def evaluate_diffs(self, file_diffs: List[FileDiff]) -> List[ReviewFinding]:
        """Scan a full list of file diffs."""
        all_findings = []
        for f in file_diffs:
            all_findings.extend(self.evaluate_file(f))
        return all_findings
