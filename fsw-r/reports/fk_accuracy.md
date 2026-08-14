# FK Accuracy Evaluation

## Overall MPJPE (normalized, size=150)
mean=45.60 median=43.29 p75=48.78 p95=61.59 max=192.79

## Baselines
- **fsw_r_261_poses**: mean=45.60 median=43.29 p75=48.78 p95=61.59 max=192.79
- **average_pose_baseline**: mean=61.08 median=59.77 p75=69.45 p95=82.08 max=181.18
- **one_pose_per_group_baseline**: mean=56.77 median=55.44 p75=64.14 p95=78.24 max=196.55

## MPJPE by finger
- **thumb**: mean=63.93 median=56.36 p75=82.51 p95=129.86 max=238.28
- **index**: mean=43.21 median=36.82 p75=51.80 p95=84.48 max=250.02
- **middle**: mean=38.92 median=35.05 p75=51.52 p95=91.84 max=288.91
- **ring**: mean=45.58 median=39.99 p75=56.83 p95=96.47 max=281.15
- **pinky**: mean=47.76 median=41.62 p75=58.20 p95=91.03 max=230.39

## MPJPE by joint type
- **CMC**: mean=54.39 median=52.23 p75=65.33 p95=84.87 max=124.83
- **MCP**: mean=28.33 median=27.10 p75=36.14 p95=53.36 max=154.25
- **PIP**: mean=44.09 median=41.50 p75=51.87 p95=67.60 max=229.05
- **DIP**: mean=49.69 median=44.87 p75=60.56 p95=95.48 max=267.94
- **IP**: mean=63.23 median=61.57 p75=79.67 p95=103.88 max=203.73
- **TIP**: mean=64.65 median=57.48 p75=84.81 p95=133.67 max=288.91

## Occlusion hypothesis (C4)
- Expected order (worst->best): ['ring', 'pinky', 'middle', 'index']
- Observed order (worst->best): ['pinky', 'ring', 'index', 'middle']
- Matches: False

## Index -> base_hex verification (A3)
- Checked 783 (base, fill) pairs
- Invalid pairs found: 14
  - base 0x14d (01-05-002-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x14d (01-05-002-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x14f (01-05-004-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x14f (01-05-004-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x151 (01-05-006-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x151 (01-05-006-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15c (01-05-017-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15c (01-05-017-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15e (01-05-019-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15e (01-05-019-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x1f6 (01-10-002-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x1f6 (01-10-002-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x204 (01-10-016-01): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x204 (01-10-016-01): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]

## Worst 20 symbols
- 01-05-014-01 'Five Fingers Spread Hinge, No Thumb' (0x159): MPJPE=192.79
- 01-05-033-01 'Open Cup' (0x16c): MPJPE=116.99
- 01-05-053-01 'Hinge Thumb Side' (0x180): MPJPE=113.53
- 01-10-002-01 'Thumb Heel' (0x1f6): MPJPE=79.23
- 01-04-008-01 'Four Fingers Unit Hinge' (0x14b): MPJPE=74.33
- 01-05-013-01 'Five Fingers Spread Hinge, Thumb Side' (0x158): MPJPE=72.12
- 01-06-030-01 'Baby Index On Angle' (0x1a3): MPJPE=70.69
- 01-06-029-01 'Baby Index On Hinge' (0x1a2): MPJPE=68.05
- 01-01-003-01 'Index on Cup' (0x102): MPJPE=67.53
- 01-06-022-01 'Baby Thumb on Hinge' (0x19b): MPJPE=67.12
- 01-09-032-01 'Index Thumb Cup' (0x1ec): MPJPE=64.58
- 01-06-010-01 'Baby Down, Ripple Straight' (0x18f): MPJPE=64.56
- 01-06-003-01 'Index Middle Ring on Hinge' (0x188): MPJPE=62.00
- 01-05-051-01 'Small Hinge' (0x17e): MPJPE=61.59
- 01-04-003-01 'Four Fingers Hinge' (0x146): MPJPE=61.43
- 01-02-014-01 'Index Middle Cross On Circle' (0x11b): MPJPE=61.10
- 01-05-019-01 'Flat Thumb Side, Heel' (0x15e): MPJPE=60.78
- 01-05-004-01 'Five Fingers Spread Four Bent Heel' (0x14f): MPJPE=59.92
- 01-08-003-01 'Index Ring Baby on Curlicue' (0x1bc): MPJPE=59.87
- 01-05-055-01 'Hinge No Thumb' (0x182): MPJPE=59.36

## Best 20 symbols
- 01-05-043-01 'Circle' (0x176): MPJPE=27.66
- 01-02-011-01 'Index Middle Unit Cup' (0x118): MPJPE=28.98
- 01-09-033-01 'Index Thumb Cup Open' (0x1ed): MPJPE=30.19
- 01-05-027-01 'Claw' (0x166): MPJPE=31.03
- 01-06-012-01 'Baby Down, Others Circle' (0x191): MPJPE=31.06
- 01-09-027-01 'Index Thumb Curlicue' (0x1e7): MPJPE=31.07
- 01-04-007-01 'Four Fingers Unit Bent' (0x14a): MPJPE=31.12
- 01-03-029-01 'Index Thumb Angle Out, Middle Up' (0x13a): MPJPE=31.43
- 01-01-009-01 'Index Bent on Fist, Thumb Under' (0x108): MPJPE=32.35
- 01-05-047-01 'Oval Thumb Forward' (0x17a): MPJPE=32.76
- 01-09-025-01 'Index Thumb Forward, Index Bent' (0x1e5): MPJPE=32.93
- 01-02-010-01 'Index Middle Unit, Middle Bent' (0x117): MPJPE=32.96
- 01-01-014-01 'Index Hinge on Circle' (0x10d): MPJPE=33.10
- 01-08-015-01 'Middle Raised Knuckle' (0x1c8): MPJPE=33.17
- 01-02-007-01 'Index Hinge, Middle Up' (0x114): MPJPE=33.35
- 01-07-022-01 'Ring Thumb Hook' (0x1b9): MPJPE=33.39
- 01-05-042-01 'Curlicue' (0x175): MPJPE=33.58
- 01-02-002-01 'Index Middle on Circle' (0x10f): MPJPE=33.67
- 01-09-035-01 'Index Thumb Hinge Large' (0x1ef): MPJPE=33.88
- 01-01-012-01 'Index Hinge' (0x10b): MPJPE=33.99
