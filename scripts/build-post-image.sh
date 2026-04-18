#!/usr/bin/env bash
# Build the README demo screenshot from real scan output.
# Regenerates assets/demo-terminal.png so it always reflects the current rule set.
#
# Requires: charmbracelet/freeze (`brew install charmbracelet/tap/freeze`).

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v freeze >/dev/null 2>&1; then
  echo "freeze not found. Install with: brew install charmbracelet/tap/freeze" >&2
  exit 1
fi

FINDINGS_JSON="$(mktemp -t watchclaw-findings.XXXXXX.json)"
SHOT_TXT="$(mktemp -t watchclaw-shot.XXXXXX.txt)"
trap 'rm -f "$FINDINGS_JSON" "$SHOT_TXT"' EXIT

scan_rc=0
PYTHONPATH=src python3 -m watchclaw.cli scan examples/demo-openclaw \
  --json-out "$FINDINGS_JSON" >/dev/null || scan_rc=$?
# rc=1 just means findings were present (expected on the demo fixture); rc>=2 is a real error
if (( scan_rc > 1 )); then
  echo "watchclaw scan failed with rc=${scan_rc}" >&2
  exit "$scan_rc"
fi

python3 - "$FINDINGS_JSON" > "$SHOT_TXT" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
findings = data["findings"]
high = [f for f in findings if f["severity"] == "high"]
med = [f for f in findings if f["severity"] == "medium"]
print("$ ./watchclaw.sh examples/demo-openclaw")
print()
print(f"WatchClaw found {len(findings)} issues  ({len(high)} HIGH \u00b7 {len(med)} MEDIUM)")
print()
for f in high:
    loc = f"{f['path']}:{f['line_number']}"
    print(f"  HIGH  {f['rule_id']:<47}  {loc}")
shown_med = med[:4]
for f in shown_med:
    loc = f"{f['path']}:{f['line_number']}"
    print(f"  MED   {f['rule_id']:<47}  {loc}")
extra = len(med) - len(shown_med)
if extra > 0:
    print(f"        ... {extra} more MEDIUM findings")
PY

freeze "$SHOT_TXT" \
  --output assets/demo-terminal.png \
  --language bash \
  --width 1040 \
  --font.size 15 \
  --padding 32 \
  --margin 20 \
  --background "#0d1117" \
  --theme dracula \
  --window \
  --border.radius 10

echo "Wrote assets/demo-terminal.png"
