from __future__ import annotations

import json
import re
from pathlib import Path

from watchclaw.models import Finding

OPENCLAW_ALLOWED_TOP_LEVEL_KEYS = {
    'agents',
    'channels',
    'memoryFlush',
    'globalCompactionPrompt',
    'gateway',
    'mcpServers',
    'skills',
    'logging',
    'runtime',
    'watchdog',
}
UNSAFE_PIPE_RE = re.compile(r'\b(?:curl|wget)\b[^\n|]*\|\s*(?:sh|bash|zsh)\b', re.IGNORECASE)
TOOLS_ALLOW_SAFE = {'exec', 'message', 'web_search', 'web_fetch', 'lobster'}


def scan_openclaw(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_scan_lobster_files(root))
    findings.extend(_scan_jobs_json(root))
    findings.extend(_scan_openclaw_json(root))
    return findings


def _scan_lobster_files(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob('*.lobster'):
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
                    findings.append(
                        Finding(
                            rule_id='lobster-remote-shell-pipe',
                            severity='high',
                            path=path,
                            line_number=idx,
                            message='Lobster command pipes a remote download directly into a shell.',
                            excerpt=stripped,
                            remediation='Split remote downloads from execution steps and verify integrity before running.',
                        )
                    )
                if '${' in command or re.search(r'\$[A-Za-z_][A-Za-z0-9_]*', command):
                    findings.append(
                        Finding(
                            rule_id='lobster-unrestricted-expansion',
                            severity='medium',
                            path=path,
                            line_number=idx,
                            message='Lobster command contains direct variable expansion that deserves review.',
                            excerpt=stripped,
                            remediation='Review variable expansion in command lines and prefer validated inputs or quoting for untrusted values.',
                        )
                    )
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
        tools_allow = payload.get('toolsAllow')
        if not isinstance(tools_allow, list):
            findings.append(
                Finding(
                    rule_id='cron-agentturn-missing-toolsallow',
                    severity='high',
                    path=path,
                    line_number=idx,
                    message='AgentTurn cron job is missing toolsAllow, which can lead to broader-than-intended tool access.',
                    excerpt=_job_excerpt(job),
                    remediation='Set an explicit toolsAllow list for each agentTurn cron job.',
                )
            )
        else:
            unexpected = [tool for tool in tools_allow if isinstance(tool, str) and tool not in TOOLS_ALLOW_SAFE]
            if unexpected:
                findings.append(
                    Finding(
                        rule_id='cron-agentturn-unreviewed-tools',
                        severity='medium',
                        path=path,
                        line_number=idx,
                        message='AgentTurn cron job allows tools outside the reviewed default set.',
                        excerpt=_job_excerpt(job),
                        remediation='Review toolsAllow and keep only the minimum tools needed for the scheduled turn.',
                    )
                )
        if 'thinking' not in payload:
            findings.append(
                Finding(
                    rule_id='cron-agentturn-missing-thinking-mode',
                    severity='medium',
                    path=path,
                    line_number=idx,
                    message='AgentTurn cron job does not pin a thinking mode, which can cause cost drift.',
                    excerpt=_job_excerpt(job),
                    remediation='Set thinking explicitly for scheduled jobs so model cost/behavior is predictable.',
                )
            )
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
    for key in data:
        if key not in OPENCLAW_ALLOWED_TOP_LEVEL_KEYS:
            findings.append(
                Finding(
                    rule_id='openclaw-orphan-top-level-key',
                    severity='high',
                    path=path,
                    line_number=1,
                    message='openclaw.json contains an unexpected top-level key that may indicate drift or a bad write path.',
                    excerpt=f'{key}=...',
                    remediation='Validate top-level keys in openclaw.json and remove orphan entries or move them to the correct nested section.',
                )
            )
    return findings


def _job_excerpt(job: dict) -> str:
    name = job.get('name') or job.get('id') or 'unknown-job'
    return f'job={name}'


def _ignored(line: str) -> bool:
    lowered = line.lower()
    return 'watchclaw: ignore' in lowered or 'watchclaw:ignore' in lowered
