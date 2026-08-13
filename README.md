# fsw-r

Framework chuyển **SignWriting/ISWA (FSW notation)** thành pose 3D và video
render được — input là chuỗi FSW thật (vd
`"M508x515S10000493x485S22a04500x500"`), không phải SWML hay mô tả tay thủ
công. Xem `ROADMAP.md` (lộ trình theo từng pha, việc còn lại) và
`PROGRESS.md` (nhật ký đầy đủ mọi quyết định/kỹ thuật đã áp dụng, kể cả
những lần phát hiện và sửa sai) để biết bối cảnh chi tiết — README này chỉ
là bản đồ tổng quan.

## Pipeline

```
FSW string ──▶ AST ──▶ FSWR symbols ──▶ SignTimeline (MVP-1) ──▶ sampled PoseFrames
                                              │
                                              ▼
                                   export/ (forward kinematics,
                                   two-bone arm IK, static torso/head)
                                              │
                                              ▼
                                    .pose file (pose-format)
                                              │
                              ┌───────────────┼────────────────┐
                              ▼               ▼                ▼
                      video toàn thân   video cận cảnh    validation/
                      (PoseVisualizer)   bàn tay (zoom +   (MPJPE, giới hạn
                                          góc nhìn 3/4)     giải phẫu)
```

## Trạng thái hiện tại

**Tầng ký hiệu (ISWA symbol → pose/quaternion/trajectory), theo category:**

| Category | Base symbol | Trạng thái |
|---|---|---|
| 1. Hands | 261 | **Xong 100%** — data-driven qua `HandSymbol`, góc khớp từ dữ liệu thật (MediaPipe trên `3d-hands-benchmark`, không phải đoán) |
| 2. Movement | 242 | **Xong 100%** — quỹ đạo sinh bằng công thức `(path_type × plane)`, không đo |
| 3. Dynamics | 8 | **Xong 100%** (tầng ký hiệu) — AUTHORED từ tên thật signbank.org, chưa nối vào `SignTimeline` |
| 4. Head & Face | ~110 | **Xong** (nhóm khác trong dự án phụ trách) — blend-shape ARKit-52 |
| 5. Trunk & Limb | 18 | **Xong 100%** (tầng ký hiệu) — AUTHORED, chưa nối vào `SignTimeline` |
| 6. Location | 8 | Chưa làm |
| 7. Punctuation | 5 | Chưa làm |

**`SignTimeline` (MVP-1):** FSW sign → timeline có trục thời gian thật, phạm
vi cố ý giới hạn — đúng 1 symbol tay (Category 1) + tối đa 1 symbol chuyển
động (Category 2), phủ **6,2% sign thật** (đo trên SignBank+, 257.800 sign).
Group 12 (Finger Movement, 20/242 base symbol Category 2, phủ thêm **16,8%
sign thật**) sinh chuyển động khớp ngón tay thật (dao động biên độ tới 56,6°
ở MCP), không chỉ tịnh tiến cổ tay.

**Tầng export + video:** `.pose` xuất đủ 3 chiều không gian (forward
kinematics bàn tay + two-bone IK cánh tay + thân/đầu tĩnh), qua
`PoseVisualizer` (thư viện `pose-format` chuẩn cộng đồng) ra video/GIF. Có
**2 video mỗi sign**: toàn thân (tư thế/quỹ đạo) và cận cảnh bàn tay (phóng
to + neo cổ tay + xoay góc 3/4, để đọc được handshape/khớp ngón mà video
toàn thân không đủ độ phân giải để thấy).

**Tầng đánh giá:** MPJPE = **48,72** (thang chuẩn hoá 150, thắng cả 2
baseline), đo trên `sign-language-processing/3d-hands-benchmark`. Vi phạm
giới hạn giải phẫu: 224/261 symbol Category 1 (đa số do CMC ngón cái, nghi
lệch định nghĩa — chưa xác minh, xem `PROGRESS.md`).

**11 GIF demo** (`fsw-r-viz/demo/mvp1_sign_*.gif`) ghi lại toàn bộ tiến
trình cải thiện chất lượng hình ảnh, từ hand-only đến full-signer đến
cận-cảnh-góc-3/4 — xem mục "Chạy thử" bên dưới để tự render lại.

