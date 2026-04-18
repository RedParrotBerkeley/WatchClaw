from __future__ import annotations

import re
from pathlib import Path

from watchclaw.models import Finding

DOC_EXTENSIONS = {'.md', '.mdx', '.txt'}
EXCLUDED_NAME_PREFIXES = ('watchclaw-report', 'watchclaw-summary', 'watchclaw-findings', 'watchclaw-discord')
TOKEN_PATTERNS = (
    ('github-pat', re.compile(r'\bghp_[A-Za-z0-9]{16,}\b')),
    ('openai-key', re.compile(r'\bsk-(?:proj|svcacct)-[A-Za-z0-9-]{20,}\b')),
    ('anthropic-key', re.compile(r'\bsk-ant-[A-Za-z0-9-]{20,}\b')),
    ('slack-token', re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b')),
)
SUSPICIOUS_LINK_PATTERNS = (
    ('javascript-link', re.compile(r'(?:\[[^\]]*\]\(|href="|href=\'|url\()\s*javascript:', re.IGNORECASE), 'Suspicious javascript: link pattern detected in documentation.', 'Use plain HTTPS documentation links and avoid executable javascript: URLs.', 'high'),
    ('raw-ip-link', re.compile(r'https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?(?:/|\b)', re.IGNORECASE), 'Raw IP link detected in documentation.', 'Prefer stable HTTPS hostnames so readers can verify where commands and downloads come from.', 'medium'),
    ('shortened-link', re.compile(r'https?://(?:bit\.ly|t\.co|tinyurl\.com|goo\.gl|rb\.gy|ow\.ly)/', re.IGNORECASE), 'Shortened link detected in documentation.', 'Prefer explicit destination URLs so operators can inspect the domain before opening it.', 'medium'),
)


def scan_docs(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in DOC_EXTENSIONS:
            continue
        if path.name.startswith(EXCLUDED_NAME_PREFIXES):
            continue
        findings.extend(_scan_doc(path))
    return findings


def _scan_doc(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding='utf-8').splitlines()
    except UnicodeDecodeError:
        return findings
    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()
        if _ignored(line):
            continue
        findings.extend(_scan_shell_patterns(path, idx, line, lowered))
        findings.extend(_scan_token_patterns(path, idx, line))
        findings.extend(_scan_link_patterns(path, idx, line))
    return findings


def _scan_shell_patterns(path: Path, idx: int, line: str, lowered: str) -> list[Finding]:
    findings: list[Finding] = []
    if '| sh' in lowered or '| bash' in lowered or '| zsh' in lowered:
        if 'curl' in lowered and ('http://' in lowered or 'https://' in lowered):
            findings.append(Finding('curl-pipe-shell', 'high', path, idx, 'Remote script execution pattern detected.', line.strip(), 'Prefer a pinned download plus checksum verification instead of piping to a shell.'))
        elif 'wget' in lowered and ('http://' in lowered or 'https://' in lowered):
            findings.append(Finding('wget-pipe-shell', 'high', path, idx, 'Remote download is being piped directly into a shell.', line.strip(), 'Split download and execution steps and show integrity verification.'))
    return findings


def _scan_token_patterns(path: Path, idx: int, line: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule_suffix, pattern in TOKEN_PATTERNS:
        match = pattern.search(line)
        if not match:
            continue
        findings.append(Finding(f'token-example-{rule_suffix}', 'high', path, idx, 'Potential credential or token example detected in docs.', _redact_token_excerpt(line.strip(), match.group(0)), 'Replace live-looking secrets with clearly fake placeholders before publishing docs.'))
    return findings


def _scan_link_patterns(path: Path, idx: int, line: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule_id, pattern, message, remediation, severity in SUSPICIOUS_LINK_PATTERNS:
        if pattern.search(line):
            findings.append(Finding(rule_id, severity, path, idx, message, line.strip(), remediation))
    return findings


def _redact_token_excerpt(line: str, token: str) -> str:
    if len(token) <= 8:
        return line.replace(token, '[REDACTED]')
    return line.replace(token, f'{token[:4]}...{token[-4:]}')


def _ignored(line: str) -> bool:
    lowered = line.lower()
    return 'watchclaw: ignore' in lowered or 'watchclaw:ignore' in lowered
