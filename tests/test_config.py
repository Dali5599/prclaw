"""Tests for PRClaw config loader."""

from pathlib import Path
import pytest
from prclaw.config import ConfigLoader, PRClawConfig


def test_default_config():
    cfg = ConfigLoader.load(start_dir="/tmp/non_existent_dir_xyz")
    assert cfg.provider == "ollama"
    assert cfg.model == "qwen2.5-coder:32b"
    assert cfg.min_confidence == 0.70
    assert cfg.fail_on_blocking is True


def test_load_custom_prclaw_toml(tmp_path):
    toml_content = """
provider = "anthropic"
model = "claude-3-5-sonnet"
min_confidence = 0.85
min_severity = "high"
ignored_paths = ["vendor/*", "node_modules/*"]
fail_on_blocking = false
"""
    cfg_file = tmp_path / ".prclaw.toml"
    cfg_file.write_text(toml_content, encoding="utf-8")

    loaded = ConfigLoader.load(str(tmp_path))
    assert loaded.provider == "anthropic"
    assert loaded.model == "claude-3-5-sonnet"
    assert loaded.min_confidence == 0.85
    assert loaded.min_severity == "high"
    assert loaded.ignored_paths == ["vendor/*", "node_modules/*"]
    assert loaded.fail_on_blocking is False
