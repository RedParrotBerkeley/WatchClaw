# Demo fixture: OpenClaw-style tree

This folder is a tiny demo target for WatchClaw.

It now intentionally includes a realistic OpenClaw failure story:

- a morning-brief style scheduled job that teaches `thread-create` with `channel` instead of `target`
- the same scheduled job allowing `BREAKING WORLD NEWS` to be omitted under quota pressure
- a cron job missing `toolsAllow` and `thinking`
- an orphan `openclaw.json` key showing config drift
- a dangerous `.lobster` command
- session logs showing rate-limit churn and compaction pressure

Run from the repo root:

```bash
PYTHONPATH=src python3 -m watchclaw.cli scan examples/demo-openclaw \
  --markdown-out examples/demo-openclaw/watchclaw-report.md \
  --github-out examples/demo-openclaw/watchclaw-summary.md \
  --discord-out examples/demo-openclaw/watchclaw-discord.txt \
  --json-out examples/demo-openclaw/watchclaw-findings.json
```
