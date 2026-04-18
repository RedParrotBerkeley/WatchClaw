# WatchClaw

**Security and usage watchdog for OpenClaw.**

WatchClaw is an OpenClaw-native watchdog focused on two high-value jobs:

1. **catch risky docs/workflow issues before they spread**
2. **surface usage, spend, and runtime anomalies before they become incidents**

It is built for maintainers and power users running OpenClaw in real environments who need better visibility into:

- unsafe or misleading documentation snippets
- risky workflow / prompt / config patterns
- broken or suspicious links in docs
- usage spikes and token burn
- repeated runtime failures
- alert routing for high-severity events

## Why WatchClaw exists

OpenClaw already has strong building blocks for workflows, watchdog behavior, and security-minded automation. What is still missing is a focused tool that treats **docs safety**, **workflow safety**, and **usage monitoring** as one operational surface.

WatchClaw fills that gap.

Instead of acting like a generic uptime checker, WatchClaw is meant to watch the things OpenClaw users actually trip over:

- docs people copy and run
- examples that can drift into insecure patterns
- workflow files that deserve security scrutiny
- usage patterns that quietly turn into cost or reliability problems

## Positioning

WatchClaw is not a SIEM.

WatchClaw is not a full incident-management platform.

WatchClaw is a sharp, OpenClaw-specific watchdog that helps maintainers catch:

- **docs security problems**
- **workflow security problems**
- **usage and spend anomalies**
- **high-signal operational regressions**

## Initial use cases

### 1. Docs security scanning

Scan OpenClaw docs and markdown-heavy surfaces for:

- dangerous shell examples
- suspicious remote-script patterns
- token / credential leaks in examples
- unsafe links or redirect patterns
- prompt-injection bait in instructional content
- localization drift that reintroduces unsafe examples

### 2. Workflow and config monitoring

Review workflow and automation surfaces for:

- risky command execution patterns
- unsafe interpolation
- insecure install flows
- brittle integrations
- alert-routing regressions

### 3. Usage monitoring

Track runtime signals such as:

- sudden spend spikes
- token pressure and context bloat
- repeated rate-limit failures
- agent-specific anomaly patterns
- missing telemetry or broken accounting

### 4. Escalation

Route findings through the channels operators already use:

- Discord
- Telegram / WhatsApp where available
- optional SMS / phone escalation via external transports such as Twilio

## What makes it interesting

WatchClaw is compelling because it sits directly on the OpenClaw surface area instead of treating OpenClaw like just another app behind a ping check.

That makes it useful for:

- OpenClaw maintainers
- self-hosters
- power users running multiple agents
- contributors working on docs, workflows, and security-sensitive integrations

## v1 scope

The first version should stay tight:

- docs and markdown security checks
- workflow/config security checks
- usage anomaly detection
- high-signal Discord alerting
- simple daily or on-demand summaries

## Non-goals for v1

- full enterprise incident management
- broad infrastructure observability
- generic cloud monitoring
- trying to replace PagerDuty, Grafana, or a SIEM

## Suggested tagline options

- **WatchClaw — security and usage watchdog for OpenClaw**
- **WatchClaw — monitor OpenClaw docs, workflows, and spend**
- **WatchClaw — OpenClaw-native monitoring for docs safety and usage anomalies**

## Roadmap direction

Short term:

- define the core signal model
- ship docs/workflow checks
- ship usage anomaly summaries
- prove alert quality

Medium term:

- add remediation hints
- add repo-native GitHub reporting
- add optional phone/SMS escalation
- support more OpenClaw surfaces and integrations

## Status

Positioning repo bootstrap. Implementation to follow.
