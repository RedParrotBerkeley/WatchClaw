from pathlib import Path

from watchclaw.checks.workflows import scan_workflows


def test_scan_workflows_finds_unsafe_interpolation(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        "steps:\n  - run: echo \"${{ github.event.pull_request.title }}\" | bash\n",
        encoding="utf-8",
    )

    findings = scan_workflows(tmp_path)

    assert len(findings) == 1
    assert findings[0].rule_id == "unsafe-workflow-interpolation"
