from __future__ import annotations

import pytest

from fsw_r.timeline.anchor import anchor


def test_smaller_y_gives_a_higher_position() -> None:
    """E1 -- the single most important test in the timeline package. y
    increases DOWNWARD in signbox coordinates (confirmed against
    SignBank+: head symbols' median y=483 is smaller than hand symbols'
    median y=496, and the head sits above the hands on the body). Getting
    this sign wrong flips every gesture upside down while every other
    test still passes -- nothing else would look "obviously broken" the
    way a mirrored left/right would."""
    higher_on_page = anchor(500, 400)  # smaller y
    lower_on_page = anchor(500, 600)  # larger y
    assert higher_on_page[1] > lower_on_page[1]


def test_anchor_normalization() -> None:
    # E2
    assert anchor(500, 500) == pytest.approx([0.0, 0.0, 0.0])
    assert anchor(750, 500) == pytest.approx([1.0, 0.0, 0.0])
    assert anchor(500, 250) == pytest.approx([0.0, 1.0, 0.0])


def test_anchor_x_axis_direction() -> None:
    # x increases to the right, u increases the same way -- not inverted
    # (only y/v is inverted, per test_smaller_y_gives_a_higher_position).
    right_of_center = anchor(600, 500)
    left_of_center = anchor(400, 500)
    assert right_of_center[0] > left_of_center[0]
