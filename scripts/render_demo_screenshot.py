#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / 'examples' / 'demo-openclaw' / 'watchclaw-findings.json'
SVG_PATH = ROOT / 'assets' / 'demo-terminal-live.svg'
PNG_PATH = ROOT / 'assets' / 'demo-terminal-live.png'
WIDTH = 760
LEFT = 36
TOP = 96
LINE_H = 38
MAX_FINDINGS = 7
RULE_W = 26
PATH_W = 18


def short(text: str, width: int) -> str:
    text = text.replace('`', '')
    return text if len(text) <= width else text[: width - 1] + '…'


def build_lines() -> list[tuple[str, str]]:
    payload = json.loads(JSON_PATH.read_text(encoding='utf-8'))
    findings = payload['findings']
    high = sum(1 for f in findings if f['severity'] == 'high')
    medium = sum(1 for f in findings if f['severity'] == 'medium')
    lines: list[tuple[str, str]] = [
        ('cmd', './watchclaw.sh'),
        ('brand', 'WATCHCLAW // crab ops, but classy'),
        ('meta', f"target: {payload['root']}"),
        ('meta', f"findings: {len(findings)} | high: {high} | med: {medium}"),
        ('gap', ''),
        ('head', 'SEV   RULE                       PATH'),
        ('rule', '───   ────────────────────────── ──────────────────'),
    ]
    for finding in findings[:MAX_FINDINGS]:
        sev = finding['severity'].upper().ljust(6)
        rule = short(finding['rule_id'], RULE_W).ljust(RULE_W)
        path = short(f"{finding['path']}:{finding['line_number']}", PATH_W)
        lines.append((finding['severity'], f'{sev}{rule} {path}'))
    lines.extend([
        ('gap', ''),
        ('callout', 'caught before production:'),
        ('bullet', '• wrong thread-create shape in cron prompt'),
        ('bullet', '• required world news can disappear'),
        ('bullet', '• missing toolsAllow + pinned thinking'),
    ])
    return lines


def render_svg(lines: list[tuple[str, str]]) -> str:
    height = TOP + LINE_H * len(lines) + 56
    nodes = []
    for i, (kind, line) in enumerate(lines):
        if kind == 'gap':
            continue
        y = TOP + i * LINE_H
        fill = '#e5e7eb'
        size = 24
        if kind == 'brand':
            fill = '#7dd3fc'
            size = 27
        elif kind == 'cmd':
            fill = '#e5e7eb'
            size = 25
        elif kind == 'head' or kind == 'rule':
            fill = '#94a3b8'
            size = 23
        elif kind == 'high':
            fill = '#fca5a5'
        elif kind == 'medium':
            fill = '#fde68a'
        elif kind == 'callout' or kind == 'bullet':
            fill = '#93c5fd'
        escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        nodes.append(f'<text x="{LEFT}" y="{y}" fill="{fill}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="{size}">{escaped}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="WatchClaw terminal screenshot">
  <rect width="{WIDTH}" height="{height}" fill="#0b1220" rx="22"/>
  <rect x="18" y="18" width="{WIDTH-36}" height="{height-36}" fill="#111827" stroke="#2b3545" rx="18"/>
  <circle cx="46" cy="48" r="8" fill="#ff5f56"/><circle cx="70" cy="48" r="8" fill="#ffbd2e"/><circle cx="94" cy="48" r="8" fill="#27c93f"/>
  <rect x="500" y="28" width="220" height="34" fill="#0f766e" rx="10"/>
  <text x="522" y="51" fill="#ecfeff" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="16">crab ops, but classy</text>
  {''.join(nodes)}
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
