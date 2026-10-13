"""Rule Models and Review Finding Types for PRClaw."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class FindingSeverity(str, Enum):
    """Severity levels for findings."""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FindingCategory(str, Enum):
    """Categories for review findings."""
    SECURITY = "security"
    BUG = "bug"
    PERFORMANCE = "performance"
    STYLE = "style"
    TEST = "test"


class ReviewFinding(BaseModel):
    """Represents a specific code review finding/comment."""

    file_path: str = Field(..., description="Path to the reviewed file")
    line_number: Optional[int] = Field(None, description="Target line number in the diff/file")
    rule_id: str = Field(..., description="Unique identifier for the triggered rule")
    category: FindingCategory = Field(FindingCategory.BUG, description="Category of the finding")
    severity: FindingSeverity = Field(FindingSeverity.MEDIUM, description="Severity of the issue")
    message: str = Field(..., description="Human-readable explanation of the issue")
    suggestion: Optional[str] = Field(None, description="Suggested replacement or fix code")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")

    @property
    def is_blocking(self) -> bool:
        """Check if finding should block the CI quality gate."""
        return self.severity in (FindingSeverity.HIGH, FindingSeverity.CRITICAL)


class ReviewSummary(BaseModel):
    """Aggregated summary of an entire PRClaw review run."""

    total_files_reviewed: int = 0
    total_findings: int = 0
    findings: List[ReviewFinding] = Field(default_factory=list)
    has_blocking_issues: bool = False
    execution_time_seconds: float = 0.0

    def add_finding(self, finding: ReviewFinding) -> None:
        """Append a finding and update summary states."""
        self.findings.append(finding)
        self.total_findings = len(self.findings)
        if finding.is_blocking:
            self.has_blocking_issues = True
