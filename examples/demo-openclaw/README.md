# Demo fixture: OpenClaw-style tree

This folder is a tiny demo target for WatchClaw.

It intentionally includes:

- a risky docs shell example
- a shortened link in docs
- an unsafe workflow interpolation pattern
- repeated rate-limit entries in a session log

Run from the repo root:

```bash
PYTHONPATH=src python3 -m watchclaw.cli scan examples/demo-openclaw \
  --markdown-out examples/demo-openclaw/watchclaw-report.md \
  --github-out examples/demo-openclaw/watchclaw-summary.md \
  --discord-out examples/demo-openclaw/watchclaw-discord.txt \
  --json-out examples/demo-openclaw/watchclaw-findings.json
```
