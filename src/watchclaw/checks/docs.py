from __future__ import annotations

from pathlib import Path

from watchclaw.models import Finding

DOC_EXTENSIONS = {".md", ".mdx", ".txt"}
DANGEROUS_PATTERNS = {
    "curl-pipe-shell": {
        "needle": "curl",
        "message": "Remote script execution pattern detected.",
        "remediation": "Prefer a pinned download plus checksum verification instead of piping to a shell.",
    },
    "wget-pipe-shell": {
        "needle": "wget",
        "message": "Remote download is being piped directly into a shell.",
        "remediation": "Split download and execution steps and show integrity verification.",
    },
}


def scan_docs(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in DOC_EXTENSIONS:
            continue
        findings.extend(_scan_doc(path))
    return findings


def _scan_doc(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return findings
    for idx, line in enumerate(lines, start=1):
        lowered = line.lower()
        if "| sh" in lowered or "| bash" in lowered or "| zsh" in lowered:
            for rule_id, rule in DANGEROUS_PATTERNS.items():
                if rule["needle"] in lowered:
                    findings.append(
                        Finding(
                            rule_id=rule_id,
                            severity="high",
                            path=path,
                            line_number=idx,
                            message=rule["message"],
                            excerpt=line.strip(),
                            remediation=rule["remediation"],
                        )
                    )
                    break
    return findings
