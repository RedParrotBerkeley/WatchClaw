# WatchClaw Report

Scanned root: `/private/tmp/watchclaw/examples/demo-openclaw`
Findings: **5**

## Severity summary

- high: 2
- medium: 3

## Findings

- **HIGH** `unsafe-workflow-interpolation` in `.github/workflows/demo.yml:7` — Potentially unsafe GitHub context interpolation in executable workflow content.
  - Excerpt: `- run: echo "${{ github.event.pull_request.title }}" | bash`
  - Fix: Avoid interpolating untrusted GitHub metadata directly into shell commands; pass through validated env vars or strict quoting.
- **HIGH** `curl-pipe-shell` in `docs/install.md:6` — Remote script execution pattern detected.
  - Excerpt: `curl https://example.com/install.sh | sh`
  - Fix: Prefer a pinned download plus checksum verification instead of piping to a shell.
- **MEDIUM** `high-token-turn` in `agents/main/sessions/demo.jsonl:3` — Large single-turn token usage detected.
  - Excerpt: `totalTokens=35000`
  - Fix: Trim carried context or move heavy reasoning into smaller delegated runs to reduce token pressure.
- **MEDIUM** `repeated-rate-limit-events` in `agents/main/sessions/demo.jsonl:3` — Repeated rate-limit events detected in usage/session logs.
  - Excerpt: `multiple 429/rate-limit entries observed`
  - Fix: Investigate prompt/context growth, model choice, and retry policy before public-facing failures stack up.
- **MEDIUM** `shortened-link` in `docs/install.md:9` — Shortened link detected in documentation.
  - Excerpt: `Docs mirror: https://bit.ly/watchclaw-demo`
  - Fix: Prefer explicit destination URLs so operators can inspect the domain before opening it.
