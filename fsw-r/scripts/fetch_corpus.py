"""Downloads the FSW evaluation corpus (``raw.csv`` from SignBank+) into
``data/external/`` (repo-relative, gitignored -- see ``.gitignore``'s
``**/data/external/``; the file is ~83 MB and never committed).

**Provenance:** ``sign-language-processing/signbank-plus``, file
``data/raw.csv`` -- the raw SignBank export that repo publishes, one row
per sign, with the Formal SignWriting string in the ``sign_writing``
column. This is the SAME corpus several of this project's existing
measurements already cite (see ``core/fsw_base_symbol.py``,
``core/body_types.py``, ``timeline/build.py``): those numbers were measured
ad hoc during development, whereas ``scripts/eval_corpus_coverage.py``
turns them into a reproducible, committed evaluation.

The corpus is used ONLY as pipeline INPUT -- it supplies real FSW strings
to process. Nothing in it is treated as ground truth for what the output
animation should look like, so this evaluation stays a functional/process
evaluation, not an accuracy one.

Run:  python scripts/fetch_corpus.py
"""

from __future__ import annotations

import argparse
import csv
import sys
import urllib.request
from pathlib import Path

# The exact raw-file URL this script fetches, so a diff can compare against
# it later without re-deriving the org/repo/branch/path.
SOURCE_URL = (
    "https://raw.githubusercontent.com/sign-language-processing/"
    "signbank-plus/main/data/raw.csv"
)

TARGET_PATH = Path(__file__).resolve().parent.parent / "data" / "external" / "signbank_plus_raw.csv"

# The column holding the Formal SignWriting string. Checked after download
# so a moved/renamed column fails loudly here rather than silently
# producing an all-zero evaluation later.
FSW_COLUMN = "sign_writing"

# Independently observed when this script was written, checked below so a
# truncated fetch or an upstream corpus change is visible instead of
# quietly shifting every number in the evaluation report.
EXPECTED_ROWS = 257801

_CSV_FIELD_LIMIT = 10**7


def fetch(target: Path = TARGET_PATH, force: bool = False) -> Path:
    if target.exists() and not force:
        print(f"{target} already exists ({target.stat().st_size:,} bytes) -- use --force to re-download")
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {SOURCE_URL}")
    urllib.request.urlretrieve(SOURCE_URL, target)  # noqa: S310 -- fixed https host
    print(f"Wrote {target} ({target.stat().st_size:,} bytes)")
    return target


def verify(target: Path) -> int:
    """Row count + presence of the FSW column. Returns the row count."""
    csv.field_size_limit(_CSV_FIELD_LIMIT)
    with open(target, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or FSW_COLUMN not in reader.fieldnames:
            raise SystemExit(
                f"column {FSW_COLUMN!r} not found in {target} -- columns are {reader.fieldnames}"
            )
        rows = sum(1 for _ in reader)
    print(f"rows = {rows:,} (expected {EXPECTED_ROWS:,})")
    if rows != EXPECTED_ROWS:
        print(
            f"  ! row count differs from the expected {EXPECTED_ROWS:,} -- the upstream corpus "
            f"may have changed; re-check any figure quoted from a previous run",
            file=sys.stderr,
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="re-download even if the file exists")
    args = parser.parse_args()
    target = fetch(force=args.force)
    verify(target)


if __name__ == "__main__":
    main()
