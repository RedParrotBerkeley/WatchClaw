#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / 'examples' / 'demo-openclaw'
JSON_PATH = DEMO / 'watchclaw-findings.json'
SVG_PATH = ROOT / 'assets' / 'demo-terminal-live.svg'
PNG_PATH = ROOT / 'assets' / 'demo-terminal-live.png'
MAX_ROWS = 12
COL1 = 7
COL2 = 42
COL3 = 28


def ellipsize(text: str, width: int) -> str:
    text = text.replace('`', '')
    return text if len(text) <= width else text[: width - 1] + '…'


def build_lines() -> list[str]:
    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    findings = payload['findings']
    high = sum(1 for f in findings if f['severity'] == 'high')
    medium = sum(1 for f in findings if f['severity'] == 'medium')
    lines = [
        './watchclaw.sh',
        '',
        'WATCHCLAW // crab ops, but classy',
        f"scan target: {payload['root']}",
        f"findings: {len(findings)}  |  high: {high}  |  medium: {medium}",
        '',
        f"{'SEV'.ljust(COL1)} {'RULE'.ljust(COL2)} {'PATH'.ljust(COL3)}",
        f"{'-'*COL1} {'-'*COL2} {'-'*COL3}",
    ]
    for finding in findings[:MAX_ROWS]:
        sev = finding['severity'].upper().ljust(COL1)
        rule = ellipsize(finding['rule_id'], COL2).ljust(COL2)
        loc = ellipsize(f"{finding['path']}:{finding['line_number']}", COL3)
        lines.append(f"{sev} {rule} {loc}")
    if len(findings) > MAX_ROWS:
        lines.append(f"… and {len(findings) - MAX_ROWS} more findings")
    lines.extend([
        '',
        'caught before production:',
        '- wrong thread-create shape in cron prompt',
        '- required world news can disappear under quota pressure',
        '- missing toolsAllow and pinned thinking on scheduled jobs',
    ])
    return lines


def render_svg(lines: list[str]) -> str:
    width = 1200
    line_h = 28
    top = 98
    height = top + line_h * len(lines) + 70
    text_nodes = []
    for i, line in enumerate(lines):
        y = top + i * line_h
        fill = '#e5e7eb'
        if line.startswith('WATCHCLAW //'):
            fill = '#7dd3fc'
        elif line.startswith('HIGH'):
            fill = '#fca5a5'
        elif line.startswith('MEDIUM'):
            fill = '#fde68a'
        elif line.startswith('caught before production') or line.startswith('- wrong') or line.startswith('- required') or line.startswith('- missing'):
            fill = '#93c5fd'
        elif line.startswith('SEV') or line.startswith('---'):
            fill = '#94a3b8'
        elif line.startswith('… and'):
            fill = '#94a3b8'
        escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text_nodes.append(f'<text x="52" y="{y}" fill="{fill}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="24">{escaped}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="WatchClaw terminal screenshot">
  <rect width="{width}" height="{height}" fill="#0b1220" rx="24"/>
  <rect x="24" y="24" width="1152" height="{height-48}" fill="#111827" stroke="#2b3545" rx="20"/>
  <circle cx="58" cy="58" r="10" fill="#ff5f56"/><circle cx="88" cy="58" r="10" fill="#ffbd2e"/><circle cx="118" cy="58" r="10" fill="#27c93f"/>
  <rect x="880" y="34" width="246" height="48" fill="#0f766e" rx="12"/>
  <text x="912" y="65" fill="#ecfeff" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="22">crab ops, but classy</text>
  {''.join(text_nodes)}
</svg>'''


def main() -> int:
    lines = build_lines()
    SVG_PATH.write_text(render_svg(lines), encoding='utf-8')
    subprocess.run(['qlmanage', '-t', '-s', '1800', '-o', '/tmp/watchclaw-previews', str(SVG_PATH)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    preview = Path('/tmp/watchclaw-previews') / f'{SVG_PATH.name}.png'
    PNG_PATH.write_bytes(preview.read_bytes())
    print(PNG_PATH)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
