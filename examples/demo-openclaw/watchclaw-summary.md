## WatchClaw Summary

- scanned root: `examples/demo-openclaw`
- total findings: **5**
- high: **2**
- medium: **3**

### Top findings

- `unsafe-workflow-interpolation` in `.github/workflows/demo.yml:7` — Potentially unsafe GitHub context interpolation in executable workflow content.
- `curl-pipe-shell` in `docs/install.md:6` — Remote script execution pattern detected.
- `high-token-turn` in `agents/main/sessions/demo.jsonl:3` — Large single-turn token usage detected.
- `repeated-rate-limit-events` in `agents/main/sessions/demo.jsonl:3` — Repeated rate-limit events detected in usage/session logs.
- `shortened-link` in `docs/install.md:9` — Shortened link detected in documentation.
