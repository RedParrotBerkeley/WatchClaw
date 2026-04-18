from __future__ import annotations

from collections import Counter
from pathlib import Path

from watchclaw.models import Finding


def render_markdown(root: Path, findings: list[Finding]) -> str:
    counts = Counter(f.severity for f in findings)
    lines = [
        "# WatchClaw Report",
        "",
        f"Scanned root: `{root}`",
        f"Findings: **{len(findings)}**",
        "",
        "## Severity summary",
        "",
    ]
    if counts:
        for severity, count in sorted(counts.items()):
            lines.append(f"- {severity}: {count}")
    else:
        lines.append("- no findings")
    lines.extend(["", "## Findings", ""])
    if findings:
        for finding in findings:
            lines.append(finding.to_markdown(root))
    else:
        lines.append("No findings.")
    return "\n".join(lines).strip() + "\n"
