# PRClaw Roadmap & Task Tracker

## Phase 1 : Core Git Diff Engine & Data Models
- [x] 01. Implement Diff Parser and Hunk Models in src/prclaw/diff_parser.py
- [x] 02. Implement Rule Models and Review Finding Types in src/prclaw/models.py
- [x] 03. Implement Local Git Repository Inspector in src/prclaw/git_inspector.py
- [x] 04. Implement Language Detection and Syntax Filter in src/prclaw/languages.py
- [x] 05. Implement Diff Context Truncator and Token Budgeter in src/prclaw/truncator.py

## Phase 2 : LLM Provider Engines (Ollama, Anthropic, OpenAI/Gemini)
- [x] 06. Implement Base LLM Provider Protocol and Prompt Templates in src/prclaw/providers/base.py
- [x] 07. Implement Local Ollama Provider with Streaming in src/prclaw/providers/ollama_provider.py
- [x] 08. Implement Anthropic Claude Provider in src/prclaw/providers/anthropic_provider.py
- [x] 09. Implement OpenAI and Gemini Provider in src/prclaw/providers/openai_provider.py
- [ ] 10. Implement Provider Factory and Fallback Chain in src/prclaw/providers/factory.py

## Phase 3 : Review Engine, Rule Checking & Scoring
- [ ] 11. Implement Security Rules Evaluator in src/prclaw/rules/security.py
- [ ] 12. Implement Bug Pattern and Performance Rules in src/prclaw/rules/bugs.py
- [ ] 13. Implement Test Coverage and Missing Test Detector in src/prclaw/rules/tests.py
- [ ] 14. Implement Comprehensive Review Engine in src/prclaw/review_engine.py
- [ ] 15. Implement Confidence Scoring and Severity Filtering in src/prclaw/scoring.py

## Phase 4 : Formatters, GitHub Action & CLI Integration
- [ ] 16. Implement Rich Terminal Output Formatter in src/prclaw/formatters/terminal.py
- [ ] 17. Implement SARIF Formatter for GitHub Code Scanning in src/prclaw/formatters/sarif.py
- [ ] 18. Implement GitHub PR Comments API Client in src/prclaw/github_client.py
- [ ] 19. Implement Config File (.prclaw.toml) Loader in src/prclaw/config.py
- [ ] 20. Implement Full CLI Commands (review, diff, config) in src/prclaw/cli.py
