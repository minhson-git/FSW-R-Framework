# fsw-r — Tiến độ dự án

Tóm tắt những gì đã làm trong quá trình xây dựng prototype **fsw-r** (fsw-renderable):
framework OOP render các symbol tay ISWA/SignWriting sang 3D, phạm vi hiện tại là
**Symbol Group 1 (Index Finger) / Base Symbol 1 ("Index", 01-01-001)**.

## Cấu trúc 2 package

```
Code/
  fsw-r/       core: symbol/pose logic, KHÔNG phụ thuộc matplotlib
  fsw-r-viz/   visualization: stick-figure 3D bằng matplotlib, phụ thuộc fsw-r
```

Hai package tách biệt hoàn toàn, phụ thuộc một chiều (`fsw-r-viz` → `fsw-r`).
`fsw-r` có `py.typed` marker để `fsw-r-viz` chạy `mypy --strict` xuyên qua type
của `fsw-r` thay vì phải ignore.

## Parse FSW thật (FSW → AST → FSWR), không còn tự chế regex mô phỏng

**Lần sửa đầu** (trong `core/fsw_symbol_key.py`) mới chỉ tự viết regex riêng
mô phỏng đúng format — có cài `signwriting` làm dependency nhưng **chưa hề
`import`/gọi hàm thật nào của nó**, và chỉ parse được 1 symbol key trần (6
ký tự), không parse được FSW sign string đầy đủ (có box marker + nhiều
symbol + vị trí). Đây là gap người dùng phát hiện và yêu cầu sửa lại đúng.

**Đã sửa thành pipeline 3 tầng, mỗi tầng 1 module:**

```
FSW sign string --[fsw_ast.py, GỌI THẬT signwriting.formats.fsw_to_sign()]--> AST (FSWSignAST)
AST             --[fswr_converter.py + registry.py]-------------------------> FSWR (PositionedSymbol)
```

1. `core/fsw_ast.py` — `parse_fsw_to_ast()` gọi **thật** hàm
   `signwriting.formats.fsw_to_sign.fsw_to_sign()` (import thật, verify đã
   chạy được), parse được cả sign string đầy đủ nhiều symbol (vd
   `"M500x500S10010480x480S1061a520x520"` — sign 2 tay).
2. `core/fsw_symbol_key.py` — decode 1 symbol key đã tách ra (vd `"S10010"`)
   thành category/group/base_symbol_number/fill/rotation. Kỹ thuật cắt
   chuỗi giống đúng cách `signwriting.utils.mirror.mirror_symbol` làm nội
   bộ (không có hàm public riêng cho việc này trong thư viện thật). Range
   group (10 group ASL) vẫn lấy từ `fsw-structure.js` như trước — đây là
   phần domain knowledge có thật, đã verify, chỉ là bản thân thư viện JS
   không expose nó ở dạng "group số 1-10" trực tiếp.
3. `core/registry.py` (`build_symbol()`, `symbol_from_fsw()`) +
   `core/fswr_converter.py` (`ast_to_fswr()`, `fsw_to_fswr()`) — converter
   AST → FSWR thật: chạy qua từng node trong AST, tra registry, dựng đúng
   object `FSWRenderableSymbol`, giữ nguyên toạ độ trang (x, y) — xử lý
   được sign nhiều symbol (2 tay), không chỉ 1 symbol đơn lẻ như trước.

Demo (`python -m fsw_r.demo`) giờ có thêm Part 2: parse 1 FSW sign string
thật có 2 symbol → ra đúng 2 object FSWR, đúng vị trí, đúng hand_side.

**Vẫn còn là model tự thiết kế (không có spec thật để tra):** ISWA/FSW là
notation 2D, không có nguồn "thật" nào cho quaternion cổ tay 3D hay góc gập
khớp — `get_wrist_orientation()` và `_default_joint_pose()` vẫn là diễn giải
riêng của project (ghi chú rõ trong code), không phải chỗ "mock chờ thay
bằng bản thật" vì không tồn tại bản thật nào khác cho phần này.

## Kiến trúc `fsw-r` (4 tầng)

```
FSWBaseSymbol                category/group/base/fill/rotation
                              + hand_side (concrete, suy ra từ rotation)
                              + get_wrist_orientation() (abstract)
    |
FSWRenderableSymbol           + get_joint_pose() -> HandJointPose
    |
SymbolGroupN (per group)      default joint-angle template cho cả group
    |
BaseSymbolX                   dùng nguyên template, hoặc override get_joint_pose()
```

`HandMeshRenderer3D` chỉ phụ thuộc `FSWRenderableSymbol` + `HandRigProvider`
(đều abstract) — không biết cụ thể group/base symbol nào.

### Quy tắc `hand_side` (ISWA)

`rotation` là 1 hex digit (0-15), chia làm 2 nửa 8 giá trị:

| rotation | hướng | góc | hand_side |
|---|---|---|---|
| 0-7 | counter-clockwise | `(rotation % 8) * 45°` | RIGHT |
| 8-15 | clockwise (ảnh gương nửa trên) | `(rotation % 8) * 45°` | LEFT |

`hand_side` là property **concrete** đặt 1 lần duy nhất ở `FSWBaseSymbol`
(không lặp lại ở group/base symbol nào), vì đây là quy tắc chung cho mọi symbol.

