"""Downloads the evaluation ground truth (``hands.npy``) used by
``scripts/eval_fk_accuracy.py`` into ``data/external/`` (repo-relative,
gitignored -- see ``.gitignore``'s comment; the file is ~18 MB and never
committed).

**Provenance, stated precisely (see PROGRESS.md's evaluation-layer entry
for the full citation with licenses):** this file is NOT
``sign-language-processing/synthetic-signwriting``'s own data -- it is
derived from ``sign-language-processing/3d-hands-benchmark`` v0.10.3, the
SAME source ``data/hand_joint_poses.json`` was already built from (see
PROGRESS.md's "Thay toàn bộ góc khớp đoán bằng dữ liệu thật" entry).
``synthetic-signwriting`` just packages it conveniently as one ``.npy``
array; that packaging is what this script fetches, not a new/different
dataset. Both repos are MIT-licensed.

Only ``numpy`` is a runtime dependency of ``fsw_r`` for reading this file
-- ``synthetic-signwriting`` itself is never installed (per this task's
brief, Part A4).

Run:  python scripts/fetch_ground_truth.py
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

# The exact raw-file URL this script fetches, so a diff can compare against
# it later without re-deriving the org/repo/branch/path.
SOURCE_URL = (
    "https://raw.githubusercontent.com/sign-language-processing/"
    "synthetic-signwriting/master/synthetic_signwriting/hands/hands.npy"
)

TARGET_PATH = Path(__file__).resolve().parent.parent / "data" / "external" / "hands.npy"

# hands.npy's real shape (see eval_fk_accuracy.py's module docstring for
# what each axis means) -- checked after download so a truncated/corrupted
# fetch fails loudly here, not confusingly later inside the eval script.
EXPECTED_SHAPE = (48, 261, 6, 21, 3)


def fetch(target: Path = TARGET_PATH, force: bool = False) -> Path:
    if target.exists() and not force:
        print(f"Already present: {target} (pass --force to re-download)")
        return target

    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}\n  -> {target}")
    try:
        urllib.request.urlretrieve(SOURCE_URL, target)
    except Exception as e:  # noqa: BLE001 -- report clearly, then re-raise
        print(f"FAILED to download ground truth: {type(e).__name__}: {e}", file=sys.stderr)
        raise

    _verify(target)
    print(f"OK: {target} ({target.stat().st_size:,} bytes)")
    return target


def _verify(target: Path) -> None:
    import numpy as np

    array = np.load(target)
    if array.shape != EXPECTED_SHAPE:
        raise ValueError(
            f"{target} has shape {array.shape}, expected {EXPECTED_SHAPE} -- "
            f"download may be truncated/corrupted, or the upstream file changed "
            f"shape (in which case eval_fk_accuracy.py's assumptions need revisiting)"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-download even if already present")
    args = parser.parse_args()
    fetch(force=args.force)


if __name__ == "__main__":
    main()
