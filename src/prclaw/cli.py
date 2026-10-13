"""PRClaw command line interface."""

import sys
import typer
from rich.console import Console

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

    console.print(f"[bold cyan]PRClaw[/bold cyan] v{prclaw.__version__}")


@app.command()
def review(
    path: str = typer.Option(".", "--path", "-p", help="Repository path"),
    provider: str = typer.Option("ollama", "--provider", help="LLM provider (ollama, anthropic, openai)"),
    model: str = typer.Option("qwen2.5-coder:32b", "--model", "-m", help="Model name"),
    base: str = typer.Option("HEAD~1", "--base", "-b", help="Base git commit or branch"),
):
    """Run code review on git changes."""
    console.print(f"[bold green]Starting PRClaw review[/bold green] on {path} (base={base}, provider={provider})")
    console.print("[yellow]Review engine initializing...[/yellow]")


def main():
    app()


if __name__ == "__main__":
    main()
