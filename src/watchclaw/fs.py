"""Shared filesystem-filter rules for WatchClaw scanners.

Two concepts:

- ``is_ignored``: vendor / build / extremely-transient paths that no scanner
  should ever read. Things like .git, node_modules, build/, .pytest_cache.
  Safe to skip universally.

- ``is_transcript``: paths that contain raw chat / per-agent runtime state
  (OpenClaw ``agents/<name>/sessions/``, ``memory/``, ``logs/``, gateway
  ``state/``). These legitimately contain IPs, curl snippets, javascript:
  URIs, giant turn-token counts, and rate-limit discussions as *content* —
  not as security issues. Docs, workflow, and token rules should skip them
  to avoid drowning a first-run scan in noise. Usage rules keep scanning
  them, because compaction pressure and rate-limit signals genuinely live
  there.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_IGNORE_DIR_NAMES = frozenset({
    '.git',
    '.hg',
    '.svn',
    'node_modules',
    '__pycache__',
    '.venv',
    'venv',
    '.mypy_cache',
    '.pytest_cache',
    '.ruff_cache',
    'dist',
    'build',
    '.tox',
    '.eggs',
    '.next',
    '.cache',
    'tmp',
})

TRANSCRIPT_PATH_SEGMENTS = (
    '/sessions/',
    '/memory/',
    '/logs/',
    '/cron/runs/',
    '/state/',
    '/checkpoint/',
)


def is_ignored(path: Path, root: Path | None = None) -> bool:
    """Return True if *path* is inside a vendor/build/cache directory.

    When *root* is provided, only directories under the scan root are
    considered — this avoids false positives when the user's checkout
    lives under an ancestor named something like ``tmp`` (for example,
    the common macOS case where ``/tmp`` resolves to ``/private/tmp``,
    giving every scanned path a ``tmp`` ancestor it does not own).
    """
    if root is not None:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        parts = rel.parts
    else:
        parts = path.parts
    return bool(set(parts) & DEFAULT_IGNORE_DIR_NAMES)


def is_transcript(path: Path, root: Path | None = None) -> bool:
    """Path is inside OpenClaw (or generic) runtime/chat state.

    Docs, workflow, and token rules skip these to avoid treating chat
    content as security signal. Usage rules keep reading them because
    rate-limit and compaction markers legitimately live here.

    When *root* is provided, only segments inside the scan root count
    (so a ``root`` that happens to sit under an ancestor named
    ``sessions`` is not accidentally flagged).
    """
    if root is not None:
        try:
            rel = path.relative_to(root)
        except ValueError:
            rel = path
        normalized = '/' + str(rel).replace('\\', '/').lstrip('/')
    else:
        normalized = '/' + str(path).replace('\\', '/').lstrip('/')
    return any(seg in normalized for seg in TRANSCRIPT_PATH_SEGMENTS)
