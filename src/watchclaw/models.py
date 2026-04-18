from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Finding:
    rule_id: str
    severity: str
    path: Path
    line_number: int
    message: str
    excerpt: str
    remediation: str

    def to_markdown(self, root: Path) -> str:
        rel = self.path.relative_to(root) if self.path.is_relative_to(root) else self.path
        return (
            f"- **{self.severity.upper()}** `{self.rule_id}` in `{rel}:{self.line_number}` — "
            f"{self.message}\n"
            f"  - Excerpt: `{self.excerpt}`\n"
            f"  - Fix: {self.remediation}"
        )
