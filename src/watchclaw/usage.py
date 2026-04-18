from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from watchclaw.models import Finding

HIGH_TOKEN_THRESHOLD = 30000
RATE_LIMIT_THRESHOLD = 3
CONTEXT_DIAG_MARKERS = ('context-overflow-diag', 'compaction-diag')


def scan_usage(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _candidate_files(root):
        findings.extend(_scan_jsonl(path))
    return findings


def _candidate_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob('*.jsonl'):
        lower = str(path).lower()
        if any(part in lower for part in ('session', 'usage', 'watchdog', 'run')):
            candidates.append(path)
    return candidates


def _scan_jsonl(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except UnicodeDecodeError:
        return findings

    rate_limit_hits = 0
    highest_token: tuple[int, int] | None = None
    context_diag_line: int | None = None
    for idx, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if _is_rate_limit_event(obj):
            rate_limit_hits += 1
            if rate_limit_hits == RATE_LIMIT_THRESHOLD:
                findings.append(
                    Finding(
                        rule_id='repeated-rate-limit-events',
                        severity='medium',
                        path=path,
                        line_number=idx,
                        message='Repeated rate-limit events detected in usage/session logs.',
                        excerpt='multiple 429/rate-limit entries observed',
                        remediation='Investigate prompt/context growth, model choice, and retry policy before public-facing failures stack up.',
                    )
                )
        total_tokens = _extract_max_total_tokens(obj)
        if total_tokens is not None and total_tokens >= HIGH_TOKEN_THRESHOLD:
            if highest_token is None or total_tokens > highest_token[1]:
                highest_token = (idx, total_tokens)
        if context_diag_line is None and _contains_context_diag(obj):
            context_diag_line = idx

    if highest_token is not None:
        idx, total_tokens = highest_token
        findings.append(
            Finding(
                rule_id='high-token-turn',
                severity='medium',
                path=path,
                line_number=idx,
                message='Large single-turn token usage detected.',
                excerpt=f'totalTokens={total_tokens}',
                remediation='Trim carried context or move heavy reasoning into smaller delegated runs to reduce token pressure.',
            )
        )
    if context_diag_line is not None:
        findings.append(
            Finding(
                rule_id='context-compaction-pressure',
                severity='medium',
                path=path,
                line_number=context_diag_line,
                message='Context overflow or compaction diagnostics appeared in session logs.',
                excerpt='context-overflow-diag / compaction-diag marker observed',
                remediation='Investigate long-lived sessions, earlier compaction, or smaller delegated runs before cache churn becomes expensive.',
            )
        )
    return findings


def _is_rate_limit_event(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    error = obj.get('error')
    if isinstance(error, dict):
        message = str(error.get('message', '')).lower()
        code = str(error.get('code', '')).lower()
        kind = str(error.get('type', '')).lower()
        return 'rate limit' in message or code == '429' or 'rate_limit' in kind
    if isinstance(error, str):
        lowered = error.lower()
        return 'rate limit' in lowered or lowered.strip() == '429'
    status = obj.get('status')
    if isinstance(status, (int, str)) and str(status) == '429':
        return True
    message = obj.get('message')
    if isinstance(message, str) and 'rate limit' in message.lower():
        return True
    return False


def _extract_max_total_tokens(obj: Any) -> int | None:
    found: int | None = None
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in {'totalTokens', 'total_tokens'} and isinstance(value, int):
                found = value if found is None else max(found, value)
            nested = _extract_max_total_tokens(value)
            if nested is not None:
                found = nested if found is None else max(found, nested)
    elif isinstance(obj, list):
        for item in obj:
            nested = _extract_max_total_tokens(item)
            if nested is not None:
                found = nested if found is None else max(found, nested)
    return found


def _contains_context_diag(obj: Any) -> bool:
    if isinstance(obj, dict):
        return any(_contains_context_diag(value) for value in obj.values())
    if isinstance(obj, list):
        return any(_contains_context_diag(item) for item in obj)
    if isinstance(obj, str):
        lowered = obj.lower()
        return any(marker in lowered for marker in CONTEXT_DIAG_MARKERS)
    return False
