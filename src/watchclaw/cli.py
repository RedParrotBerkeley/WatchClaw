from __future__ import annotations

import argparse
from pathlib import Path

from watchclaw.checks.docs import scan_docs
from watchclaw.detector import detect_repo_root
from watchclaw.reporting import render_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="watchclaw",
        description="Security and usage watchdog for OpenClaw.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Scan an OpenClaw-style tree.")
    scan.add_argument("target", nargs="?", default=".", help="Folder to scan. Defaults to current directory.")
    scan.add_argument(
        "--markdown-out",
        help="Optional path for a markdown report.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "scan":
        target = Path(args.target)
        root = detect_repo_root(target)
        findings = scan_docs(root)
        report = render_markdown(root, findings)
        print(report, end="")
        if args.markdown_out:
            Path(args.markdown_out).write_text(report, encoding="utf-8")
        return 1 if findings else 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
