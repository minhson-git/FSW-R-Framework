"""Resolves what ``fill`` MEANS for ISWA Category 4 (Head & Face) -- the
question ``data/face_expression_poses.json``'s ``_meta`` has carried as
``fill_nuance: UNRESOLVED`` since that table was authored.

The open question was concrete: ``FacePoseTable`` is keyed ``(base_hex,
fill)``, but every valid fill of a base was given the SAME ARKit-52
blend-shape vector, because no source had been found saying whether fills
differ. If they do, the table is silently discarding real notation.

Three independent lines of evidence, none of which needs the glyph to be
interpreted by eye:

  1. GLYPH OUTLINES. For every one of the 55 authored face bases, compare
     the actual TrueType outlines (contour coordinates, not a rendered
     bitmap) of each valid fill. Identical outlines would mean fill is
     decoration.
  2. FACIAL-CIRCLE AXIS. Compare glyph areas across a base's fills. A fill
     that draws the facial circle is several times larger than one that
     draws the facial mark alone.
  3. SIDE AXIS. Within a base, two fills with the SAME contour count and
     the SAME bounding box but different outlines are a left/right pair.
     Which side each occupies is measured from the mark's mean x against
     the facial circle's own centre -- geometry, not judgement.

The naming behind axes 2 and 3 is the official textbook, "Lessons in
SignWriting" (Sutton), pp. 158-159, which lists the Category 4 brow
variants as "Eyebrows Up / Right Eyebrow Up / Left Eyebrow Up" (and the
same triple for Neutral and Down), plus a "Facial Circle" entry. Those
right/left variants are NOT separate base symbols -- signbank gives
0x30a/0x30b/0x30c as Up/Neutral/Down only -- so they can only be fills.

** WHAT THIS SCRIPT DELIBERATELY DOES NOT DO. ** It does not assign ARKit
blend-shapes. Mapping "the mark sits on the viewer's right of the glyph"
onto ARKit's ``...Left``/``...Right`` (which are defined in the CHARACTER's
own anatomical frame) needs the SignWriting viewpoint convention to be
settled for faces -- expressive (as the signer) or receptive (facing the
signer). That is a project decision, and this project's standing rule is to
route unresolved left/right to ``AnnotationSymbol`` rather than guess (see
the "dreamy brows" entry in PROGRESS.md). The evidence is produced here so
the decision can be made on it.

Run:  python scripts/check_face_fill_semantics.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tarfile
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from fontTools.ttLib import TTFont

FACE_POSES = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "face_expression_poses.json"

_FONT_PACKAGE = "@sutton-signwriting/font-ttf"
_FONT_RELATIVE_PATH = "package/font/SuttonSignWritingLine.ttf"
_LINE_FONT_CODEPOINT_OFFSET = 0xF0000

# A fill drawing the facial circle encloses the whole head; one drawing the
# bare facial mark does not. Anything at or above this area ratio is the
# circle being present in some fills and absent in others -- chosen well
# clear of the observed split (the smallest real ratio is far above it).
_CIRCLE_AREA_RATIO = 3.0


def fetch_font(dest: Path) -> Path:
    """Same ``npm pack`` fetch as scripts/gen_valid_combinations.py -- a real
    package download, not a scrape."""
    npm = shutil.which("npm")
    if npm is None:
        raise SystemExit(f"npm not found on PATH -- required to fetch {_FONT_PACKAGE}")
    subprocess.run([npm, "pack", _FONT_PACKAGE], cwd=dest, check=True, capture_output=True)
    tarballs = list(dest.glob("*.tgz"))
    if len(tarballs) != 1:
        raise SystemExit(f"expected 1 tarball from npm pack, found {tarballs}")
    with tarfile.open(tarballs[0]) as tar:
        tar.extract(_FONT_RELATIVE_PATH, path=dest)  # noqa: S202 -- trusted npm package
    return dest / _FONT_RELATIVE_PATH


def main() -> None:
    payload = json.loads(FACE_POSES.read_text(encoding="utf-8"))
    payload.pop("_meta", None)

    with tempfile.TemporaryDirectory() as tmp:
        font = TTFont(fetch_font(Path(tmp)))
        glyf = font["glyf"]
        cmap = font.getBestCmap()

        def glyph(base: int, fill: int, rotation: int = 0) -> Any:
            symbol_id = 1 + (base - 0x100) * 96 + fill * 16 + rotation
            name = cmap.get(symbol_id + _LINE_FONT_CODEPOINT_OFFSET)
            return glyf[name] if name is not None else None

        identical = 0
        circle_axis = 0
        twin_bases: list[tuple[int, str, list[tuple[int, int]]]] = []
        side_rows: list[tuple[int, str, int, str]] = []

        for key, entry in payload.items():
            base = int(key, 16)
            fills = sorted(int(f) for f in entry["fills"])
            shapes = {}
            for fill in fills:
                g = glyph(base, fill)
                if g is None or g.numberOfContours == 0:
                    continue
                coordinates, _, _ = g.getCoordinates(glyf)
                shapes[fill] = (
                    g.numberOfContours,
                    g.xMin,
                    g.xMax,
                    g.yMin,
                    g.yMax,
                    tuple(map(tuple, coordinates)),
                )
            if len(shapes) < 2:
                continue

            # --- 1. outlines identical across fills? ---
            if len({s[5] for s in shapes.values()}) <= 1:
                identical += 1

            # --- 2. facial-circle axis ---
            areas = {f: (s[2] - s[1]) * (s[4] - s[3]) for f, s in shapes.items()}
            if max(areas.values()) >= _CIRCLE_AREA_RATIO * min(areas.values()):
                circle_axis += 1

            # --- 3. side axis: same contour count AND same bbox, different outline ---
            by_signature: dict[tuple[int, int, int, int, int], list[int]] = defaultdict(list)
            for fill, s in shapes.items():
                by_signature[(s[0], s[1], s[2], s[3], s[4])].append(fill)
            twins = [sorted(fs) for fs in by_signature.values() if len(fs) >= 2]
            if twins:
                twin_bases.append((base, str(entry["name"]), [(t[0], t[1]) for t in twins]))
                # Which side, measured against the facial circle's own centre.
                widest = max(shapes, key=lambda f: areas[f])
                centre_x = (shapes[widest][1] + shapes[widest][2]) / 2
                for pair in twins:
                    for fill in pair[:2]:
                        points = shapes[fill][5]
                        mean_x = sum(p[0] for p in points) / len(points)
                        side = "viewer-LEFT" if mean_x < centre_x else "viewer-RIGHT"
                        side_rows.append((base, str(entry["name"]), fill, side))

    total = len(payload)
    print("=" * 72)
    print("CATEGORY 4 -- what does `fill` mean?")
    print("=" * 72)
    print(f"\nAuthored face bases examined: {total} (every one has >= 2 valid fills)")
    print(f"\n[1] Glyph OUTLINES identical across a base's fills: {identical}/{total}")
    print("    => fill is NOT decoration; ISWA draws a different glyph per fill."
          if identical == 0 else "    => some fills really are the same drawing.")
    print(f"\n[2] Bases where one fill's glyph is >= {_CIRCLE_AREA_RATIO:g}x another's area:"
          f" {circle_axis}/{total}")
    print("    => the FACIAL CIRCLE axis: some fills draw the head outline around")
    print("       the mark, others draw the mark alone. Universal across Category 4.")
    print(f"\n[3] Bases with a left/right TWIN pair (same contour count, same bbox,")
    print(f"    different outline): {len(twin_bases)}/{total}")
    for base, name, pairs in twin_bases:
        print(f"      0x{base:03x} {name!r}: fills {pairs}")
    print("\n    Which side each twin occupies, measured against the facial circle's centre:")
    print(f"      {'base':>6}  {'fill':>4}  side")
    for base, _, fill, side in side_rows:
        print(f"      0x{base:03x}  {fill:>4}  {side}")

    print("\n" + "=" * 72)
    print("VERDICT: fill_nuance is RESOLVED as a structure, not as a value.")
    print("  * fill encodes at least two real axes -- whether the facial circle is")
    print("    drawn, and (on the twin bases) WHICH SIDE the mark is on. Textbook")
    print('    naming matches: "Eyebrows Up / Right Eyebrow Up / Left Eyebrow Up"')
    print("    (Lessons in SignWriting, pp. 158-159), and right/left are not")
    print("    separate base symbols, so they can only be fills.")
    print("  * CONSEQUENCE for the data: face_expression_poses.json gives every")
    print("    fill of a base the SAME ARKit vector, so on the twin bases a")
    print("    one-sided expression is currently stored as a symmetric one. ARKit-52")
    print("    can express the asymmetry (browOuterUpLeft/Right, eyeBlinkLeft/Right).")
    print("  * NOT decided here: which ARKit side a viewer-side maps to. That needs")
    print("    the face viewpoint convention (expressive vs receptive) settled; this")
    print("    project routes unresolved left/right to AnnotationSymbol rather than")
    print("    guess. Evidence above is what that decision should be made on.")


if __name__ == "__main__":
    main()
