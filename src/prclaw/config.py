"""Config File (.prclaw.toml) Loader for PRClaw."""

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


class PRClawConfig(BaseModel):
    """PRClaw user and repository configuration model."""

    provider: str = Field("ollama", description="Default LLM provider")
    model: str = Field("qwen2.5-coder:32b", description="Model identifier")
    base_url: Optional[str] = Field(None, description="API base url")
    base_branch: str = Field("main", description="Target base branch for diff comparisons")
    min_confidence: float = Field(0.70, description="Minimum confidence cutoff")
    min_severity: str = Field("low", description="Minimum severity cutoff")
    enable_static_rules: bool = Field(True, description="Enable deterministic security and bug rules")
    enable_llm: bool = Field(True, description="Enable AI LLM semantic review")
    ignored_paths: List[str] = Field(default_factory=list, description="Paths to exclude from review")
    fail_on_blocking: bool = Field(True, description="Return exit code 1 if blocking issues found")


class ConfigLoader:
    """Discovers and loads .prclaw.toml files."""

    CONFIG_FILE_NAME = ".prclaw.toml"

    @classmethod
    def load(cls, start_dir: str = ".") -> PRClawConfig:
        """Search up directory tree for .prclaw.toml, or return defaults."""
        curr = Path(start_dir).resolve()
        config_path = None

        for directory in [curr] + list(curr.parents):
            candidate = directory / cls.CONFIG_FILE_NAME
            if candidate.is_file():
                config_path = candidate
                break

        if not config_path:
            return PRClawConfig()

        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            # Flatten potential [tool.prclaw] or [prclaw] sections
            section = data.get("prclaw") or data.get("tool", {}).get("prclaw") or data
            return PRClawConfig(**section)
        except Exception:
            return PRClawConfig()
