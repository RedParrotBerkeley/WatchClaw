from __future__ import annotations

import json
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


def render_github_summary(root: Path, findings: list[Finding]) -> str:
    high = [f for f in findings if f.severity == "high"]
    medium = [f for f in findings if f.severity == "medium"]
    lines = [
        "## WatchClaw Summary",
        "",
        f"- scanned root: `{root}`",
        f"- total findings: **{len(findings)}**",
        f"- high: **{len(high)}**",
        f"- medium: **{len(medium)}**",
        "",
    ]
    if findings:
        lines.append("### Top findings")
        lines.append("")
        for finding in findings[:5]:
            rel = finding.path.relative_to(root) if finding.path.is_relative_to(root) else finding.path
            lines.append(
                f"- `{finding.rule_id}` in `{rel}:{finding.line_number}` — {finding.message}"
            )
    else:
        lines.append("No findings.")
    return "\n".join(lines).strip() + "\n"


def render_discord_alert(root: Path, findings: list[Finding], limit: int = 3) -> str:
    if not findings:
        return f"✅ WatchClaw: no findings for `{root.name}`."
    top = findings[:limit]
    fragments = []
    for finding in top:
        rel = finding.path.relative_to(root) if finding.path.is_relative_to(root) else finding.path
        fragments.append(
            f"[{finding.severity.upper()}] {finding.rule_id} at {rel}:{finding.line_number}"
        )
    extra = ""
    if len(findings) > limit:
        extra = f" (+{len(findings) - limit} more)"
    return f"⚠️ WatchClaw found {len(findings)} issue(s) in `{root.name}`: " + "; ".join(fragments) + extra


def render_json(root: Path, findings: list[Finding]) -> str:
    payload = {
        "root": str(root),
        "findings": [
            {
                "rule_id": f.rule_id,
                "severity": f.severity,
                "path": str(f.path),
                "line_number": f.line_number,
                "message": f.message,
                "excerpt": f.excerpt,
                "remediation": f.remediation,
            }
            for f in findings
        ],
    }
    return json.dumps(payload, indent=2) + "\n"
