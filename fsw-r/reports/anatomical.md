# Anatomical Limit Evaluation

## Flexion violations
- Symbols with >=1 violation: 224/261 (85.8%)
- Angle checks with violation: 400/3915

### By finger
- thumb: 202
- pinky: 73
- ring: 63
- middle: 42
- index: 18

### By joint
- cmc: 201
- pip: 187
- dip: 11
- mcp: 1

### Worst overshoot (top 20)
- 01-03-013 'Index Middle Thumb Hook' (0x12a): overshoot=60.0 deg
- 01-05-033 'Open Cup' (0x16c): overshoot=60.0 deg
- 01-05-053 'Hinge Thumb Side' (0x180): overshoot=60.0 deg
- 01-03-011 'Index Middle Thumb Cup' (0x128): overshoot=58.0 deg
- 01-06-020 'Baby Touches Thumb' (0x199): overshoot=47.0 deg
- 01-10-001 'Thumb' (0x1f5): overshoot=47.0 deg
- 01-10-014 'Thumb Over Four Raised Knuckles' (0x202): overshoot=47.0 deg
- 01-06-018 'Baby Raised Knuckle' (0x197): overshoot=46.0 deg
- 01-07-011 'Ring Up' (0x1ae): overshoot=46.0 deg
- 01-08-016 'Middle Up, Thumb Side' (0x1c9): overshoot=44.0 deg
- 01-10-015 'Fist' (0x203): overshoot=44.0 deg
- 01-04-007 'Four Fingers Unit Bent' (0x14a): overshoot=43.0 deg
- 01-10-005 'Thumb Side Bent' (0x1f9): overshoot=42.0 deg
- 01-08-019 'Middle Baby' (0x1cc): overshoot=40.0 deg
- 01-07-018 'Ring Middle Unit' (0x1b5): overshoot=39.0 deg
- 01-07-019 'Ring Middle Raised Knuckles' (0x1b6): overshoot=39.0 deg
- 01-07-020 'Ring Index' (0x1b7): overshoot=39.0 deg
- 01-08-017 'Middle Thumb Hook' (0x1ca): overshoot=39.0 deg
- 01-10-003 'Thumb Side Diagonal' (0x1f7): overshoot=38.0 deg
- 01-08-005 'Index Ring Baby on Hook In' (0x1be): overshoot=36.0 deg

## Abduction violations
- Symbols with >=1 violation: 0/261
- Note: hand_joint_poses.json's own abduction values are already documented as un-measured estimates (see PROGRESS.md) -- these violation counts are a weaker signal than the flexion ones above, reported separately rather than merged into one number.

## Correlation with FK reconstruction error (C3)
- Pearson r = 0.014 (n=261)
- positive r: symbols with worse anatomical violations tend to also have worse FK reconstruction error (consistent with a shared root cause); near-zero or negative r: the two are not obviously related
