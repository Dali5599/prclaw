"""Basic smoke test for PRClaw package initialization."""

import prclaw
from prclaw import cli


def test_prclaw_version():
    assert prclaw.__version__ == "0.1.0"
    assert isinstance(prclaw.__version__, str)


def test_cli_app_defined():
    assert cli.app is not None
    assert cli.app.info.name == "prclaw"
