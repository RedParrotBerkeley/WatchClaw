from __future__ import annotations

import argparse
from pathlib import Path

from watchclaw.checks.docs import scan_docs
from watchclaw.checks.openclaw import scan_openclaw
from watchclaw.checks.workflows import scan_workflows
from watchclaw.detector import detect_repo_root
from watchclaw.reporting import render_discord_alert, render_github_summary, render_json, render_markdown
from watchclaw.usage import scan_usage


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='watchclaw', description='Security and usage watchdog for OpenClaw.')
    subparsers = parser.add_subparsers(dest='command', required=True)
    scan = subparsers.add_parser('scan', help='Scan an OpenClaw-style tree.')
    scan.add_argument('target', nargs='?', default='.', help='Folder to scan. Defaults to current directory.')
    scan.add_argument('--markdown-out', help='Optional path for a markdown report.')
    scan.add_argument('--github-out', help='Optional path for a GitHub-ready markdown summary.')
    scan.add_argument('--discord-out', help='Optional path for a compact Discord alert payload.')
    scan.add_argument('--json-out', help='Optional path for JSON findings.')
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == 'scan':
        root = detect_repo_root(Path(args.target))
        findings = []
        findings.extend(scan_docs(root))
        findings.extend(scan_workflows(root))
        findings.extend(scan_openclaw(root))
        findings.extend(scan_usage(root))
        findings.sort(key=lambda f: (f.severity != 'high', str(f.path), f.line_number, f.rule_id))
        report = render_markdown(root, findings)
        github_summary = render_github_summary(root, findings)
        discord_alert = render_discord_alert(root, findings)
        json_payload = render_json(root, findings)
        print(report, end='')
        if args.markdown_out:
            Path(args.markdown_out).write_text(report, encoding='utf-8')
        if args.github_out:
            Path(args.github_out).write_text(github_summary, encoding='utf-8')
        if args.discord_out:
            Path(args.discord_out).write_text(discord_alert + '\n', encoding='utf-8')
        if args.json_out:
            Path(args.json_out).write_text(json_payload, encoding='utf-8')
        return 1 if any(f.severity == 'high' for f in findings) else 0
    parser.error('unknown command')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
