from pathlib import Path

from watchclaw.usage import scan_usage


def test_scan_usage_finds_repeated_rate_limits_and_high_token_turn(tmp_path: Path) -> None:
    session = tmp_path / "agents" / "main" / "sessions" / "sample.jsonl"
    session.parent.mkdir(parents=True)
    session.write_text(
        '\n'.join([
            '{"error":"rate limit reached","usage":{"totalTokens":1200}}',
            '{"error":"rate limit reached","usage":{"totalTokens":1400}}',
            '{"error":"rate limit reached","usage":{"totalTokens":35000}}',
        ]) + '\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)
    rule_ids = {finding.rule_id for finding in findings}

    assert "repeated-rate-limit-events" in rule_ids
    assert "high-token-turn" in rule_ids
