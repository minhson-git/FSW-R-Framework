# FSW Corpus Coverage Evaluation

Corpus: sign-language-processing/signbank-plus `data/raw.csv` (see `scripts/fetch_corpus.py`)  
Signs: **257,801**  |  fps: 30

Functional/process evaluation: each stage is scored on whether it produced an output at all, never on whether that output is the semantically correct animation. The corpus is pipeline INPUT only -- nothing in it is used as ground truth.

## Processing stages

| Processing Stage | Input | Successful | Failed | Success Rate | % of corpus |
|---|---:|---:|---:|---:|---:|
| FSW Parsing | 257,801 | 257,801 | 0 | 100.0% | 100.0% |
| Symbol Mapping (per sign) | 257,801 | 232,958 | 24,843 | 90.4% | 90.4% |
| Timeline Construction | 232,958 | 36,079 | 196,879 | 15.5% | 14.0% |
| Animation Generation | 36,079 | 36,079 | 0 | 100.0% | 14.0% |

*Input* is the number of signs that REACHED that stage, so *Success Rate* is conditional; *% of corpus* is the unconditional figure.

### Failure reasons by stage

**Symbol Mapping (per sign)**

- 24,843 — at least one symbol unmapped

**Timeline Construction**

- 135,362 — symbol outside Categories 1-2
- 23,986 — not 1-2 hand symbols
- 23,190 — two movements on one hand
- 14,341 — two postures on one hand

### Timeline scope funnel

``build_timeline`` raises on the FIRST constraint a sign violates, so the counts above are mutually exclusive and can be read as a funnel. This shows where MVP-2 coverage is actually lost -- an intermediate row is the coverage the framework would reach if only the constraints above it applied.

| After applying | Signs remaining | % of corpus |
|---|---:|---:|
| (reached Timeline Construction) | 232,958 | 90.4% |
| — symbol outside Categories 1-2 | 97,596 | 37.9% |
| — not 1-2 hand symbols | 73,610 | 28.6% |
| — two postures on one hand | 59,269 | 23.0% |
| — two movements on one hand | 36,079 | 14.0% |

## Symbol level

- symbol tokens: **3,407,742**
- mapped to a library symbol: **3,289,124** (96.52%)
- mean symbols per parsed sign: 13.218

| Category | Symbol tokens | Share |
|---|---:|---:|
| 1 Hands | 1,415,887 | 41.5% |
| 2 Movement | 1,129,847 | 33.2% |
| 3 Dynamics | 76,604 | 2.2% |
| 4 Head & Face | 511,366 | 15.0% |
| 5 Trunk & Limb | 155,420 | 4.6% |
| 6 Location | 367 | 0.0% |
| 7 Punctuation | 118,251 | 3.5% |

Unmapped symbol reasons:

- 118,251 — Category 7 is not supported yet
- 367 — Category 6 is not supported yet

## Previously-cited corpus claims

Every corpus percentage asserted in fsw_r's own source, recomputed here. Each was originally measured ad hoc and could not be re-derived, which under the paper's no-invented-data rule makes it unquotable until it either reproduces or is corrected.

| Claim | Cited | Measured | Delta (pp) | Reproduced | Asserted in |
|---|---:|---:|---:|---|---|
| `mvp1_one_hand` | 6.2% | 6.65% | +0.45 | yes | `timeline/build.py` |
| `mvp2_coverage` | 20.9% | 13.99% | -6.91 | **NO** | `timeline/build.py` |
| `cat5_fill0` | 92.5% | 92.47% | -0.03 | yes | `core/body_types.py, core/body_symbol.py` |
| `cat5_rotation_0_7` | 88.7% | 88.67% | -0.03 | yes | `core/body_types.py, core/body_symbol.py` |
| `group12_sign_share` | 16.8% | 16.83% | +0.03 | yes | `core/movement_paths.py` |
| `group12_top5_tokens` | 76.1% | 76.12% | +0.02 | yes | `core/movement_paths.py, scripts/gen_finger_articulations.py` |
| `cat2_right_rot_0_7` | 62.2% | 94.0% | +31.8 | **NO** | `core/movement_symbol.py` |
| `cat2_left_rot_0_7` | 58.5% | 94.28% | +35.78 | **NO** | `core/movement_symbol.py` |

Definition measured for each claim:

- `mvp1_one_hand` — signs whose built timeline has exactly 1 track, over all corpus signs
- `mvp2_coverage` — signs whose timeline builds at all, over all corpus signs
- `cat5_fill0` — Category 5 symbol TOKENS with fill == 0, over all Category 5 tokens
- `cat5_rotation_0_7` — Category 5 symbol TOKENS with rotation 0-7, over all Category 5 tokens
- `group12_sign_share` — signs containing >=1 Group 12 symbol, over all parsed signs
- `group12_top5_tokens` — Group 12 TOKENS whose base is one of the 5 named in finger_articulations.json, over all Group 12 tokens
- `cat2_right_rot_0_7` — in signs with EXACTLY ONE Category 1 symbol whose rotation < 8 (a right hand): Category 2 TOKENS with rotation 0-7, over that sign set's Category 2 tokens
- `cat2_left_rot_0_7` — same, for signs whose single Category 1 symbol has rotation >= 8 (a left hand)

## Library exercise

- distinct base symbols appearing in the corpus: **652** of 652 (100.0%)

## Generated output

- pose frames generated: 865,896
- mean frames per sign: 24.000
- mean animation tracks (hands) per sign: 1.525
