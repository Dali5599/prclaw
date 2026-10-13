"""Language Detection and Syntax Filter for PRClaw."""

from pathlib import Path
from typing import Dict, Optional, Set

EXTENSION_LANGUAGE_MAP: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".sql": "sql",
    ".sh": "bash",
    ".bash": "bash",
    ".html": "html",
    ".css": "css",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
}

IGNORED_EXTENSIONS: Set[str] = {
    ".lock",
    ".svg",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".exe",
    ".bin",
    ".pyc",
    ".min.js",
    ".min.css",
}


class LanguageDetector:
    """Identifies programming languages and filters reviewable source files."""

    @staticmethod
    def detect_language(file_path: str) -> Optional[str]:
        """Detect language from file path extension."""
        p = Path(file_path)
        name_lower = p.name.lower()

        # Handle compound extensions
        if name_lower.endswith(".min.js"):
            return "javascript"
        if name_lower.endswith(".min.css"):
            return "css"

        ext = p.suffix.lower()
        return EXTENSION_LANGUAGE_MAP.get(ext)

    @staticmethod
    def is_reviewable(file_path: str) -> bool:
        """Determine if file should be processed by AI code review."""
        p = Path(file_path)
        name_lower = p.name.lower()

        for ignored in IGNORED_EXTENSIONS:
            if name_lower.endswith(ignored):
                return False

        # Ignore dotfiles / hidden configs
        if p.name.startswith(".") and not p.suffix:
            return False

        ext = p.suffix.lower()
        return ext in EXTENSION_LANGUAGE_MAP
