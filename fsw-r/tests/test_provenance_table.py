from __future__ import annotations

from gen_provenance_table import _classify, _categories_of_keys, collect, render_markdown

# Every bundled data table, and the value layer its own _meta declares.
# Pinned here so a data file that quietly loses its provenance declaration
# (or has it downgraded) fails a test instead of silently weakening the
# paper's traceability table.
EXPECTED_LAYERS = {
    "body_poses.json": "AUTHORED",
    "dynamics_modifiers.json": "AUTHORED",
    "face_expression_poses.json": "AUTHORED",
    "finger_articulations.json": "AUTHORED",
    "hand_joint_poses.json": "MEASURED",
    "iswa_symbol_ids.json": "AUTHORITATIVE",
    "iswa_valid_combinations.json": "AUTHORITATIVE",
    "movement_paths.json": "DERIVED",
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


def test_declared_counts_match_actual_entries() -> None:
    """A _meta count that drifted from the file's real entry count would
    make every figure quoted from it suspect."""
    mismatched = [r.filename for r in collect() if r.count_matches is False]
    assert mismatched == []


def test_declared_generator_scripts_exist() -> None:
    missing = [(r.filename, r.generated_by) for r in collect() if not r.generator_exists]
    assert missing == []


def test_classification_reports_its_evidence() -> None:
    """The layer label is only defensible if the substring that produced it
    is shown; a label with no evidence string would be unverifiable."""
    for row in collect():
        assert row.layer_evidence, f"{row.filename} has a layer but no evidence"


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


def test_classify_returns_undeclared_when_nothing_matches() -> None:
    layer, evidence = _classify({"source": "somewhere unspecified"})
    assert layer == "UNDECLARED"
    assert evidence == ""


def test_categories_are_measured_from_keys_not_metadata() -> None:
    payload: dict[str, object] = {"_meta": {"source": "irrelevant"}, "100": {}, "36d": {}}
    assert _categories_of_keys(payload) == (1, 5)


def test_render_markdown_contains_every_file_and_the_integrity_table() -> None:
    markdown = render_markdown(collect())
    for filename in EXPECTED_LAYERS:
        assert filename in markdown
    assert "## Integrity checks" in markdown
    assert "Classification evidence" in markdown