## Cấu trúc 2 package

```
Code/
  fsw-r/       core + timeline + export + validation: KHÔNG phụ thuộc
               matplotlib hay bất kỳ thư viện 3D/hiển thị nào
  fsw-r-viz/   visualization: matplotlib (sanity-check tĩnh) +
               pose-format/PoseVisualizer (video thật), phụ thuộc fsw-r
```

Hai package tách biệt hoàn toàn, phụ thuộc một chiều (`fsw-r-viz` →
`fsw-r`). `fsw-r`'s `core/` không có chỗ nào biết cụ thể về category/group
nào (renderer, registry, parser đều category-agnostic) — xem
`fsw-r/README.md` để biết kiến trúc chi tiết từng tầng
(`core/`/`timeline/`/`export/`/`validation/`), và `fsw-r-viz/README.md` cho
các renderer/video.

## Chạy thử

```bash
cd fsw-r && pip install -e ".[dev]"
python -m fsw_r.demo        # parse FSW thật -> object FSWR, in ra pose/quaternion
pytest                       # 1.475 test
mypy --strict                 # strict type-check, sạch toàn bộ (91 file: src/+tests/+scripts/ đã bật)

cd ../fsw-r-viz && pip install -e ".[dev]"
python -m fsw_r_viz.demo    # render toàn bộ ảnh/GIF demo vào output/ và demo/
pytest                       # 42 test
mypy --strict                 # 4 lỗi cũ không liên quan (FuncAnimation stub, 1 ndarray generic)
```

`python -m fsw_r_viz.demo` ghi cả video toàn thân (`demo/mvp1_sign.gif`,
tên chính tắc "mới nhất") lẫn video cận cảnh bàn tay 2 góc nhìn
(`demo/mvp1_sign_hand_closeup.gif` 0°, và ví dụ với 1 sign có chuyển động
khớp ngón — xem `demo/mvp1_sign_10_closeup_front.gif` /
`_3q.gif`) — môi trường phát triển hiện tại không có `vidgear`/ffmpeg thật
nên tự động fallback từ `.mp4` sang `.gif` (Pillow), có in cảnh báo rõ ràng
khi fallback, không âm thầm.

## 3 giới hạn đã biết (quan trọng khi trích dẫn/dùng số liệu)

1. **Góc khớp ngón tay (Category 1) là ước lượng MediaPipe trên ảnh thật,
   KHÔNG phải motion-capture đã xác thực.** Nguồn:
   `sign-language-processing/3d-hands-benchmark` — 1 người thật làm mẫu cả
   261 handshape × 6 góc chụp, pose 3D suy ra bằng MediaPipe v0.10.3 (median
   qua 48 lần chụp/symbol). MPJPE=48,72 đo trên chính nguồn này (không phải
   ground truth độc lập).
2. **Toàn bộ dữ liệu Category 2 (quỹ đạo), 3 (dynamics), 5 (thân người), và
   `FingerArticulation` (Group 12) là AUTHORED** — người soạn đọc tên ISWA
   thật trên signbank.org rồi tự gán số, không có dataset nào ánh xạ tên ISWA
   sang toạ độ/góc số. Luôn ghi rõ trong `_meta` của từng file JSON trong
   `fsw-r/src/fsw_r/data/`.
3. **`PoseVisualizer` (renderer chuẩn cộng đồng `pose-format`) chỉ chiếu 2
   chiều (XY) lên video** — Z chỉ dùng để quyết định thứ tự vẽ. Dữ liệu
   `.pose` xuất ra giàu hơn thứ renderer chuẩn khai thác được; video cận
   cảnh bàn tay bù lại bằng cách xoay góc 3/4 trước khi chiếu (xem
   `fsw-r-viz/README.md`), nhưng bản thân renderer vẫn không đổi.

Cả 3 điểm này (và nhiều giả định nhỏ hơn khác) được ghi lại đầy đủ trong
`PROGRESS.md`'s mục "giả định chưa kiểm chứng" ở mỗi pha, và trong `_meta`
của từng file dữ liệu — không bị mất qua các lần refactor.
