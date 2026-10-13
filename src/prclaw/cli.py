"""PRClaw command line interface."""

import os
import sys
from typing import Optional
from rich.console import Console
import typer
from prclaw.config import ConfigLoader
from prclaw.formatters.sarif import SarifFormatter
from prclaw.formatters.terminal import TerminalFormatter
from prclaw.git_inspector import GitInspector
from prclaw.providers.base import ProviderConfig
from prclaw.providers.factory import ProviderFactory
from prclaw.review_engine import ReviewEngine
from prclaw.scoring import ScoringFilter

app = typer.Typer(
    name="prclaw",
    help="Fast, offline-friendly AI Code Reviewer for git diffs and Pull Requests.",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Display PRClaw version."""
    import prclaw

    console.print(f"[bold cyan]PRClaw[/bold cyan] v{prclaw.__version__} - AI Code Reviewer")


@app.command()
def diff(
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    base: Optional[str] = typer.Option(None, "--base", "-b", help="Base commit or branch to diff against"),
):
    """Inspect and display parsed git diff."""
    inspector = GitInspector(path)
    if not inspector.is_git_repo():
        console.print(f"[bold red]Error:[/bold red] '{path}' is not a valid git repository.")
        raise typer.Exit(1)

    file_diffs = inspector.inspect_diff(base)
    console.print(f"[bold green]Parsed {len(file_diffs)} changed file(s):[/bold green]")
    for f in file_diffs:
        status = "[green]NEW[/green]" if f.is_new else ("[red]DELETED[/red]" if f.is_deleted else "[yellow]MODIFIED[/yellow]")
        console.print(f"  • {f.target_path} ({len(f.hunks)} hunk(s)) {status}")


@app.command()
def review(
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    provider: Optional[str] = typer.Option(None, "--provider", help="LLM provider (ollama, anthropic, openai)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
    base: Optional[str] = typer.Option(None, "--base", "-b", help="Base git commit or branch"),
    output_format: str = typer.Option("terminal", "--format", "-f", help="Output format: terminal or sarif"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Write report to file"),
    no_llm: bool = typer.Option(False, "--no-llm", help="Run only static security and bug rules"),
):
    """Run automated code review on repository diffs."""
    cfg = ConfigLoader.load(path)
    chosen_provider = provider or cfg.provider
    chosen_model = model or cfg.model
    chosen_base = base or cfg.base_branch

    inspector = GitInspector(path)
    if not inspector.is_git_repo():
        console.print(f"[bold red]Error:[/bold red] '{path}' is not a valid git repository.")
        raise typer.Exit(1)

    file_diffs = inspector.inspect_diff(chosen_base)
    if not file_diffs:
        console.print("[bold green]No changes detected to review.[/bold green]")
        return

    llm_instance = None
    if not no_llm and cfg.enable_llm:
        p_cfg = ProviderConfig(model_name=chosen_model, base_url=cfg.base_url)
        try:
            llm_instance = ProviderFactory.create(chosen_provider, p_cfg)
        except Exception as e:
            console.print(f"[yellow]Warning: Could not initialize provider {chosen_provider}: {e}[/yellow]")

    engine = ReviewEngine(
        provider=llm_instance,
        enable_static_rules=cfg.enable_static_rules,
        enable_llm=(not no_llm and cfg.enable_llm),
    )
    raw_summary = engine.review(file_diffs)

    # Score and filter findings
    scorer = ScoringFilter(min_confidence=cfg.min_confidence)
    raw_summary.findings = scorer.filter_findings(raw_summary.findings)
    raw_summary.total_findings = len(raw_summary.findings)
    raw_summary.has_blocking_issues = any(f.is_blocking for f in raw_summary.findings)

    # Format output
    if output_format.lower() == "sarif":
        sarif_fmt = SarifFormatter()
        rendered = sarif_fmt.render_json(raw_summary)
    else:
        term_fmt = TerminalFormatter(console)
        rendered = term_fmt.render_to_string(raw_summary)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rendered)
        console.print(f"[green]Report saved to {output_file}[/green]")
    else:
        console.print(rendered)

    if cfg.fail_on_blocking and raw_summary.has_blocking_issues:
        console.print("[bold red]Quality Gate Failed: Blocking issues found.[/bold red]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
