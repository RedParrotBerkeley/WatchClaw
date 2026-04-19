from pathlib import Path

from watchclaw.usage import scan_usage


def test_scan_usage_on_metric_file_finds_all_three_signals(tmp_path: Path) -> None:
    metrics = tmp_path / 'usage.jsonl'
    metrics.write_text(
        '\n'.join([
            '{"event":"warning","message":"rate limit reached","usage":{"totalTokens":1200}}',
            '{"event":"warning","error":{"message":"rate limit reached","code":429},"usage":{"totalTokens":1400}}',
            '{"event":"warning","status":429,"message":"compaction-diag triggered","usage":{"nested":{"totalTokens":75000}}}',
        ]) + '\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)
    rule_ids = {finding.rule_id for finding in findings}

    assert 'repeated-rate-limit-events' in rule_ids
    assert 'high-token-turn' in rule_ids
    assert 'context-compaction-pressure' in rule_ids


def test_scan_usage_on_session_transcript_suppresses_high_token_turn(tmp_path: Path) -> None:
    """Session turns legitimately hit 30k+ during normal long-form work.

    The high-token-turn rule is meant for metric files, not chat transcripts,
    so a session jsonl with giant turns but no rate-limit or compaction
    signal should produce no findings."""
    session = tmp_path / 'agents' / 'main' / 'sessions' / 'sample.jsonl'
    session.parent.mkdir(parents=True)
    session.write_text(
        '{"role":"assistant","usage":{"totalTokens":85000}}\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)
    rule_ids = {finding.rule_id for finding in findings}

    assert 'high-token-turn' not in rule_ids


def test_scan_usage_on_session_transcript_still_surfaces_rate_limit_and_compaction(
    tmp_path: Path,
) -> None:
    session = tmp_path / 'agents' / 'main' / 'sessions' / 'pressure.jsonl'
    session.parent.mkdir(parents=True)
    session.write_text(
        '\n'.join([
            '{"event":"warning","message":"rate limit reached"}',
            '{"event":"warning","error":{"message":"rate limit reached","code":429}}',
            '{"event":"warning","status":429,"message":"compaction-diag triggered"}',
        ]) + '\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)
    rule_ids = {finding.rule_id for finding in findings}

    assert 'repeated-rate-limit-events' in rule_ids
    assert 'context-compaction-pressure' in rule_ids
    assert 'high-token-turn' not in rule_ids


def test_scan_usage_ignores_plain_discussion_of_rate_limits(tmp_path: Path) -> None:
    session = tmp_path / 'agents' / 'main' / 'sessions' / 'discussion.jsonl'
    session.parent.mkdir(parents=True)
    session.write_text(
        '{"message":"we should talk about rate limits later","usage":{"totalTokens":1200}}\n',
        encoding='utf-8',
    )

    findings = scan_usage(tmp_path)

    assert findings == []
