"""Tests for complete PRClaw CLI commands."""

from typer.testing import CliRunner
import pytest
from prclaw.cli import app

runner = CliRunner()


def test_cli_version_command():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "PRClaw" in res.stdout
    assert "AI Code Reviewer" in res.stdout


def test_cli_diff_non_repo(tmp_path):
    res = runner.invoke(app, ["diff", "--path", str(tmp_path)])
    assert res.exit_code == 1
    assert "not a valid" in res.stdout
    assert "git repository" in res.stdout


def test_cli_review_clean_help():
    res = runner.invoke(app, ["review", "--help"])
    assert res.exit_code == 0
    assert "--provider" in res.stdout
    assert "--format" in res.stdout
    assert "--no-llm" in res.stdout
