from pathlib import Path

from watchclaw.models import Finding
from watchclaw.reporting import render_discord_alert, render_github_summary


def test_render_outputs_include_core_signal(tmp_path: Path) -> None:
    root = tmp_path
    finding = Finding(
        rule_id="curl-pipe-shell",
        severity="high",
        path=root / "docs" / "install.md",
        line_number=10,
        message="Remote script execution pattern detected.",
        excerpt="curl https://example.com/install.sh | sh",
        remediation="Use a checksum.",
    )

    gh = render_github_summary(root, [finding])
    discord = render_discord_alert(root, [finding])

    assert "WatchClaw Summary" in gh
    assert "curl-pipe-shell" in gh
    assert "WatchClaw found 1 issue" in discord
