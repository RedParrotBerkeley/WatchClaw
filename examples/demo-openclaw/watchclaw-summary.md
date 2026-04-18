## WatchClaw Summary

- scanned root: `examples/demo-openclaw`
- total findings: **13**
- high: **6**
- medium: **7**

### Top findings

- `unsafe-workflow-interpolation` in `.github/workflows/demo.yml:7` — Potentially unsafe GitHub context interpolation in executable workflow content.
- `cron-agentturn-missing-toolsallow` in `cron/jobs.json:1` — AgentTurn cron job is missing toolsAllow, which can lead to broader-than-intended tool access.
- `cron-thread-create-channel-instead-of-target` in `cron/jobs.json:1` — AgentTurn prompt teaches thread-create with `channel` instead of `target`, which can break posting.
- `curl-pipe-shell` in `docs/install.md:6` — Remote script execution pattern detected.
- `openclaw-orphan-top-level-key` in `openclaw.json:1` — openclaw.json contains an unexpected top-level key that may indicate drift or a bad write path.
