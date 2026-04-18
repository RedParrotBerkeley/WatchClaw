from __future__ import annotations

from pathlib import Path

OPENCLAW_SENTINELS = (
    "openclaw.json",
    "docs",
    "scripts",
    "packages",
)


def detect_repo_root(start: Path) -> Path:
    start = start.resolve()
    candidates = [start, *start.parents]
    for candidate in candidates:
        if (candidate / ".git").exists():
            return candidate
        if any((candidate / sentinel).exists() for sentinel in OPENCLAW_SENTINELS):
            return candidate
    return start
