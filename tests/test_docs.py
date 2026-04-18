from pathlib import Path

from watchclaw.checks.docs import scan_docs


def test_scan_docs_finds_curl_pipe_shell(tmp_path: Path) -> None:
    doc = tmp_path / "docs" / "install.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("Run `curl https://example.com/install.sh | sh`\n", encoding="utf-8")

    findings = scan_docs(tmp_path)

    assert len(findings) == 1
    assert findings[0].rule_id == "curl-pipe-shell"
    assert findings[0].severity == "high"
