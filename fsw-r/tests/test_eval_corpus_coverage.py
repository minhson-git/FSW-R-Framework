from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest

from eval_corpus_coverage import (
    Results,
    Stage,
    _classify_timeline_failure,
    build_report,
    load_corpus,
    render_markdown,
)
from fsw_r.core.fswr_converter import fsw_to_fswr
from fsw_r.timeline.build import build_timeline

# Real FSW strings that each trip one of build_timeline()'s MVP-2 scope
# limits, paired with the label the report must file them under. These go
# through the REAL build_timeline rather than asserting against a copied
# message string -- so if a message is reworded, this test fails instead of
# the report silently growing an "other" bucket.
SCOPE_FAILURES = (
    ("M500x500S10000480x480S30a00500x500", "symbol outside Categories 1-2"),
    ("M500x500S22b00480x480", "not 1-2 hand symbols"),
    ("M500x500S10000480x480S10100500x500", "two postures on one hand"),
    ("M500x500S10000480x480S22b00500x500S22b00510x510", "two movements on one hand"),
)


@pytest.mark.parametrize("fsw,expected_label", SCOPE_FAILURES)
def test_timeline_failures_are_classified_not_bucketed_as_other(fsw: str, expected_label: str) -> None:
    with pytest.raises(Exception) as caught:
        build_timeline(fsw_to_fswr(fsw))
    assert _classify_timeline_failure(str(caught.value)) == expected_label


def test_unrecognised_message_falls_back_to_other() -> None:
    assert _classify_timeline_failure("something nobody anticipated") == "other"


def test_stage_counters_are_consistent() -> None:
    stage = Stage("x", attempted=10, succeeded=4)
    assert stage.failed == 6
    assert stage.rate == pytest.approx(0.4)


def test_stage_rate_is_zero_when_nothing_attempted() -> None:
    assert Stage("x").rate == 0.0


def test_stage_reports_both_conditional_and_unconditional_rates() -> None:
    """The conditional rate (of what reached the stage) and the corpus-wide
    rate differ whenever an earlier stage dropped anything -- reporting only
    one of them is how a pipeline looks better than it is."""
    stage = Stage("x", attempted=50, succeeded=25)
    entry = stage.as_dict(corpus_total=100)
    assert entry["success_rate_of_attempted"] == pytest.approx(0.5)
    assert entry["success_rate_of_corpus"] == pytest.approx(0.25)


def test_load_corpus_fails_loudly_when_missing() -> None:
    with pytest.raises(SystemExit, match="fetch_corpus"):
        load_corpus(Path("does-not-exist.csv"), limit=None)


def _synthetic_results() -> Results:
    results = Results(corpus_rows=100)
    results.parse = Stage("FSW Parsing", attempted=100, succeeded=98)
    results.mapping = Stage("Symbol Mapping (per sign)", attempted=98, succeeded=90)
    results.timeline = Stage("Timeline Construction", attempted=90, succeeded=20)
    results.generation = Stage("Animation Generation", attempted=20, succeeded=20)
    results.symbol_tokens = 500
    results.symbol_mapped = 480
    results.tokens_by_category[1] = 300
    results.tokens_by_category[2] = 180
    results.bases_seen = {0x100, 0x22B}
    results.frames_total = 480
    results.tracks_total = 24
    return results


def test_build_report_separates_symbol_and_sign_level() -> None:
    report = build_report(_synthetic_results(), fps=30, seed=0)
    symbol = cast(dict[str, object], report["symbol_level"])
    assert symbol["symbol_tokens"] == 500
    assert symbol["symbols_unmapped"] == 20
    stages = cast(list[dict[str, object]], report["stages"])
    assert [s["stage"] for s in stages] == [
        "FSW Parsing",
        "Symbol Mapping (per sign)",
        "Timeline Construction",
        "Animation Generation",
    ]


def test_report_states_the_corpus_is_input_only() -> None:
    """The corpus supplies FSW strings; treating it as ground truth would
    turn this into an accuracy evaluation, which it explicitly is not."""
    report = build_report(_synthetic_results(), fps=30, seed=0)
    meta = cast(dict[str, object], report["_meta"])
    assert "not an accuracy evaluation" in str(meta["corpus_role"])


def test_render_markdown_has_the_stage_table_and_both_rate_columns() -> None:
    markdown = render_markdown(_synthetic_results(), fps=30, seed=0)
    assert "| Processing Stage | Input | Successful | Failed | Success Rate | % of corpus |" in markdown
    assert "Timeline Construction" in markdown
    assert "## Library exercise" in markdown
