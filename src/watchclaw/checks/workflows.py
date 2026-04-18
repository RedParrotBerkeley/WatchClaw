from __future__ import annotations

import re
from pathlib import Path

from watchclaw.models import Finding

WORKFLOW_EXTENSIONS = {".yml", ".yaml", ".json", ".sh", ".toml"}
WORKFLOW_NAME_HINTS = ("workflow", "action", "ci", "cron", "script", ".github")
UNSAFE_INTERPOLATION = re.compile(r"\$\{\{\s*github\.(?:event|head_ref|ref_name|actor)[^}]*\}\}")


def scan_workflows(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in WORKFLOW_EXTENSIONS:
            continue
        if not _looks_relevant(path):
            continue
        findings.extend(_scan_file(path))
    return findings


def _looks_relevant(path: Path) -> bool:
    path_str = str(path).lower()
    return any(hint in path_str for hint in WORKFLOW_NAME_HINTS)


def _scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings
    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()
        if ("run:" in lowered or path.suffix.lower() == ".sh") and UNSAFE_INTERPOLATION.search(line):
            findings.append(
                Finding(
                    rule_id="unsafe-workflow-interpolation",
                    severity="high",
                    path=path,
                    line_number=idx,
                    message="Potentially unsafe GitHub context interpolation in executable workflow content.",
                    excerpt=line.strip(),
                    remediation="Avoid interpolating untrusted GitHub metadata directly into shell commands; pass through validated env vars or strict quoting.",
                )
            )
        if "curl" in lowered and ("| sh" in lowered or "| bash" in lowered or "| zsh" in lowered):
            findings.append(
                Finding(
                    rule_id="workflow-curl-pipe-shell",
                    severity="high",
                    path=path,
                    line_number=idx,
                    message="Workflow executes a remote script directly from curl output.",
                    excerpt=line.strip(),
                    remediation="Download artifacts explicitly, pin versions, and verify integrity before execution.",
                )
            )
    return findings
