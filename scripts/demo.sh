#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p examples/demo-openclaw
PYTHONPATH=src python3 -m watchclaw.cli scan examples/demo-openclaw \
  --markdown-out examples/demo-openclaw/watchclaw-report.md \
  --github-out examples/demo-openclaw/watchclaw-summary.md \
  --discord-out examples/demo-openclaw/watchclaw-discord.txt \
  --json-out examples/demo-openclaw/watchclaw-findings.json

echo
echo "Demo outputs refreshed:"
echo "- examples/demo-openclaw/watchclaw-report.md"
echo "- examples/demo-openclaw/watchclaw-summary.md"
echo "- examples/demo-openclaw/watchclaw-discord.txt"
echo "- examples/demo-openclaw/watchclaw-findings.json"
