from __future__ import annotations

import json
from pathlib import Path

from watchclaw.models import Finding


def scan_usage(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in _candidate_files(root):
        findings.extend(_scan_jsonl(path))
    return findings


def _candidate_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for path in root.rglob("*.jsonl"):
        lower = str(path).lower()
        if any(part in lower for part in ("session", "usage", "watchdog", "run")):
            candidates.append(path)
    return candidates


def _scan_jsonl(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings

    rate_limit_hits = 0
    high_token_line = None
    for idx, line in enumerate(lines, start=1):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = json.dumps(obj).lower()
        if "rate limit" in payload or '"429"' in payload:
            rate_limit_hits += 1
            if rate_limit_hits >= 3:
                findings.append(
                    Finding(
                        rule_id="repeated-rate-limit-events",
                        severity="medium",
                        path=path,
                        line_number=idx,
                        message="Repeated rate-limit events detected in usage/session logs.",
                        excerpt="multiple 429/rate-limit entries observed",
                        remediation="Investigate prompt/context growth, model choice, and retry policy before public-facing failures stack up.",
                    )
                )
        total_tokens = _extract_total_tokens(obj)
        if total_tokens and total_tokens >= 30000 and high_token_line is None:
            high_token_line = (idx, total_tokens)
    if high_token_line is not None:
        idx, total_tokens = high_token_line
        findings.append(
            Finding(
                rule_id="high-token-turn",
                severity="medium",
                path=path,
                line_number=idx,
                message="Large single-turn token usage detected.",
                excerpt=f"totalTokens={total_tokens}",
                remediation="Trim carried context or move heavy reasoning into smaller delegated runs to reduce token pressure.",
            )
        )
    return findings


def _extract_total_tokens(obj: object) -> int | None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in {"totalTokens", "total_tokens"} and isinstance(value, int):
                return value
            nested = _extract_total_tokens(value)
            if nested is not None:
                return nested
    elif isinstance(obj, list):
        for item in obj:
            nested = _extract_total_tokens(item)
            if nested is not None:
                return nested
    return None
