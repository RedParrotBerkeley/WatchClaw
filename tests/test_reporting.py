from pathlib import Path

from watchclaw.models import Finding
from watchclaw.reporting import render_discord_alert, render_github_summary, render_json, render_markdown


def test_render_outputs_include_core_signal(tmp_path: Path) -> None:
    root = tmp_path
    finding = Finding(
        rule_id='curl-pipe-shell',
        severity='high',
        path=root / 'docs' / 'install.md',
        line_number=10,
        message='Remote script execution pattern detected.',
        excerpt='curl https://example.com/install.sh | sh',
        remediation='Use a checksum.',
    )

    gh = render_github_summary(root, [finding])
    discord = render_discord_alert(root, [finding])

    assert 'WatchClaw Summary' in gh
    assert 'curl-pipe-shell' in gh
    assert 'WatchClaw found 1 issue' in discord


def test_render_outputs_prefer_human_root_display(tmp_path: Path, monkeypatch) -> None:
    root = tmp_path / 'demo-openclaw'
    root.mkdir()
    monkeypatch.chdir(tmp_path)
    finding = Finding(
        rule_id='shortened-link',
        severity='medium',
        path=root / 'docs' / 'install.md',
        line_number=9,
        message='Shortened link detected in documentation.',
        excerpt='https://bit.ly/watchclaw-demo',
        remediation='Use the full destination URL.',
    )

    gh = render_github_summary(root, [finding])
    md = render_markdown(root, [finding])
    payload = render_json(root, [finding])

    assert '`demo-openclaw`' in gh
    assert '`demo-openclaw`' in md
    assert '"root": "demo-openclaw"' in payload
    assert '"path": "docs/install.md"' in payload


def test_discord_alert_stays_under_limit(tmp_path: Path) -> None:
    root = tmp_path / 'demo-openclaw'
    root.mkdir()
    findings = [
        Finding(
            rule_id=f'long-rule-{i}',
            severity='high' if i % 2 == 0 else 'medium',
            path=root / ('very' * 20) / f'file{i}.md',
            line_number=100 + i,
            message='x' * 20,
            excerpt='y' * 40,
            remediation='z' * 20,
        )
        for i in range(30)
    ]
    alert = render_discord_alert(root, findings, limit=10)
    assert len(alert) <= 1900
    assert 'more' in alert or len(findings) <= 10
