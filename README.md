# fsw-r

Framework chuyển **SignWriting/ISWA (FSW notation)** thành pose 3D render
được — input là chuỗi FSW thật (vd `"S10010480x480"`), không phải SWML hay
mô tả tay thủ công. Xem `ROADMAP.md` (lộ trình cover toàn bộ ISWA theo
từng pha) và `PROGRESS.md` (nhật ký các quyết định/kỹ thuật đã áp dụng, kể
cả những lần sửa sai) để biết bối cảnh đầy đủ.

**Trạng thái hiện tại:** Category 1 (Hands) xong 100% — cả 261/261 base
symbol của 10 group ASL-counting (Index, Index & Middle, ..., Thumb), mỗi
symbol nhận đủ `fill`/`rotation` hợp lệ theo đúng bảng ISWA thật (không còn
validate theo range chung chung). 7 category còn lại của ISWA (Movement,
Dynamics, Head & Face, Trunk, Limb, Location, Punctuation) chưa bắt đầu.

## Cấu trúc 2 package

```
Code/
  fsw-r/       core: FSW parsing + joint-pose/wrist-orientation logic,
               KHÔNG phụ thuộc matplotlib hay bất kỳ thư viện 3D nào
  fsw-r-viz/   visualization: stick-figure 3D bằng matplotlib, phụ thuộc fsw-r
```

Hai package tách biệt hoàn toàn, phụ thuộc một chiều (`fsw-r-viz` →
`fsw-r`). `fsw-r` không có bất kỳ chỗ nào biết cụ thể về group/base symbol
nào (renderer, registry, parser đều category/group-agnostic) — xem
`fsw-r/README.md` để biết kiến trúc chi tiết (4 tầng ban đầu → data-driven
sau refactor, xem `PROGRESS.md`).

## Chạy thử

```bash
cd fsw-r && pip install -e ".[dev]"
python -m fsw_r.demo      # parse FSW thật -> object FSWR, in ra pose/quaternion
pytest                     # 596 test
mypy --strict               # strict type-check

cd ../fsw-r-viz && pip install -e ".[dev]"
python -m fsw_r_viz.demo   # render 2 ảnh PNG stick-figure vào fsw-r-viz/output/
pytest                      # 4 test
mypy --strict
```

## 2 giới hạn đã biết (quan trọng khi trích dẫn/dùng số liệu)

1. **Góc khớp (joint angle) là ước lượng MediaPipe trên ảnh thật, KHÔNG
   phải motion-capture đã xác thực.** Nguồn:
   `sign-language-processing/3d-hands-benchmark` — 1 người thật làm mẫu cả
   261 handshape × 6 góc chụp, pose 3D suy ra bằng MediaPipe v0.10.3 (median
   qua 48 lần chụp/symbol). Bản thân benchmark cũng không claim đây là
   ground truth mocap. Đáng tin hơn nhiều so với số tự đoán (baseline cũ
   trước khi tích hợp dataset), nhưng vẫn là ước lượng, không phải đo đạc
   trực tiếp.
2. **`abduction` (độ xoè ngón, khác `flexion` là góc gập) chưa đo được từ
   dataset trên** — vẫn là số ước lượng thủ công, không phải dữ liệu thật.
   Muốn đo cần thêm bước định nghĩa mặt phẳng tham chiếu (lòng bàn tay) và
   tính góc chiếu ngang, phức tạp hơn flexion.

Cả 2 điểm này được ghi lại trong `_meta` của
`fsw-r/src/fsw_r/data/hand_joint_poses.json` và trong docstring liên quan —
không bị mất qua các lần refactor.
