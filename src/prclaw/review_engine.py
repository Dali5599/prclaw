"""Comprehensive Review Engine for PRClaw."""

import time
from typing import List, Optional
from prclaw.diff_parser import FileDiff
from prclaw.languages import LanguageDetector
from prclaw.models import ReviewFinding, ReviewSummary
from prclaw.providers.base import BaseLLMProvider
from prclaw.rules.bugs import BugAndPerformanceRulesEvaluator
from prclaw.rules.security import SecurityRulesEvaluator
from prclaw.rules.tests import TestCoverageDetector
from prclaw.truncator import TokenBudgeter


class ReviewEngine:
    """Orchestrates multi-phase review: static rule scanning, LLM inspection, and aggregation."""

    def __init__(
        self,
        provider: Optional[BaseLLMProvider] = None,
        enable_static_rules: bool = True,
        enable_llm: bool = True,
        max_tokens: int = 10000,
    ):
        self.provider = provider
        self.enable_static_rules = enable_static_rules
        self.enable_llm = enable_llm
        self.budgeter = TokenBudgeter(max_tokens=max_tokens)
        self.security_evaluator = SecurityRulesEvaluator()
        self.bug_evaluator = BugAndPerformanceRulesEvaluator()
        self.test_detector = TestCoverageDetector()

    def filter_reviewable_files(self, file_diffs: List[FileDiff]) -> List[FileDiff]:
        """Filter out binary and non-reviewable files."""
        return [
            f for f in file_diffs
            if not f.is_binary and LanguageDetector.is_reviewable(f.target_path)
        ]

    def review(self, file_diffs: List[FileDiff]) -> ReviewSummary:
        """Run complete review pipeline on incoming diffs."""
        t0 = time.time()
        reviewable = self.filter_reviewable_files(file_diffs)
        summary = ReviewSummary(total_files_reviewed=len(reviewable))

        if not reviewable:
            summary.execution_time_seconds = time.time() - t0
            return summary

        # 1. Static deterministic rule checks
        if self.enable_static_rules:
            sec_findings = self.security_evaluator.evaluate_diffs(reviewable)
            for f in sec_findings:
                summary.add_finding(f)

            bug_findings = self.bug_evaluator.evaluate_diffs(reviewable)
            for f in bug_findings:
                summary.add_finding(f)

            test_findings = self.test_detector.evaluate_diffs(reviewable)
            for f in test_findings:
                summary.add_finding(f)

        # 2. LLM semantic review
        if self.enable_llm and self.provider:
            budgeted_diffs, _ = self.budgeter.truncate_diffs(reviewable)
            llm_findings = self.provider.review_diff(budgeted_diffs)
            for f in llm_findings:
                summary.add_finding(f)

        summary.execution_time_seconds = round(time.time() - t0, 3)
        return summary
