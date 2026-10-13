"""Confidence Scoring and Severity Filtering for PRClaw."""

from typing import List, Optional
from prclaw.models import FindingSeverity, ReviewFinding, ReviewSummary


class ScoringFilter:
    """Filters and re-scores findings based on confidence threshold and severity levels."""

    SEVERITY_ORDER = {
        FindingSeverity.INFO: 0,
        FindingSeverity.LOW: 1,
        FindingSeverity.MEDIUM: 2,
        FindingSeverity.HIGH: 3,
        FindingSeverity.CRITICAL: 4,
    }

    def __init__(
        self,
        min_confidence: float = 0.70,
        min_severity: FindingSeverity = FindingSeverity.LOW,
    ):
        self.min_confidence = min_confidence
        self.min_severity = min_severity

    def should_keep(self, finding: ReviewFinding) -> bool:
        """Evaluate if finding passes severity and confidence cutoffs."""
        if finding.confidence < self.min_confidence:
            return False

        current_rank = self.SEVERITY_ORDER.get(finding.severity, 0)
        min_rank = self.SEVERITY_ORDER.get(self.min_severity, 0)
        return current_rank >= min_rank

    def filter_findings(self, findings: List[ReviewFinding]) -> List[ReviewFinding]:
        """Filter a list of findings."""
        return [f for f in findings if self.should_keep(f)]

    def compute_health_score(self, summary: ReviewSummary) -> int:
        """Compute an overall codebase health score (0 to 100) based on review findings."""
        base_score = 100

        for f in summary.findings:
            if f.severity == FindingSeverity.CRITICAL:
                base_score -= 35
            elif f.severity == FindingSeverity.HIGH:
                base_score -= 15
            elif f.severity == FindingSeverity.MEDIUM:
                base_score -= 5
            elif f.severity == FindingSeverity.LOW:
                base_score -= 2

        return max(0, min(100, base_score))
