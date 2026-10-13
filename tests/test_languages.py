"""Tests for PRClaw language detector module."""

import pytest
from prclaw.languages import LanguageDetector


def test_detect_language():
    assert LanguageDetector.detect_language("src/main.py") == "python"
    assert LanguageDetector.detect_language("web/app.tsx") == "typescript"
    assert LanguageDetector.detect_language("server/main.go") == "go"
    assert LanguageDetector.detect_language("config.toml") == "toml"
    assert LanguageDetector.detect_language("unknown.xyz123") is None


def test_is_reviewable():
    assert LanguageDetector.is_reviewable("src/auth.py") is True
    assert LanguageDetector.is_reviewable("assets/logo.png") is False
    assert LanguageDetector.is_reviewable("package-lock.json") is True
    assert LanguageDetector.is_reviewable("yarn.lock") is False
    assert LanguageDetector.is_reviewable("dist/bundle.min.js") is False
    assert LanguageDetector.is_reviewable(".gitignore") is False
