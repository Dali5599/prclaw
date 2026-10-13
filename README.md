# 🦅 PRClaw - AI Code Reviewer for Developers & CI

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> **Fast, offline-friendly AI code reviewer for git diffs and pull requests.**  
> Zero cloud lock-in. Works directly with your local **Ollama** (`qwen2.5-coder`, `deepseek-r1`), **Claude 3.5**, or **Gemini**.  
> Runs as a single CLI command locally or as a **GitHub Action** in your CI pipeline.

---

## ⚡ Why PRClaw?

- 🔒 **Zero Data Leakage** : Review sensitive code locally using Ollama (`qwen2.5-coder:32b`, `llama3.3`).
- 🎯 **Line-Accurate Feedback** : Flags bugs, security vulnerabilities (OWASP top 10), performance regressions and missing tests with precise file and line numbers.
- ⚡ **Lightning Fast Diff Parsing** : Unified git diff engine with hunk header calculation, token-aware context truncation, and multi-language support.
- 🤖 **GitHub PR Comments** : Automatically post markdown reviews and inline review comments on GitHub Pull Requests.
- 🚦 **CI Quality Gate** : Block pull requests (`exit 1`) if high-severity security issues or critical regressions are detected.

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Dali5599/prclaw.git
cd prclaw
pip install -e .
```

### Review your local changes

```bash
# Review uncommitted changes (git diff) using Ollama locally
prclaw review --provider ollama --model qwen2.5-coder:32b

# Review a branch compared to main using Claude 3.5 Sonnet
prclaw review --base main --provider anthropic

# Output as SARIF for GitHub Security tab
prclaw review --format sarif --output results.sarif
```

---

## 🗺️ Roadmap (4 Phases to Production)

See [`ROADMAP.md`](ROADMAP.md) for detailed tasks and live completion status.

---

## 📜 License

MIT License © 2026 Dali5599 & Requin.