**Renderer không mirror bằng phép xoay** — tay trái là ảnh gương (chirality
khác), không phải tay phải xoay đi 1 góc. `HandRigProvider.get_rig(hand_side)`
chọn đúng rig (2 rig thực sự khác nhau) trước, rồi mới áp
`get_wrist_orientation()` + `get_joint_pose()` lên rig đó.

## Các lỗi đã phát hiện và sửa trong quá trình đối chứng

1. **Trục xoay sai (y → z).** `rotation` của ISWA là góc xoay **trong mặt
   phẳng trang giấy** (như kim đồng hồ: 0°, 45°, ... 315°), tức xoay quanh
   trục vuông góc với trang (trục nhìn của người xem = trục z trong hệ quy
   chiếu đang dùng: x = ngang qua khớp đốt, y = cổ tay→đầu ngón, z = pháp
   tuyến lòng bàn tay hướng ra người xem). Ban đầu code xoay quanh trục y
   (nghiêng bàn tay vào chiều sâu) — sai, khiến hình render biến dạng kỳ lạ.
   Đã sửa `Rotation.from_euler("y", ...)` → `("z", ...)` trong
   `group_01_index_finger.py`.

2. **rotation không chỉ là góc — còn encode hand_side.** Ban đầu mock chỉ có
   `rotation * 60` không giới hạn phạm vi, không phân biệt trái/phải. Đã bổ
   sung `HandSide` enum, validate `fill` (0-5) / `rotation` (0-15) ở
   constructor (raise `ValueError` nếu sai phạm vi), và `_rotation_angle_degrees()`
   dùng chung công thức `(rotation % 8) * 45°` cho cả 2 nửa.

3. **Camera demo (fsw-r-viz) làm hình trông sai dù logic đã đúng.** Sau khi
   sửa trục xoay, góc camera xiên ban đầu (elev=15) đôi lúc nhìn bàn tay
   "dí cạnh" (edge-on) do bàn tay giờ xoay phẳng trong mặt x-y. Thử camera
   nhìn thẳng trục z (elev=90) thì đúng về góc nhưng lại phẳng như 2D, mất
   cảm giác 3D. Chốt lại: camera xiên vừa phải (`elev=20, azim=-60`) — vẫn
   là góc nhìn 3D thật, đồng thời vẫn thấy rõ cổ tay xoay như kim đồng hồ mà
   góc gập từng khớp ngón không đổi.

## `fsw-r-viz`: visualization

- `hand_geometry.py`: forward-kinematics gần đúng (độ dài xương, vị trí gốc
  từng ngón) để dựng stick-figure từ `HandJointPose`, cộng
  `mirror_for_left_hand()` — lật trục x (không xoay) để mô phỏng việc chọn
  rig LEFT riêng biệt, vì package này không có rig/mesh thật.
- `plot_hand.py`: vẽ matplotlib 3D (`render_symbol_to_file`,
  `render_symbols_grid`), lưu PNG (headless, backend Agg).
- `demo.py`: render Base Symbol 1 ở 4 rotation (3 RIGHT: 0, 2, 6 + 1 LEFT: 10)
  thành 1 ảnh lưới, xác nhận trực quan joint pose giữ nguyên còn wrist
  orientation + chirality thay đổi.

## Trạng thái hiện tại

- `fsw-r`: `mypy --strict` sạch (19 file), `pytest` 49/49 pass
  (`test_group_01.py`, `test_hand_side.py`, `test_fsw_symbol_key.py`,
  `test_fsw_ast.py`, `test_registry.py`, `test_fswr_converter.py`).
- `fsw-r-viz`: `mypy --strict` sạch (6 file), `pytest` 4/4 pass
  (`test_hand_geometry.py`, `test_plot_hand.py`).
- Demo trực quan (`python -m fsw_r_viz.demo`) render đúng: joint pose giống
  hệt nhau ở mọi rotation/hand_side, chỉ hướng cổ tay + chirality khác.
- `demo.py` của `fsw-r` giờ dựng instance qua `symbol_from_fsw("S10010")` —
  key FSW thật — thay vì gọi thẳng constructor với int tự đặt.

## Việc còn để ngỏ / chưa làm

- Chỉ mới đăng ký 2/652 base symbol Category 1 ("Index", "Index Bent") vào
  registry — `symbol_from_fsw()` sẽ raise `ValueError` rõ ràng cho mọi key
  khác cho đến khi mở rộng thêm group.
- Góc khớp trong `group_01_index_finger.py` là baseline áng chừng, chưa tinh
  chỉnh theo rig/mesh 3D thật.
- Dấu của `abduction` có thể cần đảo chiều cho tay trái tuỳ convention rig —
  chưa xử lý (ghi chú trong code, chưa có rig thật để kiểm chứng).
- Chưa có export JSON cho `HandJointPose`/wrist quaternion (cần nếu render
  cuối cùng là web three.js thay vì Blender/Open3D).
- Mới có Group 1 / 2 base symbol (`Index`, `Index Bent`) — còn ~9 group và
  ~650 base symbol khác của ISWA Category 1 cần mở rộng theo đúng pattern đã
  thiết lập (xem README của `fsw-r` mục "Adding a new group").
- Môi trường dùng Python 3.10 (máy hiện có) thay vì 3.11+ như brief ban đầu
  yêu cầu — không ảnh hưởng vì không dùng feature riêng của 3.11.
