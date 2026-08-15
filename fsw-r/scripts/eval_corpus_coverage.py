"""Runs a real FSW corpus through the whole pipeline and reports, stage by
stage, how much of it the framework can actually process.

This is a **functional / process** evaluation, deliberately NOT an accuracy
one: it measures whether each stage produces an output at all, never
whether that output is the semantically or perceptually right animation.
The corpus supplies INPUT only; nothing in it is treated as ground truth.

Stages, each measured separately so a failure is attributed to the stage
that actually caused it:

    1. FSW Parsing          fsw_ast.parse_fsw_to_ast()   string -> AST
    2. Symbol Mapping       registry.build_symbol()      AST node -> symbol object
    3. Timeline Construction timeline.build_timeline()   symbols -> tracks/keyframes
    4. Animation Generation  timeline.sample()           timeline -> pose frames

Stage 2 is measured at BOTH levels, because they answer different
questions: per-SYMBOL ("what fraction of ISWA tokens in real use does the
library cover?") and per-SIGN ("for what fraction of signs did EVERY symbol
map?", which is what stage 3 can actually consume).

Numbers this replaces: ``timeline/build.py`` and several ``core/`` modules
cite corpus percentages (MVP-1 6.2%, MVP-2 ~20.9%, Category 5 fill skew...)
measured ad hoc during development. This script makes them reproducible.

**It does not reproduce all of them.** Measured over the full corpus, MVP-2
timeline construction succeeds for 14.0% of signs, not the ~20.9% that
``timeline/build.py``'s docstring cites. The "Timeline scope funnel" in the
report shows why the two can differ: 23.0% of signs survive every MVP-2
constraint EXCEPT "at most 1 movement per hand", so a looser filter reaches
a figure in that neighbourhood. Whichever number the paper quotes has to
come from this script, not from the docstring.

Prerequisite:  python scripts/fetch_corpus.py
Run:           python scripts/eval_corpus_coverage.py
               python scripts/eval_corpus_coverage.py --limit 20000
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from fsw_r.core.fsw_ast import parse_fsw_to_ast
from fsw_r.core.fsw_symbol_key import parse_fsw_symbol_key
from fsw_r.core.fswr_converter import PositionedSymbol
from fsw_r.core.iswa_data import GROUP_START, category_of
from fsw_r.core.registry import build_symbol
from fsw_r.core.renderable_symbol import FSWRenderableSymbol
from fsw_r.timeline.build import build_timeline
from fsw_r.timeline.sample import sample
from fsw_r.timeline.types import SignTimeline

CORPUS_PATH = Path(__file__).resolve().parent.parent / "data" / "external" / "signbank_plus_raw.csv"
REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
FSW_COLUMN = "sign_writing"

_CSV_FIELD_LIMIT = 10**7
DEFAULT_FPS = 30

# ISWA base-symbol total, from data/iswa_valid_combinations.json (the font
# cmap). Used to report what fraction of the library real usage exercises.
ISWA_BASE_SYMBOLS = 652

_CATEGORY_NAME = {
    1: "Hands",
    2: "Movement",
    3: "Dynamics",
    4: "Head & Face",
    5: "Trunk & Limb",
    6: "Location",
    7: "Punctuation",
}

# Stable short labels for timeline failures, matched against the message
# build_timeline() raises. Keeping this as an explicit table (rather than
# bucketing raw message text) means an upstream message change shows up as
# a growing "other" bucket instead of silently re-partitioning the report.
_TIMELINE_REASONS: tuple[tuple[str, str], ...] = (
    ("only supports Category 1", "symbol outside Categories 1-2"),
    ("1 or 2 hand (Category 1) symbols", "not 1-2 hand symbols"),
    ("at most one posture per hand", "two postures on one hand"),
    ("at most 1 movement per hand", "two movements on one hand"),
)


def _classify_timeline_failure(message: str) -> str:
    for needle, label in _TIMELINE_REASONS:
        if needle in message:
            return label
    return "other"


# Every corpus-derived percentage asserted anywhere in fsw_r's own source,
# with the file that asserts it. Each was measured ad hoc during development
# and none could be re-derived, which under the paper's own "no invented
# data" rule makes them unquotable. verify_cited_claims() recomputes each
# one from the corpus so they either become citable or get corrected.
# (key, where it is asserted, cited %, the DEFINITION measured here). The
# definition is part of the output, not just a comment: a percentage whose
# population and filter are unstated is no more reproducible than one that
# was never measured, and an unrecoverable original definition is itself
# the finding wherever a claim fails to reproduce.
_CITED_CLAIMS: tuple[tuple[str, str, float, str], ...] = (
    ("mvp1_one_hand", "timeline/build.py", 6.2,
     "signs whose built timeline has exactly 1 track, over all corpus signs"),
    ("mvp2_coverage", "timeline/build.py", 20.9,
     "signs whose timeline builds at all, over all corpus signs"),
    ("cat5_fill0", "core/body_types.py, core/body_symbol.py", 92.5,
     "Category 5 symbol TOKENS with fill == 0, over all Category 5 tokens"),
    ("cat5_rotation_0_7", "core/body_types.py, core/body_symbol.py", 88.7,
     "Category 5 symbol TOKENS with rotation 0-7, over all Category 5 tokens"),
    ("group12_sign_share", "core/movement_paths.py", 16.8,
     "signs containing >=1 Group 12 symbol, over all parsed signs"),
    ("group12_top5_tokens", "core/movement_paths.py, scripts/gen_finger_articulations.py", 76.1,
     "Group 12 TOKENS whose base is one of the 5 named in finger_articulations.json, "
     "over all Group 12 tokens"),
    ("cat2_right_rot_0_7", "core/movement_symbol.py", 62.2,
     "in signs with EXACTLY ONE Category 1 symbol whose rotation < 8 (a right hand): "
     "Category 2 TOKENS with rotation 0-7, over that sign set's Category 2 tokens"),
    ("cat2_left_rot_0_7", "core/movement_symbol.py", 58.5,
     "same, for signs whose single Category 1 symbol has rotation >= 8 (a left hand)"),
)

# A claim counts as reproduced if it lands within this many percentage
# points. Wide enough to absorb an upstream corpus revision, narrow enough
# that a differently-defined filter (the real cause of the MVP-2 gap) still
# shows up as a disagreement.
_CLAIM_TOLERANCE_PP = 0.5

# Category 2 spans base 0x205-0x2f6; Group 12 (Finger Movement) is
# 0x216-0x229. Taken from iswa_data's GROUP_START rather than hardcoded.
_GROUP12 = 12
_CATEGORY_5 = 5


@dataclass
class Stage:
    """One pipeline stage's counters. ``attempted`` is the number of items
    that REACHED this stage (i.e. survived every earlier one), so the
    success rates below are conditional, not fractions of the whole
    corpus -- both forms are reported."""

    name: str
    attempted: int = 0
    succeeded: int = 0
    seconds: float = 0.0
    reasons: Counter[str] = field(default_factory=Counter)

    @property
    def failed(self) -> int:
        return self.attempted - self.succeeded

    @property
    def rate(self) -> float:
        return self.succeeded / self.attempted if self.attempted else 0.0

    def as_dict(self, corpus_total: int) -> dict[str, object]:
        return {
            "stage": self.name,
            "attempted": self.attempted,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "success_rate_of_attempted": round(self.rate, 6),
            "success_rate_of_corpus": round(self.succeeded / corpus_total, 6) if corpus_total else 0.0,
            "seconds": round(self.seconds, 3),
            "failure_reasons": dict(self.reasons.most_common()),
        }


@dataclass
class Results:
    corpus_rows: int = 0
    parse: Stage = field(default_factory=lambda: Stage("FSW Parsing"))
    mapping: Stage = field(default_factory=lambda: Stage("Symbol Mapping (per sign)"))
    timeline: Stage = field(default_factory=lambda: Stage("Timeline Construction"))
    generation: Stage = field(default_factory=lambda: Stage("Animation Generation"))
    # Symbol-level (token) counters, independent of the per-sign view.
    symbol_tokens: int = 0
    symbol_mapped: int = 0
    symbol_reasons: Counter[str] = field(default_factory=Counter)
    tokens_by_category: Counter[int] = field(default_factory=Counter)
    bases_seen: set[int] = field(default_factory=set)
    symbols_per_sign: Counter[int] = field(default_factory=Counter)
    # Counted at stage 3, not derived from stage 4's track tally, so it
    # stays correct when --generation-limit samples the timelines.
    timelines_by_track_count: Counter[int] = field(default_factory=Counter)
    frames_total: int = 0
    tracks_total: int = 0
    generation_sampled: bool = False


def load_corpus(path: Path, limit: int | None) -> list[str]:
    if not path.exists():
        raise SystemExit(f"corpus not found at {path} -- run `python scripts/fetch_corpus.py` first")
    csv.field_size_limit(_CSV_FIELD_LIMIT)
    rows: list[str] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or FSW_COLUMN not in reader.fieldnames:
            raise SystemExit(f"column {FSW_COLUMN!r} missing from {path}")
        for row in reader:
            fsw = (row[FSW_COLUMN] or "").strip()
            if fsw:
                rows.append(fsw)
            if limit is not None and len(rows) >= limit:
                break
    return rows


def evaluate(corpus: list[str], fps: int, generation_limit: int | None, seed: int) -> Results:
    results = Results(corpus_rows=len(corpus))

    # Stage 3 outputs are kept so stage 4 can run over them without redoing
    # stages 1-3; only the timeline object is retained, never pose frames.
    timelines: list[SignTimeline] = []

    for fsw in corpus:
        # --- Stage 1: FSW parsing (string -> AST). ---
        results.parse.attempted += 1
        started = time.perf_counter()
        try:
            ast = parse_fsw_to_ast(fsw)
        except Exception as exc:  # noqa: BLE001 -- taxonomy of real failures is the point
            results.parse.seconds += time.perf_counter() - started
            results.parse.reasons[type(exc).__name__] += 1
            continue
        results.parse.seconds += time.perf_counter() - started
        results.parse.succeeded += 1

        # --- Stage 2: symbol mapping, per symbol AND per sign. ---
        results.mapping.attempted += 1
        results.symbols_per_sign[len(ast.symbols)] += 1
        started = time.perf_counter()
        positioned: list[PositionedSymbol] = []
        sign_ok = True
        for node in ast.symbols:
            results.symbol_tokens += 1
            try:
                parsed = parse_fsw_symbol_key(node.key)
                results.tokens_by_category[category_of(parsed.base_hex)] += 1
                results.bases_seen.add(parsed.base_hex)
                symbol = build_symbol(parsed)
            except Exception as exc:  # noqa: BLE001
                results.symbol_reasons[str(exc).split(" (base ")[0][:80]] += 1
                sign_ok = False
                continue
            results.symbol_mapped += 1
            if isinstance(symbol, FSWRenderableSymbol):
                positioned.append(PositionedSymbol(symbol=symbol, x=node.x, y=node.y))
        results.mapping.seconds += time.perf_counter() - started
        if not sign_ok:
            results.mapping.reasons["at least one symbol unmapped"] += 1
            continue
        results.mapping.succeeded += 1

        # --- Stage 3: timeline construction. ---
        results.timeline.attempted += 1
        started = time.perf_counter()
        try:
            timeline = build_timeline(tuple(positioned))
        except Exception as exc:  # noqa: BLE001
            results.timeline.seconds += time.perf_counter() - started
            results.timeline.reasons[_classify_timeline_failure(str(exc))] += 1
            continue
        results.timeline.seconds += time.perf_counter() - started
        results.timeline.succeeded += 1
        results.timelines_by_track_count[len(timeline.tracks)] += 1
        timelines.append(timeline)

    # --- Stage 4: animation generation. ---
    if generation_limit is not None and len(timelines) > generation_limit:
        random.Random(seed).shuffle(timelines)
        timelines = timelines[:generation_limit]
        results.generation_sampled = True
    for timeline in timelines:
        results.generation.attempted += 1
        started = time.perf_counter()
        try:
            frames = sample(timeline, fps=fps)
        except Exception as exc:  # noqa: BLE001
            results.generation.seconds += time.perf_counter() - started
            results.generation.reasons[type(exc).__name__] += 1
            continue
        results.generation.seconds += time.perf_counter() - started
        results.generation.succeeded += 1
        results.frames_total += len(frames)
        results.tracks_total += len(timeline.tracks)

    return results


def verify_cited_claims(corpus: list[str], results: Results) -> list[dict[str, object]]:
    """Recompute every corpus percentage fsw_r's source asserts, so each one
    is either reproduced or corrected instead of being quoted on trust.

    Each claim is recomputed under the definition its own citation states;
    where a citation is ambiguous about the filter it used, that ambiguity is
    the finding (it is what makes MVP-2's ~20.9% irreproducible), not
    something to tune the filter until it matches."""
    group12_start = GROUP_START[_GROUP12 - 1]
    group12_end = GROUP_START[_GROUP12]  # exclusive

    # Claim 6's "5 leading base symbols" are the ones gen_finger_articulations
    # researched by name; read from the shipped table rather than restated
    # here, so the two cannot drift apart.
    articulations = json.loads(
        (Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "finger_articulations.json")
        .read_text(encoding="utf-8")
    )
    top5 = {
        int(key, 16)
        for key, entry in articulations.items()
        if key != "_meta" and isinstance(entry, dict) and entry.get("name")
    }

    cat5_tokens = cat5_fill0 = cat5_rot07 = 0
    g12_tokens = g12_top5 = 0
    signs_with_g12 = 0
    right_07 = right_815 = left_07 = left_815 = 0

    for fsw in corpus:
        try:
            ast = parse_fsw_to_ast(fsw)
        except Exception:  # noqa: BLE001 -- unparseable signs are counted in stage 1
            continue
        parsed_symbols = []
        for node in ast.symbols:
            try:
                parsed_symbols.append(parse_fsw_symbol_key(node.key))
            except Exception:  # noqa: BLE001
                continue

        has_g12 = False
        hands = [p for p in parsed_symbols if category_of(p.base_hex) == 1]
        for parsed in parsed_symbols:
            category = category_of(parsed.base_hex)
            if category == _CATEGORY_5:
                cat5_tokens += 1
                cat5_fill0 += parsed.fill == 0
                cat5_rot07 += parsed.rotation < 8
            if group12_start <= parsed.base_hex < group12_end:
                has_g12 = True
                g12_tokens += 1
                g12_top5 += parsed.base_hex in top5
        signs_with_g12 += has_g12

        # Category 2 rotation vs. the hand the sign is performed with, only
        # for signs with EXACTLY one Category 1 symbol -- the filter
        # core/movement_symbol.py's own table states, so the hand is known.
        if len(hands) == 1:
            hand_is_right = hands[0].rotation < 8
            for parsed in parsed_symbols:
                if category_of(parsed.base_hex) != 2:
                    continue
                if hand_is_right:
                    right_07 += parsed.rotation < 8
                    right_815 += parsed.rotation >= 8
                else:
                    left_07 += parsed.rotation < 8
                    left_815 += parsed.rotation >= 8

    def pct(numerator: int, denominator: int) -> float:
        return numerator / denominator * 100.0 if denominator else 0.0

    total = results.corpus_rows
    one_track = results.timelines_by_track_count[1]
    measured = {
        # MVP-1 was "one hand": buildable signs whose timeline has exactly
        # one track, counted at stage 3.
        "mvp1_one_hand": pct(one_track, total),
        "mvp2_coverage": pct(results.timeline.succeeded, total),
        "cat5_fill0": pct(cat5_fill0, cat5_tokens),
        "cat5_rotation_0_7": pct(cat5_rot07, cat5_tokens),
        "group12_sign_share": pct(signs_with_g12, results.parse.succeeded),
        "group12_top5_tokens": pct(g12_top5, g12_tokens),
        "cat2_right_rot_0_7": pct(right_07, right_07 + right_815),
        "cat2_left_rot_0_7": pct(left_07, left_07 + left_815),
    }

    rows: list[dict[str, object]] = []
    for key, where, cited, definition in _CITED_CLAIMS:
        value = measured[key]
        rows.append(
            {
                "claim": key,
                "cited_in": where,
                "definition_measured_here": definition,
                "cited_pct": cited,
                "measured_pct": round(value, 2),
                "delta_pp": round(value - cited, 2),
                "reproduced": abs(value - cited) <= _CLAIM_TOLERANCE_PP,
            }
        )
    return rows


def build_report(
    results: Results, fps: int, seed: int, claims: list[dict[str, object]] | None = None
) -> dict[str, object]:
    total = results.corpus_rows
    stages = [results.parse, results.mapping, results.timeline, results.generation]
    mean_symbols = results.symbol_tokens / results.parse.succeeded if results.parse.succeeded else 0.0
    return {
        "_meta": {
            "corpus": "sign-language-processing/signbank-plus data/raw.csv (see scripts/fetch_corpus.py)",
            "corpus_role": (
                "pipeline INPUT only -- supplies real FSW strings; nothing in it is used as "
                "ground truth for what the output animation should be, so this is a "
                "functional/process evaluation, not an accuracy evaluation"
            ),
            "fps": fps,
            "generation_sampled": results.generation_sampled,
            "generation_sample_seed": seed if results.generation_sampled else None,
            "generated_by": "scripts/eval_corpus_coverage.py",
        },
        "corpus_signs": total,
        "stages": [stage.as_dict(total) for stage in stages],
        "symbol_level": {
            "symbol_tokens": results.symbol_tokens,
            "symbols_mapped": results.symbol_mapped,
            "symbols_unmapped": results.symbol_tokens - results.symbol_mapped,
            "mapping_rate": round(results.symbol_mapped / results.symbol_tokens, 6)
            if results.symbol_tokens
            else 0.0,
            "mean_symbols_per_parsed_sign": round(mean_symbols, 3),
            "failure_reasons": dict(results.symbol_reasons.most_common()),
            "tokens_by_category": {
                f"{cat} {_CATEGORY_NAME[cat]}": results.tokens_by_category[cat] for cat in range(1, 8)
            },
        },
        "library_exercise": {
            "distinct_base_symbols_used": len(results.bases_seen),
            "iswa_base_symbols": ISWA_BASE_SYMBOLS,
            "fraction_of_library_used": round(len(results.bases_seen) / ISWA_BASE_SYMBOLS, 6),
        },
        "generation_output": {
            "frames_total": results.frames_total,
            "mean_frames_per_sign": round(results.frames_total / results.generation.succeeded, 3)
            if results.generation.succeeded
            else 0.0,
            "mean_tracks_per_sign": round(results.tracks_total / results.generation.succeeded, 3)
            if results.generation.succeeded
            else 0.0,
        },
        "cited_claims": claims or [],
        "symbols_per_sign_distribution": {
            str(k): v for k, v in sorted(results.symbols_per_sign.items())
        },
    }


def render_markdown(
    results: Results, fps: int, seed: int, claims: list[dict[str, object]] | None = None
) -> str:
    total = results.corpus_rows
    stages = [results.parse, results.mapping, results.timeline, results.generation]

    lines: list[str] = []
    lines.append("# FSW Corpus Coverage Evaluation")
    lines.append("")
    lines.append(
        "Corpus: sign-language-processing/signbank-plus `data/raw.csv` "
        "(see `scripts/fetch_corpus.py`)  "
    )
    lines.append(f"Signs: **{total:,}**  |  fps: {fps}")
    lines.append("")
    lines.append(
        "Functional/process evaluation: each stage is scored on whether it produced an "
        "output at all, never on whether that output is the semantically correct "
        "animation. The corpus is pipeline INPUT only -- nothing in it is used as "
        "ground truth."
    )
    lines.append("")
    lines.append("## Processing stages")
    lines.append("")
    lines.append("| Processing Stage | Input | Successful | Failed | Success Rate | % of corpus |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for stage in stages:
        of_corpus = stage.succeeded / total if total else 0.0
        lines.append(
            f"| {stage.name} | {stage.attempted:,} | {stage.succeeded:,} | {stage.failed:,} "
            f"| {stage.rate:.1%} | {of_corpus:.1%} |"
        )
    lines.append("")
    lines.append(
        "*Input* is the number of signs that REACHED that stage, so *Success Rate* is "
        "conditional; *% of corpus* is the unconditional figure."
    )
    if results.generation_sampled:
        lines.append("")
        lines.append(
            f"> Animation Generation ran on a random sample (seed {seed}), not every timeline."
        )
    lines.append("")
    lines.append("### Failure reasons by stage")
    lines.append("")
    for stage in stages:
        if not stage.reasons:
            continue
        lines.append(f"**{stage.name}**")
        lines.append("")
        for reason, count in stage.reasons.most_common():
            lines.append(f"- {count:,} — {reason}")
        lines.append("")
    lines.append("### Timeline scope funnel")
    lines.append("")
    lines.append(
        "``build_timeline`` raises on the FIRST constraint a sign violates, so the "
        "counts above are mutually exclusive and can be read as a funnel. This shows "
        "where MVP-2 coverage is actually lost -- an intermediate row is the coverage "
        "the framework would reach if only the constraints above it applied."
    )
    lines.append("")
    lines.append("| After applying | Signs remaining | % of corpus |")
    lines.append("|---|---:|---:|")
    remaining = results.timeline.attempted
    lines.append(
        f"| (reached Timeline Construction) | {remaining:,} "
        f"| {remaining / total:.1%} |" if total else f"| (reached) | {remaining:,} | — |"
    )
    for _, label in _TIMELINE_REASONS:
        remaining -= results.timeline.reasons.get(label, 0)
        lines.append(
            f"| — {label} | {remaining:,} | {remaining / total:.1%} |" if total else f"| — {label} | {remaining:,} | — |"
        )
    lines.append("")
    lines.append("## Symbol level")
    lines.append("")
    mapping_rate = results.symbol_mapped / results.symbol_tokens if results.symbol_tokens else 0.0
    mean_symbols = results.symbol_tokens / results.parse.succeeded if results.parse.succeeded else 0.0
    lines.append(f"- symbol tokens: **{results.symbol_tokens:,}**")
    lines.append(f"- mapped to a library symbol: **{results.symbol_mapped:,}** ({mapping_rate:.2%})")
    lines.append(f"- mean symbols per parsed sign: {mean_symbols:.3f}")
    lines.append("")
    lines.append("| Category | Symbol tokens | Share |")
    lines.append("|---|---:|---:|")
    cat_total = sum(results.tokens_by_category.values()) or 1
    for cat in range(1, 8):
        count = results.tokens_by_category[cat]
        lines.append(f"| {cat} {_CATEGORY_NAME[cat]} | {count:,} | {count / cat_total:.1%} |")
    lines.append("")
    if results.symbol_reasons:
        lines.append("Unmapped symbol reasons:")
        lines.append("")
        for reason, count in results.symbol_reasons.most_common():
            lines.append(f"- {count:,} — {reason}")
        lines.append("")
    if claims:
        lines.append("## Previously-cited corpus claims")
        lines.append("")
        lines.append(
            "Every corpus percentage asserted in fsw_r's own source, recomputed here. "
            "Each was originally measured ad hoc and could not be re-derived, which "
            "under the paper's no-invented-data rule makes it unquotable until it "
            "either reproduces or is corrected."
        )
        lines.append("")
        lines.append("| Claim | Cited | Measured | Delta (pp) | Reproduced | Asserted in |")
        lines.append("|---|---:|---:|---:|---|---|")
        for claim in claims:
            ok = "yes" if claim["reproduced"] else "**NO**"
            lines.append(
                f"| `{claim['claim']}` | {claim['cited_pct']}% | {claim['measured_pct']}% "
                f"| {claim['delta_pp']:+} | {ok} | `{claim['cited_in']}` |"
            )
        lines.append("")
        lines.append("Definition measured for each claim:")
        lines.append("")
        for claim in claims:
            lines.append(f"- `{claim['claim']}` — {claim['definition_measured_here']}")
        lines.append("")
    lines.append("## Library exercise")
    lines.append("")
    used = len(results.bases_seen)
    lines.append(
        f"- distinct base symbols appearing in the corpus: **{used}** of "
        f"{ISWA_BASE_SYMBOLS} ({used / ISWA_BASE_SYMBOLS:.1%})"
    )
    lines.append("")
    lines.append("## Generated output")
    lines.append("")
    mean_frames = results.frames_total / results.generation.succeeded if results.generation.succeeded else 0.0
    mean_tracks = results.tracks_total / results.generation.succeeded if results.generation.succeeded else 0.0
    lines.append(f"- pose frames generated: {results.frames_total:,}")
    lines.append(f"- mean frames per sign: {mean_frames:.3f}")
    lines.append(f"- mean animation tracks (hands) per sign: {mean_tracks:.3f}")
    lines.append("")
    return "\n".join(lines)



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "only read the FIRST N signs -- a smoke-test option, NOT a sample: the "
            "corpus is ordered, so a prefix is not representative (measured: the first "
            "5,000 signs give a 20.4%% timeline rate against 14.0%% for the full corpus)"
        ),
    )
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help=f"sampling rate (default {DEFAULT_FPS})")
    parser.add_argument(
        "--generation-limit",
        type=int,
        default=None,
        help="cap stage 4 at N timelines, chosen randomly with --seed (default: all)",
    )
    parser.add_argument("--seed", type=int, default=0, help="seed for --generation-limit sampling")
    args = parser.parse_args()

    corpus = load_corpus(CORPUS_PATH, args.limit)
    print(f"Loaded {len(corpus):,} FSW strings from {CORPUS_PATH}")
    started = time.perf_counter()
    results = evaluate(corpus, fps=args.fps, generation_limit=args.generation_limit, seed=args.seed)
    elapsed = time.perf_counter() - started
    print(f"Processed in {elapsed:.1f}s ({len(corpus) / elapsed:,.0f} signs/s)")

    claims = verify_cited_claims(corpus, results)
    report = build_report(results, fps=args.fps, seed=args.seed, claims=claims)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = REPORT_DIR / "corpus_coverage.json"
    md_path = REPORT_DIR / "corpus_coverage.md"
    with open(json_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    markdown = render_markdown(results, fps=args.fps, seed=args.seed, claims=claims)
    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(markdown)
    print(f"Wrote {json_path}\nWrote {md_path}\n")
    sys.stdout.write(markdown)


if __name__ == "__main__":
    main()
