from pathlib import Path

from watchclaw.detector import detect_repo_root


def test_detect_repo_root_uses_openclaw_markers(tmp_path: Path) -> None:
    root = tmp_path / "openclaw"
    nested = root / "watchclaw"
    nested.mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "openclaw.json").write_text("{}", encoding="utf-8")

    assert detect_repo_root(nested) == root
