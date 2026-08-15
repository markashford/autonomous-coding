"""
Runtime settings and argument defaults.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _int_from_env(name: str, default: int, min_value: int = 1) -> int:
    """Read an integer environment variable with safe fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default

    try:
        value = int(raw)
    except ValueError:
        return default

    if value < min_value:
        return default

    return value


@dataclass(frozen=True)
class AppSettings:
    """App-level defaults loaded from environment variables."""

    default_model: str
    auto_continue_delay_seconds: int
    max_turns: int
    generations_root: Path


def load_settings() -> AppSettings:
    """Load runtime settings from environment variables."""
    return AppSettings(
        default_model=os.getenv(
            "AUTONOMOUS_DEFAULT_MODEL", "claude-sonnet-4-5-20250929"
        ),
        auto_continue_delay_seconds=_int_from_env(
            "AUTONOMOUS_AUTO_CONTINUE_DELAY_SECONDS", 3
        ),
        max_turns=_int_from_env("AUTONOMOUS_MAX_TURNS", 1000),
        generations_root=Path(os.getenv("AUTONOMOUS_GENERATIONS_DIR", "generations")),
    )


def resolve_project_dir(project_dir: Path, generations_root: Path) -> Path:
    """
    Normalize project path.

    Relative paths are placed under generations_root unless they already start
    with the generations root prefix.
    """
    if project_dir.is_absolute():
        return project_dir

    project_parts = project_dir.parts
    root_parts = generations_root.parts

    if project_parts[: len(root_parts)] == root_parts:
        return project_dir

    return generations_root / project_dir
