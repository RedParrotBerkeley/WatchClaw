# WatchClaw Report

Scanned root: `examples/demo-openclaw`
Findings: **13**

## Severity summary

- high: 6
- medium: 7

## Findings

- **HIGH** `unsafe-workflow-interpolation` in `.github/workflows/demo.yml:7` — Potentially unsafe GitHub context interpolation in executable workflow content.
  - Excerpt: `- run: echo "${{ github.event.pull_request.title }}" | bash`
  - Fix: Avoid interpolating untrusted GitHub metadata directly into shell commands; pass through validated env vars or strict quoting.
- **HIGH** `cron-agentturn-missing-toolsallow` in `cron/jobs.json:1` — AgentTurn cron job is missing toolsAllow, which can lead to broader-than-intended tool access.
  - Excerpt: `job=Morning briefing`
  - Fix: Set an explicit toolsAllow list for each agentTurn cron job.
- **HIGH** `cron-thread-create-channel-instead-of-target` in `cron/jobs.json:1` — AgentTurn prompt teaches thread-create with `channel` instead of `target`, which can break posting.
  - Excerpt: `job=Morning briefing`
  - Fix: For message tool thread creation, use `target` for the parent channel id instead of `channel`.
- **HIGH** `curl-pipe-shell` in `docs/install.md:6` — Remote script execution pattern detected.
  - Excerpt: `curl https://example.com/install.sh | sh`
  - Fix: Prefer a pinned download plus checksum verification instead of piping to a shell.
- **HIGH** `openclaw-orphan-top-level-key` in `openclaw.json:1` — openclaw.json contains an unexpected top-level key that may indicate drift or a bad write path.
  - Excerpt: `agents.main=...`
  - Fix: Validate top-level keys in openclaw.json and remove orphan entries or move them to the correct nested section.
- **HIGH** `lobster-remote-shell-pipe` in `workflows/deploy.lobster:2` — Lobster command pipes a remote download directly into a shell.
  - Excerpt: `- command: curl https://example.com/bootstrap.sh | bash`
  - Fix: Split remote downloads from execution steps and verify integrity before running.
- **MEDIUM** `context-compaction-pressure` in `agents/main/sessions/demo.jsonl:3` — Context overflow or compaction diagnostics appeared in session logs.
  - Excerpt: `context-overflow-diag / compaction-diag marker observed`
  - Fix: Investigate long-lived sessions, earlier compaction, or smaller delegated runs before cache churn becomes expensive.
- **MEDIUM** `high-token-turn` in `agents/main/sessions/demo.jsonl:3` — Large single-turn token usage detected.
  - Excerpt: `totalTokens=35000`
  - Fix: Trim carried context or move heavy reasoning into smaller delegated runs to reduce token pressure.
- **MEDIUM** `repeated-rate-limit-events` in `agents/main/sessions/demo.jsonl:3` — Repeated rate-limit events detected in usage/session logs.
  - Excerpt: `multiple 429/rate-limit entries observed`
  - Fix: Investigate prompt/context growth, model choice, and retry policy before public-facing failures stack up.
- **MEDIUM** `cron-agentturn-missing-thinking-mode` in `cron/jobs.json:1` — AgentTurn cron job does not pin a thinking mode, which can cause cost drift.
  - Excerpt: `job=Morning briefing`
  - Fix: Set thinking explicitly for scheduled jobs so model cost/behavior is predictable.
- **MEDIUM** `cron-omits-required-world-news` in `cron/jobs.json:1` — AgentTurn prompt allows BREAKING WORLD NEWS to be omitted even though the section is part of the required brief shape.
  - Excerpt: `job=Morning briefing`
  - Fix: Keep required user-facing sections mandatory and add a fallback source instead of omitting them.
- **MEDIUM** `shortened-link` in `docs/install.md:9` — Shortened link detected in documentation.
  - Excerpt: `Docs mirror: https://bit.ly/watchclaw-demo`
  - Fix: Prefer explicit destination URLs so operators can inspect the domain before opening it.
- **MEDIUM** `lobster-unrestricted-expansion` in `workflows/deploy.lobster:3` — Lobster command contains direct variable expansion that deserves review.
  - Excerpt: `- command: echo ${USER}`
  - Fix: Review variable expansion in command lines and prefer validated inputs or quoting for untrusted values.
