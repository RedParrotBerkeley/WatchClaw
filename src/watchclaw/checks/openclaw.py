from __future__ import annotations

import json
import re
from pathlib import Path

from watchclaw.fs import is_ignored
from watchclaw.models import Finding

UNSAFE_PIPE_RE = re.compile(r'\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh)\b', re.IGNORECASE)
TOOLS_ALLOW_SAFE = {'exec', 'message', 'web_search', 'web_fetch', 'lobster'}
THREAD_CREATE_CHANNEL_RE = re.compile(r'"action"\s*:\s*"thread-create"[^\n{}]*"channel"\s*:', re.IGNORECASE)
THREAD_CREATE_TARGET_RE = re.compile(r'"action"\s*:\s*"thread-create"[^\n{}]*"target"\s*:', re.IGNORECASE)
WORLD_NEWS_RE = re.compile(r'BREAKING WORLD NEWS', re.IGNORECASE)
OMIT_WORLD_NEWS_RE = re.compile(r'omit\s+BREAKING WORLD NEWS', re.IGNORECASE)


def scan_openclaw(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_scan_lobster_files(root))
    findings.extend(_scan_jobs_json(root))
    findings.extend(_scan_openclaw_json(root))
    return findings


def _scan_lobster_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob('*.lobster'):
        if is_ignored(path, root):
            continue
        try:
            lines = path.read_text(encoding='utf-8').splitlines()
        except UnicodeDecodeError:
            continue
        for idx, line in enumerate(lines, start=1):
            if _ignored(line):
                continue
            stripped = line.strip()
            lowered = stripped.lower()
            if 'command:' in lowered:
                command = stripped.split('command:', 1)[1].strip()
                if UNSAFE_PIPE_RE.search(command):
                    findings.append(Finding('lobster-remote-shell-pipe', 'high', path, idx, 'Lobster command pipes a remote download directly into a shell.', stripped, 'Split remote downloads from execution steps and verify integrity before running.'))
                if '${' in command or re.search(r'\$[A-Za-z_][A-Za-z0-9_]*', command):
                    findings.append(Finding('lobster-unrestricted-expansion', 'medium', path, idx, 'Lobster command contains direct variable expansion that deserves review.', stripped, 'Review variable expansion in command lines and prefer validated inputs or quoting for untrusted values.'))
    return findings


def _scan_jobs_json(root: Path) -> list[Finding]:
    path = root / 'cron' / 'jobs.json'
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    jobs = data.get('jobs')
    if not isinstance(jobs, list):
        return []
    findings: list[Finding] = []
    for idx, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            continue
        payload = job.get('payload')
        if not isinstance(payload, dict) or payload.get('kind') != 'agentTurn':
            continue
        excerpt = _job_excerpt(job)
        tools_allow = payload.get('toolsAllow')
        if not isinstance(tools_allow, list):
            findings.append(Finding('cron-agentturn-missing-toolsallow', 'high', path, idx, 'AgentTurn cron job is missing toolsAllow, which can lead to broader-than-intended tool access.', excerpt, 'Set an explicit toolsAllow list for each agentTurn cron job.'))
        else:
            unexpected = [tool for tool in tools_allow if isinstance(tool, str) and tool not in TOOLS_ALLOW_SAFE]
            if unexpected:
                findings.append(Finding('cron-agentturn-unreviewed-tools', 'medium', path, idx, 'AgentTurn cron job allows tools outside the reviewed default set.', excerpt, 'Review toolsAllow and keep only the minimum tools needed for the scheduled turn.'))
        if 'thinking' not in payload:
            findings.append(Finding('cron-agentturn-missing-thinking-mode', 'medium', path, idx, 'AgentTurn cron job does not pin a thinking mode, which can cause cost drift.', excerpt, 'Set thinking explicitly for scheduled jobs so model cost/behavior is predictable.'))
        message = payload.get('message')
        if isinstance(message, str):
            findings.extend(_scan_agentturn_prompt(path, idx, excerpt, message))
    return findings


def _scan_agentturn_prompt(path: Path, idx: int, excerpt: str, message: str) -> list[Finding]:
    findings: list[Finding] = []
    if THREAD_CREATE_CHANNEL_RE.search(message) and not THREAD_CREATE_TARGET_RE.search(message):
        findings.append(Finding('cron-thread-create-channel-instead-of-target', 'high', path, idx, 'AgentTurn prompt teaches thread-create with `channel` instead of `target`, which can break posting.', excerpt, 'For message tool thread creation, use `target` for the parent channel id instead of `channel`.'))
    if WORLD_NEWS_RE.search(message) and OMIT_WORLD_NEWS_RE.search(message):
        findings.append(Finding('cron-omits-required-world-news', 'medium', path, idx, 'AgentTurn prompt allows BREAKING WORLD NEWS to be omitted even though the section is part of the required brief shape.', excerpt, 'Keep required user-facing sections mandatory and add a fallback source instead of omitting them.'))
    return findings


def _scan_openclaw_json(root: Path) -> list[Finding]:
    path = root / 'openclaw.json'
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return []
    findings: list[Finding] = []
    if not isinstance(data, dict):
        return findings
    for key in data:
        if isinstance(key, str) and '.' in key:
            findings.append(Finding('openclaw-orphan-top-level-key', 'high', path, 1, 'openclaw.json contains a dotted top-level key that may indicate drift or a bad write path.', f'{key}=...', 'Top-level keys should be objects like `agents`; move dotted keys into the proper nested structure.'))
    return findings


def _job_excerpt(job: dict) -> str:
    name = job.get('name') or job.get('id') or 'unknown-job'
    return f'job={name}'


def _ignored(line: str) -> bool:
    lowered = line.lower()
    return 'watchclaw: ignore' in lowered or 'watchclaw:ignore' in lowered
