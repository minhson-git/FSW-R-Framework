# FK Accuracy Evaluation

## Overall MPJPE (normalized, size=150)
mean=48.72 median=46.49 p75=50.99 p95=66.19 max=193.37

## Baselines
- **fsw_r_261_poses**: mean=48.72 median=46.49 p75=50.99 p95=66.19 max=193.37
- **average_pose_baseline**: mean=64.84 median=64.03 p75=72.25 p95=83.31 max=181.79
- **one_pose_per_group_baseline**: mean=60.44 median=59.87 p75=68.10 p95=81.15 max=197.18

## MPJPE by finger
- **thumb**: mean=80.29 median=71.33 p75=105.95 p95=150.20 max=244.37
- **index**: mean=43.21 median=36.82 p75=51.80 p95=84.48 max=250.02
- **middle**: mean=38.92 median=35.05 p75=51.52 p95=91.84 max=288.91
- **ring**: mean=45.58 median=39.99 p75=56.83 p95=96.47 max=281.15
- **pinky**: mean=47.76 median=41.62 p75=58.20 p95=91.03 max=230.39

## MPJPE by joint type
- **CMC**: mean=54.13 median=52.42 p75=64.65 p95=84.66 max=124.93
- **MCP**: mean=30.49 median=28.54 p75=38.37 p95=63.21 max=158.04
- **PIP**: mean=44.09 median=41.50 p75=51.87 p95=67.60 max=229.05
- **DIP**: mean=49.69 median=44.87 p75=60.56 p95=95.48 max=267.94
- **IP**: mean=90.63 median=89.66 p75=106.04 p95=128.43 max=209.19
- **TIP**: mean=70.16 median=60.16 p75=94.19 p95=150.59 max=288.91

## Occlusion hypothesis (C4)
- Expected order (worst->best): ['ring', 'pinky', 'middle', 'index']
- Observed order (worst->best): ['pinky', 'ring', 'index', 'middle']
- Matches: False

## Index -> base_hex verification (A3)
- Checked 783 (base, fill) pairs
- Invalid pairs found: 14
  - base 0x14d (01-05-002): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x14d (01-05-002): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x14f (01-05-004): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x14f (01-05-004): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x151 (01-05-006): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x151 (01-05-006): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15c (01-05-017): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15c (01-05-017): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15e (01-05-019): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x15e (01-05-019): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x1f6 (01-10-002): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x1f6 (01-10-002): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x204 (01-10-016): fill=0 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]
  - base 0x204 (01-10-016): fill=2 used by hands.py's ground truth is NOT in ISWA's valid_fills=[1]

## Worst 20 symbols
- 01-05-014 'Five Fingers Spread Hinge, No Thumb' (0x159): MPJPE=193.37
- 01-05-033 'Open Cup' (0x16c): MPJPE=116.20
- 01-05-053 'Hinge Thumb Side' (0x180): MPJPE=113.11
- 01-04-008 'Four Fingers Unit Hinge' (0x14b): MPJPE=78.06
- 01-06-030 'Baby Index On Angle' (0x1a3): MPJPE=76.42
- 01-06-029 'Baby Index On Hinge' (0x1a2): MPJPE=74.66
- 01-10-002 'Thumb Heel' (0x1f6): MPJPE=73.08
- 01-05-013 'Five Fingers Spread Hinge, Thumb Side' (0x158): MPJPE=71.24
- 01-06-022 'Baby Thumb on Hinge' (0x19b): MPJPE=68.61
- 01-05-051 'Small Hinge' (0x17e): MPJPE=68.25
- 01-01-003 'Index on Cup' (0x102): MPJPE=67.68
- 01-06-010 'Baby Down, Ripple Straight' (0x18f): MPJPE=67.01
- 01-09-032 'Index Thumb Cup' (0x1ec): MPJPE=66.39
- 01-05-004 'Five Fingers Spread Four Bent Heel' (0x14f): MPJPE=66.19
- 01-04-003 'Four Fingers Hinge' (0x146): MPJPE=65.90
- 01-08-003 'Index Ring Baby on Curlicue' (0x1bc): MPJPE=65.77
- 01-03-036 'Middle Thumb Angle Out, Index Crossed' (0x141): MPJPE=65.21
- 01-05-017 'Flat Hand, Heel' (0x15c): MPJPE=64.54
- 01-05-055 'Hinge No Thumb' (0x182): MPJPE=64.29
- 01-06-003 'Index Middle Ring on Hinge' (0x188): MPJPE=63.81

## Best 20 symbols
- 01-05-027 'Claw' (0x166): MPJPE=32.05
- 01-05-043 'Circle' (0x176): MPJPE=32.78
- 01-03-001 'Index Middle Thumb' (0x11e): MPJPE=34.30
- 01-09-035 'Index Thumb Hinge Large' (0x1ef): MPJPE=34.39
- 01-09-033 'Index Thumb Cup Open' (0x1ed): MPJPE=34.56
- 01-09-027 'Index Thumb Curlicue' (0x1e7): MPJPE=34.64
- 01-04-007 'Four Fingers Unit Bent' (0x14a): MPJPE=34.65
- 01-05-047 'Oval Thumb Forward' (0x17a): MPJPE=34.69
- 01-02-011 'Index Middle Unit Cup' (0x118): MPJPE=34.76
- 01-05-048 'Open Hinge' (0x17b): MPJPE=35.27
- 01-05-034 'Cup' (0x16d): MPJPE=35.29
- 01-03-004 'Index Middle Bent, Thumb Straight' (0x121): MPJPE=35.41
- 01-01-014 'Index Hinge on Circle' (0x10d): MPJPE=35.81
- 01-09-025 'Index Thumb Forward, Index Bent' (0x1e5): MPJPE=36.31
- 01-03-021 'Index Middle Unit Hinge, Thumb Side' (0x132): MPJPE=36.39
- 01-05-040 'Cup Thumb Forward' (0x173): MPJPE=36.52
- 01-06-012 'Baby Down, Others Circle' (0x191): MPJPE=36.61
- 01-02-010 'Index Middle Unit, Middle Bent' (0x117): MPJPE=36.90
- 01-08-015 'Middle Raised Knuckle' (0x1c8): MPJPE=37.19
- 01-03-029 'Index Thumb Angle Out, Middle Up' (0x13a): MPJPE=37.25
