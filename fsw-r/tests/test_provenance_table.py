from __future__ import annotations

import json

from gen_provenance_table import (
    DATA_DIR,
    _categories_of_keys,
    _classify,
    _generator_scripts,
    collect,
    render_markdown,
)

# Every bundled data table, and the value layer its own _meta declares.
# Pinned here so a data file that quietly loses its provenance declaration
# (or has it downgraded) fails a test instead of silently weakening the
# paper's traceability table -- and so a NEW data file cannot land without
# someone deciding what layer it belongs to.
EXPECTED_LAYERS = {
    "body_poses.json": "AUTHORED",
    "dynamics_modifiers.json": "AUTHORED",
    "face_expression_poses.json": "AUTHORED",
    "finger_articulations.json": "AUTHORED",
    "hand_joint_poses.json": "MEASURED",
    "iswa_base_symbol_names.json": "REFERENCE",
    "iswa_movement_glyph_sizes.json": "REFERENCE",
    "iswa_symbol_ids.json": "REFERENCE",
    "iswa_valid_combinations.json": "REFERENCE",
    "movement_paths.json": "MAPPED",
}


def test_collect_covers_every_bundled_data_file() -> None:
    rows = collect()
    assert {r.filename for r in rows} == set(EXPECTED_LAYERS)


def test_every_data_file_declares_a_value_layer() -> None:
    """UNDECLARED means a data table states no provenance the rule table
    recognises -- exactly the gap this report exists to surface."""
    rows = collect()
    undeclared = [r.filename for r in rows if r.value_layer == "UNDECLARED"]
    assert undeclared == []


def test_value_layers_match_expected() -> None:
    rows = {r.filename: r.value_layer for r in collect()}
    assert rows == EXPECTED_LAYERS


def test_movement_paths_is_mapped_not_authored() -> None:
    """Regression for a real trap: movement_paths.json's _meta contains the
    string "NOT AUTHORED", so a substring classifier labels the most
    carefully-sourced Category 2 table AUTHORED -- the opposite of the
    truth. It is MAPPED: real ISWA names and glyph sizes put through this
    project's own keyword/scaling rules."""
    row = next(r for r in collect() if r.filename == "movement_paths.json")
    assert row.value_layer == "MAPPED"
    # The trap is real in the shipped data, not hypothetical: assert the
    # phrase is actually present in this file's own _meta, so this test
    # still means something if the wording ever changes.
    meta = json.loads(
        (DATA_DIR / "movement_paths.json").read_text(encoding="utf-8")
    )["_meta"]
    assert "NOT AUTHORED" in json.dumps(meta)


def test_declared_counts_match_actual_entries() -> None:
    """A _meta count that drifted from the file's real entry count would
    make every figure quoted from it suspect."""
    mismatched = [r.filename for r in collect() if r.count_matches is False]
    assert mismatched == []


def test_declared_generator_scripts_all_exist() -> None:
    missing = [(r.filename, r.missing_generators) for r in collect() if r.missing_generators]
    assert missing == []


def test_classification_reports_its_evidence() -> None:
    """The layer label is only defensible if the excerpt that produced it is
    shown; a label with no evidence string would be unverifiable."""
    for row in collect():
        assert row.layer_evidence, f"{row.filename} has a layer but no evidence"


def test_files_declaring_their_own_layer_are_reported_verbatim() -> None:
    """The team's own ``layer:`` wording must survive into the report rather
    than being replaced by this script's vocabulary."""
    declared = {r.filename: r.declared_layer for r in collect() if r.declared_layer}
    assert "iswa_symbol_ids.json" in declared
    assert declared["iswa_symbol_ids.json"].startswith("derived")


def test_classify_prefers_authored_over_authoritative_names() -> None:
    """A file whose NAMES come from an authoritative source but whose
    VALUES are authored must classify as AUTHORED -- the stricter label."""
    layer, evidence = _classify(
        {
            "names_source": "signbank.org ISWA 2010 reference -- authoritative ISWA names",
            "values_source": "AUTHORED, not measured -- a human reading of each name",
        }
    )
    assert layer == "AUTHORED"
    assert "AUTHORED" in evidence


def test_classify_does_not_read_not_authored_as_authored() -> None:
    layer, _ = _classify({"layer": "derived (real ISWA font glyph size), NOT AUTHORED"})
    assert layer != "AUTHORED"


def test_classify_returns_undeclared_when_nothing_matches() -> None:
    layer, evidence = _classify({"source": "somewhere unspecified"})
    assert layer == "UNDECLARED"
    assert evidence == ""


def test_generator_scripts_handles_a_chain_of_scripts() -> None:
    """movement_paths.json is built by three scripts; checking only the
    first would let a deleted one go unnoticed."""
    found = _generator_scripts(
        "scripts/gen_movement_paths.py (path_type, amplitude), "
        "scripts/fetch_base_symbol_names.py (names), scripts/gen_movement_glyph_sizes.py (sizes)"
    )
    assert found == (
        "scripts/gen_movement_paths.py",
        "scripts/fetch_base_symbol_names.py",
        "scripts/gen_movement_glyph_sizes.py",
    )


def test_categories_are_measured_from_keys_not_metadata() -> None:
    payload: dict[str, object] = {"_meta": {"source": "irrelevant"}, "100": {}, "36d": {}}
    assert _categories_of_keys(payload) == (1, 5)


def test_render_markdown_contains_every_file_and_the_integrity_table() -> None:
    markdown = render_markdown(collect())
    for filename in EXPECTED_LAYERS:
        assert filename in markdown
    assert "## Integrity checks" in markdown
    assert "Classification evidence" in markdown
