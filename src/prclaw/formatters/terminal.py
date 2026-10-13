"""Rich Terminal Output Formatter for PRClaw."""

from io import StringIO
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from prclaw.models import FindingSeverity, ReviewFinding, ReviewSummary


class TerminalFormatter:
    """Formats review summaries and findings into rich ANSI terminal layouts."""

    SEVERITY_COLORS = {
        FindingSeverity.INFO: "blue",
        FindingSeverity.LOW: "cyan",
        FindingSeverity.MEDIUM: "yellow",
        FindingSeverity.HIGH: "red",
        FindingSeverity.CRITICAL: "bold white on red",
    }

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()

    def format_summary_table(self, summary: ReviewSummary) -> Table:
        """Create a summary table of findings."""
        table = Table(title="🦅 PRClaw Review Summary", show_header=True, header_style="bold magenta")
        table.add_column("Severity", justify="center")
        table.add_column("Count", justify="right")

        counts = {sev: 0 for sev in FindingSeverity}
        for f in summary.findings:
            counts[f.severity] += 1

        for sev in (FindingSeverity.CRITICAL, FindingSeverity.HIGH, FindingSeverity.MEDIUM, FindingSeverity.LOW, FindingSeverity.INFO):
            color = self.SEVERITY_COLORS.get(sev, "white")
            table.add_row(f"[{color}]{sev.upper()}[/{color}]", str(counts[sev]))

        return table

    def format_finding_panel(self, finding: ReviewFinding) -> Panel:
        """Format an individual finding as an aesthetic panel."""
        color = self.SEVERITY_COLORS.get(finding.severity, "yellow")
        title = f"[{color}]{finding.severity.upper()}[/{color}] - {finding.rule_id} ({finding.category.value})"

        body_lines = [
            f"[bold]File:[/bold] {finding.file_path}" + (f":{finding.line_number}" if finding.line_number else ""),
            f"[bold]Issue:[/bold] {finding.message}",
        ]
        if finding.suggestion:
            body_lines.append(f"[bold green]Suggestion:[/bold green] {finding.suggestion}")

        return Panel("\n".join(body_lines), title=title, border_style=color.split()[-1])

    def render_to_string(self, summary: ReviewSummary) -> str:
        """Capture formatted terminal output to a string buffer."""
        buf = StringIO()
        c = Console(file=buf, force_terminal=True, width=90)
        c.print(self.format_summary_table(summary))
        for f in summary.findings:
            c.print(self.format_finding_panel(f))
        return buf.getvalue()
