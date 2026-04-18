from pathlib import Path

from watchclaw.usage import scan_usage


def test_scan_usage_finds_openclaw_session_pressure_signals(tmp_path: Path) -> None:
    session = tmp_path / 'agents' / 'main' / 'sessions' / 'sample.jsonl'
    session.parent.mkdir(parents=True)
    session.write_text(
        '\n'.join([
            '{"event":"warning","message":"rate limit reached","usage":{"totalTokens":1200}}',
            '{"event":"warning","error":{"message":"rate limit reached","code":429},"usage":{"totalTokens":1400}}',
            '{"event":"warning","status":429,"message":"compaction-diag triggered","usage":{"nested":{"totalTokens":35000}}}',
        ]) + '\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)
    rule_ids = {finding.rule_id for finding in findings}

    assert 'repeated-rate-limit-events' in rule_ids
    assert 'high-token-turn' in rule_ids
    assert 'context-compaction-pressure' in rule_ids


def test_scan_usage_ignores_plain_discussion_of_rate_limits(tmp_path: Path) -> None:
    session = tmp_path / 'agents' / 'main' / 'sessions' / 'discussion.jsonl'
    session.parent.mkdir(parents=True)
    session.write_text(
        '{"message":"we should talk about rate limits later","usage":{"totalTokens":1200}}\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)

    assert findings == []
