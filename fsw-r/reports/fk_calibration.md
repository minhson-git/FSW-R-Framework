# Hand-geometry calibration (thumb constants, held-out)

Seed **42**, stratified by ISWA group, train **183** / test **78**.
Objective: MPJPE (mean per-symbol) after validation/normalization.normalize_landmarks (size=150).
Optimizer: scipy Nelder-Mead, single start x0=[26.0, 15.0, 0.0, -65.0, -20.0], no restarts.

## The four numbers (MPJPE, normalized size=150)

| | train | test |
|---|---|---|
| before | 48.97 | 48.14 |
| after | 45.83 | 45.07 |

Held-out (test) relative improvement: **6.4%** (train 6.4%). Meaningful (>= 5%): **True**.

## Baselines recomputed on the SAME test set
- average_pose_baseline: 59.07
- one_pose_per_group_baseline: 55.67

## Fitted thumb constants (FITTED origin -- from data, not a citation)
- `_THUMB_BASE_OFFSET_MM` raw ratio: [27.216, 15.625, 0.001] (was [26.0, 15.0, 0.0])
- `_THUMB_BASE_ROTATION` zy deg: [-29.7, -24.56] (was [-65.0, -20.0])
- optimizer success: True, iterations: 150
