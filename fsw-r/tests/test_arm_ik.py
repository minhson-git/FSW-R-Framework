from __future__ import annotations

import numpy as np
import pytest

from fsw_r.export.arm_ik import POLE_DIRECTION_LEFT, POLE_DIRECTION_RIGHT, solve_two_bone_ik
from fsw_r.export.body_geometry import FOREARM_LENGTH, UPPER_ARM_LENGTH, shoulder_position

_L1 = UPPER_ARM_LENGTH
_L2 = FOREARM_LENGTH


@pytest.mark.parametrize("is_right", [True, False])
def test_c1_elbow_bends_toward_the_pole_direction(is_right: bool) -> None:
    shoulder = shoulder_position(is_right)
    pole = POLE_DIRECTION_RIGHT if is_right else POLE_DIRECTION_LEFT
    # A wrist straight out to the side (perpendicular to the pole plane
    # isn't guaranteed, but any reachable wrist not exactly along the pole
    # axis works) -- within reach so the bend is real, not degenerate.
    wrist = shoulder + np.array([0.0, -(_L1 + _L2) * 0.6, 0.0])

    elbow = solve_two_bone_ik(shoulder, wrist, pole, _L1, _L2)
    elbow_direction = (elbow - shoulder) / np.linalg.norm(elbow - shoulder)
    pole_direction = pole / np.linalg.norm(pole)

    # The elbow direction must lean toward the pole direction, not away
    # from it -- i.e. positive dot product with the pole's own component
    # perpendicular to the aim direction.
    aim = (wrist - shoulder) / np.linalg.norm(wrist - shoulder)
    pole_perp = pole_direction - aim * np.dot(pole_direction, aim)
    elbow_perp = elbow_direction - aim * np.dot(elbow_direction, aim)
    assert np.dot(pole_perp, elbow_perp) > 0


@pytest.mark.parametrize("is_right", [True, False])
def test_c2_bone_lengths_are_preserved_within_reach(is_right: bool) -> None:
    shoulder = shoulder_position(is_right)
    pole = POLE_DIRECTION_RIGHT if is_right else POLE_DIRECTION_LEFT
    # Well within [|L1-L2|, L1+L2] -- both segment lengths must hold exactly.
    wrist = shoulder + np.array([0.3, -(_L1 + _L2) * 0.7, 0.2])

    elbow = solve_two_bone_ik(shoulder, wrist, pole, _L1, _L2)

    assert np.linalg.norm(elbow - shoulder) == pytest.approx(_L1, abs=1e-6)
    assert np.linalg.norm(wrist - elbow) == pytest.approx(_L2, abs=1e-6)


def test_c3_wrist_beyond_max_reach_does_not_raise_or_nan() -> None:
    shoulder = shoulder_position(is_right=True)
    wrist = shoulder + np.array([_L1 + _L2 + 100.0, 0.0, 0.0])
    elbow = solve_two_bone_ik(shoulder, wrist, POLE_DIRECTION_RIGHT, _L1, _L2)
    assert np.all(np.isfinite(elbow))
    # Straightens out: elbow lies on the shoulder->wrist ray, at distance L1.
    assert np.linalg.norm(elbow - shoulder) == pytest.approx(_L1, abs=1e-6)


def test_c3_wrist_closer_than_min_reach_does_not_raise_or_nan() -> None:
    shoulder = shoulder_position(is_right=True)
    min_reach = abs(_L1 - _L2)
    wrist = shoulder + np.array([min_reach * 0.1, 0.0, 0.0])  # well inside the fold limit
    elbow = solve_two_bone_ik(shoulder, wrist, POLE_DIRECTION_RIGHT, _L1, _L2)
    assert np.all(np.isfinite(elbow))


def test_c3_wrist_coincident_with_shoulder_does_not_raise_or_nan() -> None:
    shoulder = shoulder_position(is_right=True)
    elbow = solve_two_bone_ik(shoulder, shoulder.copy(), POLE_DIRECTION_RIGHT, _L1, _L2)
    assert np.all(np.isfinite(elbow))
    assert np.linalg.norm(elbow - shoulder) == pytest.approx(_L1, abs=1e-6)


def test_pole_directions_are_named_constants_mirrored_across_x() -> None:
    assert POLE_DIRECTION_RIGHT[0] == -POLE_DIRECTION_LEFT[0]
    assert POLE_DIRECTION_RIGHT[1] == POLE_DIRECTION_LEFT[1]
    assert POLE_DIRECTION_RIGHT[2] == POLE_DIRECTION_LEFT[2]


def test_no_general_iterative_solver_is_used() -> None:
    # Acceptance criterion 5: grep-verifiable, but also checked directly
    # here so a regression fails a test, not just a manual grep. Checks
    # actual IMPORT statements (AST), not just substring absence -- the
    # module's own docstring legitimately mentions "scipy.optimize" by
    # name to explain what it deliberately does NOT use.
    import ast
    import inspect

    from fsw_r.export import arm_ik

    tree = ast.parse(inspect.getsource(arm_ik))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    } | {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any(m and "optimize" in m for m in imported_modules)
