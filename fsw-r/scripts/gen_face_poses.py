"""Regenerates ``data/face_expression_poses.json`` for ISWA Category 4
(Head & Face) facial-expression symbols.

Provenance, stated honestly: the base-symbol NAMES are authoritative ISWA
names (signbank.org/iswa/<hex>_sg.html). The blend-shape VECTORS are
AUTHORED -- a human reading of each name mapped to the ARKit-52 standard --
NOT measured (there is no dataset keying ISWA face symbols to blend-shapes
the way 3d-hands-benchmark measured hand joints). Only symbols that are a
real facial *deformation* representable in ARKit-52 are authored; airflow /
breath / ears / contact / movement symbols are DEFERRED with a reason,
rather than faked.

The valid ``fill`` values per base come from the authoritative
``iswa_valid_combinations.json`` (the ISWA font cmap), so this file can
never disagree with it. fill nuance (what fill 0 vs 1 *means*) is still
unresolved, so every valid fill of a base currently carries the same
expression -- keyed by (base_hex, fill) so that's a data-only change later.

Run:  python scripts/gen_face_poses.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fsw_r.core.iswa_data import symbol_id_of, valid_combinations_for

# base_hex -> (name, {arkit_blendshape: weight}). Names from signbank.org.
AUTHORED: dict[int, tuple[str, dict[str, float]]] = {
    # ---- Group 23: Brow / Eyes (0x30a-0x329), static brow & eye-openness ----
    0x30A: ("Eyebrows Straight Up", {"browInnerUp": 0.6, "browOuterUpLeft": 0.7, "browOuterUpRight": 0.7}),
    0x30B: ("Eyebrows Straight Neutral", {}),
    0x30C: ("Eyebrows Straight Down", {"browDownLeft": 0.7, "browDownRight": 0.7}),
    0x311: ("Forehead Neutral", {}),
    0x313: ("Forehead Wrinkled", {"browInnerUp": 0.4, "browOuterUpLeft": 0.4, "browOuterUpRight": 0.4}),
    0x314: ("Eyes Open", {}),
    0x315: ("Eyes Squeezed",
            {"eyeBlinkLeft": 0.8, "eyeBlinkRight": 0.8, "eyeSquintLeft": 0.7, "eyeSquintRight": 0.7}),
    0x316: ("Eyes Closed", {"eyeBlinkLeft": 1.0, "eyeBlinkRight": 1.0}),
    0x319: ("Eyes Half Open", {"eyeBlinkLeft": 0.5, "eyeBlinkRight": 0.5}),
    0x31A: ("Eyes Wide Open", {"eyeWideLeft": 0.8, "eyeWideRight": 0.8}),
    0x31B: ("Eyes Half Closed", {"eyeBlinkLeft": 0.5, "eyeBlinkRight": 0.5}),
    # A wink is one eye; which eye is a drawing convention, taken as the right here.
    0x31D: ("Eye Wink (Squeezed Eye Blink)", {"eyeBlinkRight": 1.0, "eyeSquintRight": 0.5}),
    # Eyegaze "straight" bases (0x321-0x326): the stored pose is neutral; the
    # gaze direction comes from `rotation` at runtime via core/eyegaze.py
    # (convention verified against the real ISWA glyph). Curved/circle
    # eyegaze (0x327-0x329) are gaze *movements* and stay deferred.
    0x321: ("Eyegaze Straight Wall Plane", {}),
    0x322: ("Eyegaze Straight Wall Double", {}),
    0x323: ("Eyegaze Straight Wall Alternate", {}),
    0x324: ("Eyegaze Straight Floor Plane", {}),
    0x325: ("Eyegaze Straight Floor Double", {}),
    0x326: ("Eyegaze Straight Floor Alternate", {}),
    # ---- Group 25: Mouth / Lips (0x33b-0x355), 27 shape symbols ----
    0x33B: ("Mouth Closed Neutral", {}),
    0x33C: ("Mouth Closed Forward", {"mouthPucker": 0.4}),
    0x33D: ("Mouth Closed Contact", {"mouthPressLeft": 0.3, "mouthPressRight": 0.3}),
    0x33E: ("Mouth Smile", {"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8}),
    0x33F: ("Mouth Smile Wrinkled",
            {"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8, "cheekSquintLeft": 0.5, "cheekSquintRight": 0.5}),
    0x340: ("Mouth Smile Open", {"mouthSmileLeft": 0.7, "mouthSmileRight": 0.7, "jawOpen": 0.3}),
    0x341: ("Mouth Frown", {"mouthFrownLeft": 0.8, "mouthFrownRight": 0.8}),
    0x342: ("Mouth Frown Wrinkled",
            {"mouthFrownLeft": 0.8, "mouthFrownRight": 0.8, "cheekSquintLeft": 0.4, "cheekSquintRight": 0.4}),
    0x343: ("Mouth Frown Open", {"mouthFrownLeft": 0.7, "mouthFrownRight": 0.7, "jawOpen": 0.3}),
    0x344: ("Mouth Open Circle", {"jawOpen": 0.4, "mouthFunnel": 0.5}),
    0x345: ("Mouth Open Forward", {"jawOpen": 0.3, "mouthFunnel": 0.4, "mouthPucker": 0.2}),
    0x346: ("Mouth Open Wrinkled",
            {"jawOpen": 0.4, "mouthFunnel": 0.4, "cheekSquintLeft": 0.3, "cheekSquintRight": 0.3}),
    0x347: ("Mouth Open Oval", {"jawOpen": 0.5, "mouthFunnel": 0.3}),
    0x348: ("Mouth Open Oval Wrinkled",
            {"jawOpen": 0.5, "mouthFunnel": 0.3, "cheekSquintLeft": 0.3, "cheekSquintRight": 0.3}),
    0x349: ("Mouth Open Oval Yawn", {"jawOpen": 0.8, "mouthFunnel": 0.2}),
    0x34A: ("Mouth Open Rectangle", {"jawOpen": 0.5, "mouthStretchLeft": 0.4, "mouthStretchRight": 0.4}),
    0x34B: ("Mouth Open Rectangle Wrinkled",
            {"jawOpen": 0.5, "mouthStretchLeft": 0.4, "mouthStretchRight": 0.4,
             "cheekSquintLeft": 0.3, "cheekSquintRight": 0.3}),
    0x34C: ("Mouth Open Rectangle Yawn", {"jawOpen": 0.8, "mouthStretchLeft": 0.4, "mouthStretchRight": 0.4}),
    0x34D: ("Mouth Kiss", {"mouthPucker": 0.9}),
    0x34E: ("Mouth Kiss Forward", {"mouthPucker": 0.8, "mouthFunnel": 0.3}),
    0x34F: ("Mouth Kiss Wrinkled", {"mouthPucker": 0.9, "cheekSquintLeft": 0.3, "cheekSquintRight": 0.3}),
    0x350: ("Mouth Tense", {"mouthPressLeft": 0.5, "mouthPressRight": 0.5, "mouthClose": 0.2}),
    0x351: ("Mouth Tense Forward", {"mouthPressLeft": 0.4, "mouthPressRight": 0.4, "mouthPucker": 0.3}),
    0x352: ("Mouth Tense Sucked", {"mouthRollLower": 0.6, "mouthRollUpper": 0.6}),
    0x353: ("Lips Pressed Together", {"mouthPressLeft": 0.6, "mouthPressRight": 0.6, "mouthClose": 0.3}),
    0x354: ("Lip Lower Over Upper", {"mouthShrugLower": 0.5, "mouthRollUpper": 0.4}),
    0x355: ("Lip Upper Over Lower", {"mouthShrugUpper": 0.5, "mouthRollLower": 0.4}),
    # ---- Group 24: Cheeks / Nose (0x32a-0x33a), facial-deformation subset ----
    0x32A: ("Cheeks Puffed", {"cheekPuff": 0.8}),
    0x32B: ("Cheeks Neutral", {}),
    # ARKit-52 has a single cheekSquint target and can't localize the
    # high/middle/low position, so these three share it (documented limit).
    0x32D: ("Tense Cheeks High", {"cheekSquintLeft": 0.6, "cheekSquintRight": 0.6}),
    0x32E: ("Tense Cheeks Middle", {"cheekSquintLeft": 0.6, "cheekSquintRight": 0.6}),
    0x32F: ("Tense Cheeks Low", {"cheekSquintLeft": 0.6, "cheekSquintRight": 0.6}),
    0x331: ("Nose Neutral", {}),
    0x333: ("Nose Wrinkles", {"noseSneerLeft": 0.6, "noseSneerRight": 0.6}),
    # ---- Group 26: Tongue (0x359-0x36c), tongue-protrusion subset ----
    # ARKit-52's only tongue target is a single non-directional `tongueOut`,
    # so only "tongue is protruding" is representable (as an amount); the
    # tongue's *direction* (these bases' rotation) and inside-mouth detail
    # are not. Intensity gradient reflects how far the tongue is out.
    0x359: ("Tongue Sticks Out Far", {"tongueOut": 1.0}),
    0x35B: ("Tongue Tip Between Lips", {"tongueOut": 0.4}),
    0x35F: ("Tongue Center Sticks Out", {"tongueOut": 0.9}),
}

# base_hex -> reason it is NOT authored (kept for the _meta record so the
# gaps are explicit, not silent). registry.py raises for these.
DEFERRED: dict[int, str] = {
    # Group 23 (Brow/Eyes/Eyegaze)
    0x30D: "Dreamy Eyebrows Neutral Down -- asymmetric/angled brow, L/R ARKit mapping unconfirmed",
    0x30E: "Dreamy Eyebrows Down Neutral -- asymmetric/angled brow, L/R ARKit mapping unconfirmed",
    0x30F: "Dreamy Eyebrows Up Neutral -- asymmetric/angled brow, L/R ARKit mapping unconfirmed",
    0x310: "Dreamy Eyebrows Neutral-Up -- asymmetric/angled brow, L/R ARKit mapping unconfirmed",
    0x312: "Forehead Contact -- a contact/location annotation, not a deformation",
    0x317: "Eye Blink Single -- a blink is a movement (needs animation)",
    0x318: "Eye Blinks Multiple -- a movement (needs animation)",
    0x31C: "Eyes Widening Movement -- a movement (needs animation)",
    0x31E: "Eyelashes Up -- ARKit-52 has no eyelash target",
    0x31F: "Eyelashes Down -- ARKit-52 has no eyelash target",
    0x320: "Eyelashes Fluttering -- no ARKit target + movement",
    0x327: "Eyegaze Curved Wall Plane -- gaze direction + curve/movement",
    0x328: "Eyegaze Curved Floor Plane -- gaze direction + curve/movement",
    0x329: "Eyegaze Circles Wall Plane -- gaze direction + movement",
    # Group 24
    0x32C: "Cheeks Sucked -- no ARKit-52 target for hollowed cheeks",
    0x330: "Ears -- ARKit-52 has no ear targets (not a facial deformation)",
    0x332: "Nose Contact -- a contact/location annotation, not a deformation",
    0x334: "Nose Wiggles -- a movement (needs animation), not a static pose",
    0x335: "Air Blowing Out -- airflow annotation, not a facial deformation",
    0x336: "Air Sucking In -- airflow annotation",
    0x337: "Air Blow Small Rotations -- directional airflow annotation",
    0x338: "Air Suck Small Rotations -- directional airflow annotation",
    0x339: "Breath Exhale -- breath annotation",
    0x33A: "Breath Inhale -- breath annotation",
    # Group 25
    0x356: "Mouth Corners -- annotation mark, not an expression",
    0x357: "Mouth Wrinkles Single -- annotation mark, not an expression",
    0x358: "Mouth Wrinkles Double -- annotation mark, not an expression",
    # Group 26 (Tongue/Teeth/Chin/Neck)
    0x35A: "Tongue Licks Lips -- a movement (needs animation)",
    0x35C: "Tongue Tip Touches Inside Mouth -- inside the mouth, no ARKit target",
    0x35D: "Tongue Inside Mouth Relaxed -- inside the mouth, not visible",
    0x35E: "Tongue Moves Against Cheek -- a movement (needs animation)",
    0x360: "Tongue Center Inside Mouth -- inside the mouth, not visible",
    0x361: "Teeth -- ARKit-52 has no teeth targets",
    0x362: "Teeth Movement -- no ARKit teeth target + movement",
    0x363: "Teeth on Tongue -- no ARKit teeth target",
    0x364: "Teeth on Tongue Movement -- no ARKit teeth target + movement",
    0x365: "Teeth on Lips -- no ARKit teeth target",
    0x366: "Teeth on Lips Movement -- no ARKit teeth target + movement",
    0x367: "Teeth Bite Lips -- no ARKit teeth target",
    0x368: "Jaw Movement Wall Plane -- a movement (needs animation)",
    0x369: "Jaw Movement Floor Plane -- a movement (needs animation)",
    0x36A: "Neck -- not a face deformation (neck; closer to Trunk/Head)",
    0x36B: "Hair -- not a facial feature",
    0x36C: "Excitement -- abstract annotation, not a specific deformation",
}


def build() -> dict[str, object]:
    out: dict[str, object] = {
        "_meta": {
            "standard": "ARKit 52 blendshapes",
            "categories": "ISWA Category 4 (Head & Face): Group 23 (Brow/Eyes subset), Group 24 "
                          "(Cheeks/Nose subset), Group 25 (Mouth/Lips), Group 26 (Tongue subset)",
            "rotation_note": "Face poses are keyed by (base_hex, fill) -- rotation is decoration for most "
                             "bases. EXCEPTION: the eyegaze 'straight' bases (0x321-0x326) store a neutral "
                             "pose and get their gaze direction from rotation at runtime (core/eyegaze.py; "
                             "convention verified against the real ISWA glyph). For the tongue bases that "
                             "use rotation as direction, that direction is not representable in ARKit-52 "
                             "(single non-directional tongueOut) and is collapsed.",
            "names_source": "signbank.org ISWA 2010 reference (<hex>_sg.html) -- authoritative ISWA names",
            "values_source": "AUTHORED, not measured -- each blend-shape vector is a human reading of the "
                             "symbol's ISWA name mapped to ARKit-52. No dataset keys ISWA face symbols to "
                             "blend-shapes (unlike hand_joint_poses.json, which is MediaPipe-measured). "
                             "Confidence is lower; treat as a first interpretive pass.",
            "fills_source": "valid fills per base come from iswa_valid_combinations.json (the ISWA font cmap)",
            "fill_nuance": "UNRESOLVED: the semantic difference between a base's fills is not yet confirmed "
                           "from the SignWriting Alphabet Manual, so every valid fill carries the same "
                           "expression. Keyed by (base_hex, fill) so this becomes a data-only change later.",
            "deferred": {f"{b:x}": reason for b, reason in sorted(DEFERRED.items())},
            "generated_by": "scripts/gen_face_poses.py",
        }
    }
    for base_hex in sorted(AUTHORED):
        name, blend = AUTHORED[base_hex]
        symbol_id = symbol_id_of(base_hex)
        fills = sorted(valid_combinations_for(base_hex).fills)
        out[f"{base_hex:x}"] = {
            "symbol_id": symbol_id,
            "name": name,
            "source": f"name from signbank {symbol_id}; blend-shapes authored (ARKit-52)",
            "fills": {str(f): dict(blend) for f in fills},
        }
    return out


def main() -> None:
    target = Path(__file__).resolve().parent.parent / "src" / "fsw_r" / "data" / "face_expression_poses.json"
    target.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target} with {len(AUTHORED)} authored base symbols ({len(DEFERRED)} deferred)")


if __name__ == "__main__":
    main()
