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

## Library exercise

- distinct base symbols appearing in the corpus: **652** of 652 (100.0%)

## Generated output

- pose frames generated: 865,896
- mean frames per sign: 24.000
- mean animation tracks (hands) per sign: 1.525
