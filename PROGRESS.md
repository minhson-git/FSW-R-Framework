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

## Giải thích chi tiết: luồng xử lý FSW → FSW-R (từng bước)

### Vì sao cần pipeline này

FSW (Formal SignWriting) là một **chuỗi ký tự ASCII** (vd
`"M500x500S10010480x480S1061a520x520"`), không phải object lập trình được.
Để render 3D, cần biến chuỗi đó thành **object Python thật** — có method
`get_joint_pose()` (góc gập khớp ngón) và `get_wrist_orientation()`
(hướng xoay cổ tay dạng quaternion). Việc này được chia làm **4 bước**, mỗi
bước 1 file riêng, để mỗi phần chỉ làm đúng 1 việc và dễ thay/mở rộng sau
này (thêm group mới không phải sửa lại các bước còn lại).

```
FSW string (text)
    │
    │  BƯỚC 1 — fsw_ast.py
    ▼
AST (FSWSignAST)              — cấu trúc: box + danh sách symbol (key thô + toạ độ x,y)
    │
    │  BƯỚC 2 — fsw_symbol_key.py
    ▼
ParsedFSWSymbol                — số nguyên: category, group, base_symbol_number, fill, rotation
    │
    │  BƯỚC 3 — registry.py
    ▼
FSWRenderableSymbol             — object Python THẬT, đúng class (vd BaseSymbol01_01_001_Index)
    │
    │  BƯỚC 4 — fswr_converter.py (gộp lại + giữ toạ độ trang)
    ▼
PositionedSymbol                — object FSWR + vị trí (x, y) trên trang
```

### Ví dụ xuyên suốt

Dùng chuỗi FSW thật của 1 "sign" 2 tay:
`"M500x500S10010480x480S1061a520x520"`

---

**BƯỚC 1 — FSW string → AST**

- **Input:** chuỗi FSW thô ở trên.
- **Xử lý:** gọi hàm `signwriting.formats.fsw_to_sign.fsw_to_sign()`
  (thư viện `signwriting` trên PyPI — bản Python của
  `sutton-signwriting/core`). Hàm này tách
  chuỗi thành: 1 "box" (khung/vị trí tổng) + danh sách các "symbol" (mỗi
  symbol là 1 key 6 ký tự + toạ độ x,y).
- **Output:**
  ```python
  FSWSignAST(
      box_symbol="M", box_x=500, box_y=500,
      symbols=(
          FSWSymbolNode(key="S10010", x=480, y=480),
          FSWSymbolNode(key="S1061a", x=520, y=520),
      ),
  )
  ```
- **Lưu ý:** `key` ở bước này vẫn là **string thô, chưa giải mã** — mới chỉ
  tách được "đây là 1 symbol, ở vị trí này", chưa biết nó là symbol gì.

---

**BƯỚC 2 — Giải mã 1 symbol key → số nguyên**

- **Input:** 1 key 6 ký tự, vd `"S10010"`.
- **Xử lý:** bóc tách theo đúng cấu trúc key thật của ISWA:
  `S` + 3 ký tự hex (base code) + 1 ký tự hex (fill, 0-5) + 1 ký tự hex
  (rotation, 0-f). Sau đó tra `base code` vào bảng ranh giới 10 group (số
  lấy thật từ source code `sutton-signwriting/core`, file
  `fsw-structure.js`) để suy ra `group` và `base_symbol_number`.
- **Output cho từng symbol:**

  | key | base (hex) | fill | rotation | → group / base_symbol_number | tên |
  |---|---|---|---|---|---|
  | `"S10010"` | `0x100` | 1 | 0 | group 1 / số 1 | **"Index"** |
  | `"S1061a"` | `0x106` | 1 | 10 (`a`) | group 1 / số 7 | **"Index Bent"** |

  Cách tính `base_symbol_number`: `base_symbol_number = base_hex - group_start_hex + 1`.
  Group 1 bắt đầu ở `0x100` → `0x106 - 0x100 + 1 = 7`.
  Riêng `rotation=10 ≥ 8` → symbol này là tay **LEFT** (quy tắc `hand_side`).

---

**BƯỚC 3 — Số nguyên đã giải mã → object Python thật**

- **Input:** `ParsedFSWSymbol` từ bước 2 (vd group=1, base_symbol_number=1, fill=1, rotation=0).
- **Xử lý:** tra bảng `_REGISTRY[(group, base_symbol_number)]`. Bảng này
  được điền **tự động lúc import module group** — mỗi class base symbol
  (vd `BaseSymbol01_01_001_Index` trong `groups/group_01_index_finger.py`)
  có decorator `@register_symbol(group=1, base_symbol_number=1)` phía
  trên, chạy 1 lần khi Python import file đó. Tìm được class → gọi
  `cls(fill=1, rotation=0)`.
- **Output:** 1 instance thật, vd `BaseSymbol01_01_001_Index(fill=1, rotation=0)` —
  từ đây gọi được `symbol.get_joint_pose()`, `symbol.get_wrist_orientation()`,
  `symbol.hand_side`, `symbol.symbol_id` (`"01-01-001"`) như object bình
  thường.
- **Nếu không tìm thấy class** (group/base_symbol_number chưa đăng ký) →
  raise `ValueError` rõ ràng, không âm thầm trả về sai.

---

**BƯỚC 4 — Gộp lại cho cả 1 "sign" (giữ vị trí trang)**

- **Input:** toàn bộ `FSWSignAST` từ bước 1.
- **Xử lý:** lặp qua từng `FSWSymbolNode`, chạy bước 2 + bước 3 cho từng
  cái, rồi bọc thêm toạ độ `(x, y)` gốc (vì 1 "sign" có thể có nhiều tay,
  mỗi tay 1 vị trí khác nhau trên trang — vd tay phải bên trái, tay trái
  bên phải).
- **Output:**
  ```python
  (
      PositionedSymbol(symbol=BaseSymbol01_01_001_Index(fill=1, rotation=0), x=480, y=480),
      PositionedSymbol(symbol=BaseSymbol01_01_007_IndexBent(fill=1, rotation=10), x=520, y=520),
  )
  ```
- Hàm `fsw_to_fswr(fsw: str)` = gộp cả 4 bước làm 1, dùng khi chỉ có chuỗi
  FSW thô trong tay: `fsw_to_fswr("M500x500S10010480x480S1061a520x520")`
  ra thẳng kết quả trên.

### Tự kiểm chứng

Chạy `python -m fsw_r.demo` (Part 2 trong file demo) sẽ in ra đúng quá
trình trên với ví dụ 2 tay này — có thể copy log đó vào báo cáo làm bằng
chứng chạy được thật, không phải mô tả suông.

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

4. **Bị đổi qua đổi lại trục xoay (y↔z) 2 lần** trước khi chốt đúng. Người
   dùng mô tả "xoay cổ tay" — hiểu nhầm thành động tác vặn cổ tay
   (pronation/supination, giữ hướng ngón cố định, trục y) nên đổi lại từ z
   về y. Sau đó người dùng mô tả cụ thể hơn: "xoay 180° thì ngón trỏ chỉ
   xuống" — chỉ khớp với trục **z** (xoay quanh z làm hướng ngón đổi từ lên
   → ngang → xuống). Đã chốt lại z và **khoá bằng test**
   `test_wrist_orientation_points_finger_down_at_180_degrees` để tránh lặp
   lỗi. Bài học: khi mô tả bằng lời mơ hồ (nhiều nghĩa vật lý khớp), nên hỏi
   ví dụ số cụ thể ("ở góc X thì ngón chỉ hướng nào") thay vì đoán, và khoá
   lại bằng test ngay khi có được ví dụ cụ thể.

5. **Phát hiện `fill` cũng ảnh hưởng hướng 3D, không chỉ là "tô màu".** Tải
   trực tiếp ảnh chart thật từ signwriting.org
   (`ISWA2010_Symbol_Charts/01-01-001-ISWA_Chart.jpg`, trang lesson
   `01-01-001-01.html`) và xem bằng mắt — phát hiện tiêu đề trang "Six Palm
   Facings" thực ra mô tả **`fill`** (không phải `rotation` như comment gốc
   ghi nhầm). Chart cho thấy `fill` (0-5) mã hoá 2 thành phần: **Palm/Side/
   Back of Hand** (mặt nào của bàn tay hướng ra người xem — xoay quanh trục
   y, giống đúng phép "vặn cổ tay" tưởng nhầm gán cho `rotation` trước đó,
   hoá ra thuộc về `fill`!) × **Wall/Floor Plane** (cả cánh tay ở mặt phẳng
   đứng hay ngang — xoay quanh trục x). Đã thêm `_fill_facing_degrees()` +
   `_fill_plane_degrees()` + `_default_wrist_orientation()` (kết hợp cả 3:
   rotation + facing + plane) vào `FSWBaseSymbol`, dùng chung cho mọi group.

6. **Bug gimbal-lock: fill=3 và fill=5 (Floor Plane) ra cùng 1 hướng.**
   Người dùng kiểm tra bằng mắt phát hiện fill 0-2 (Wall Plane) đúng, nhưng
   fill 3-5 (Floor Plane) sai hướng: fill=3 (Palm, Floor) phải hướng lòng
   bàn tay lên trên, fill=5 (Back, Floor) phải úp xuống dưới — nhưng code
   cũ cho ra cùng 1 kết quả cho cả 2. Nguyên nhân: công thức cũ áp `plane`
   (xoay quanh x) TRƯỚC `facing` (xoay quanh y) — `plane` xoay vector pháp
   tuyến lòng bàn tay vào đúng trục y, khiến `facing` (cũng xoay quanh y)
   không còn tác dụng phân biệt Palm/Back nữa (giống hiện tượng gimbal
   lock). Đã sửa: (1) đổi thứ tự composition thành `facing` trước rồi mới
   `plane` trong `_default_wrist_orientation()`, (2) đổi dấu
   `_fill_plane_degrees()` thành âm (`-90°` cho Floor) để khớp đúng hướng
   "palm lên trên" theo chart thật. Khoá lại bằng 3 test mới:
   `test_fill_palm_faces_up_in_floor_plane`,
   `test_fill_back_faces_down_in_floor_plane`,
   `test_fill_side_in_floor_plane_differs_from_palm_and_back`.

## Hoàn thành khung sườn cho cả 10 group Hands (Category 1)

Đã tạo đủ `groups/group_03_*.py` đến `group_10_*.py` (trước đó chỉ có group
1, 2). Mỗi group: xem ảnh GIF thật của symbol trên signwriting.org trước
khi viết `_default_joint_pose()` (không suy đoán từ tên group — group 6-9
có base_symbol_number=1 KHÔNG trùng tên group, vd Group 6 "Baby Finger"
nhưng symbol 1 là "Index Middle Ring", không có ngón út). Mỗi group có 1
base symbol đăng ký (`@register_symbol`) + 1 file test riêng
(`test_group_03.py`..`test_group_10.py`, 4 test/file: joint pose ổn định
qua rotation/hand_side, wrist orientation đổi theo rotation, symbol_id/
hand_side đúng, `symbol_from_fsw()` parse ra đúng class). `demo.py` Part 4
mới: parse base_symbol_number=1 của cả 10 group, xác nhận registry phủ đủ
10/10 group.

Tổng cập nhật sau đó: **261/261 base symbol Category 1 — ĐÃ XONG HẾT** (xem
mục "Làm full toàn bộ 261 base symbol" bên dưới).

**Sửa lỗi ngón cái sau khi người dùng đối chiếu lại:** chỉ Group 3, 5, 10
thật sự có ngón cái xoè ra (`ThumbPose` có `abduction`); 7 group còn lại
(1, 2, 4, 6, 7, 8, 9) ngón cái phải cuộn/gập sát lòng bàn tay, KHÔNG xoè
ra. Baseline ban đầu (`cmc=20, mcp=15, ip=10`) tuy không có abduction nhưng
góc gập vẫn quá nhỏ — dựng hình vẫn cho ra ngón cái vươn dài ra ngoài giống
hệt nhóm có ngón cái xoè, không phân biệt được bằng mắt. Đã tăng góc gập
lên `cmc=70, mcp=80, ip=60` (kiểm tra khoảng cách đầu ngón tới cổ tay giảm
từ 11.5 xuống 3.2 đơn vị trước khi áp dụng) cho cả 7 group đó — giờ nhìn
rõ ràng ngón cái cuộn sát vào, không còn giống nhóm ngón cái xoè.

## Thay toàn bộ góc khớp đoán bằng dữ liệu thật (3d-hands-benchmark)

Người dùng hỏi thẳng "project này có hardcode không" — câu trả lời: kiến
trúc/công thức xoay thì không (generic, dùng chung), nhưng **góc khớp từng
ngón tay thì 100% là tôi tự đoán**, không có nguồn nào xác nhận. Đã tìm
cách khắc phục bằng dataset thật `sign-language-processing/3d-hands-benchmark`:

- Dataset chứa: ảnh thật (1 bàn tay thật, 261 handshape ISWA × 6 góc chụp,
  đặt tên file đúng bằng `symbol_id` của mình vd `01-01-001`) + pose 3D
  ước lượng sẵn bằng MediaPipe (3 version, 48 lần chụp/symbol, dạng mảng
  `(48, 261, 6, 21, 3)`).
- Đọc script gốc sinh ra mảng này (`main.py` trong repo) để xác nhận thứ
  tự index trong mảng khớp CHÍNH XÁC với thứ tự group/base_symbol_number
  của mình (cả hai đều sort theo cùng thứ tự thư mục).
- Xem 6 ảnh của symbol "Index" để xác nhận thứ tự 6 orientation trong
  dataset khớp đúng thứ tự `fill` 0-5 (Palm/Side/Back × Wall/Floor) đã
  dùng — khớp hoàn toàn.
- Viết script tính góc `flexion` mỗi khớp = góc giữa 2 vector xương liên
  tiếp (vd mcp flexion = góc giữa wrist→mcp và mcp→pip), lấy median qua 48
  lần chụp để ổn định.
- Kết quả xác nhận đúng hướng đã gán trước đó (vd "Index Bent" thật sự có
  index bị gập khác "Index" thường — pip 46°/8° khác biệt rõ), nhưng con số
  cụ thể lệch khá xa so với đoán (vd ngón "duỗi thẳng" thật ra không phải
  0° mà 2-20°, ngón "cuộn" thật ra 104-167° chứ không phải 100°).
- Đã thay góc khớp (`mcp`/`pip`/`dip`/`cmc`/`ip`) của **cả 11 symbol đã
  đăng ký** bằng số liệu thật này, cập nhật docstring từng file ghi rõ
  nguồn + phương pháp + giới hạn (đây là ước lượng MediaPipe trên ảnh
  thật, KHÔNG phải motion-capture đã xác thực — bản thân benchmark cũng
  không claim vậy). `abduction` (độ xoè ngón) chưa đo được bằng cách này,
  vẫn giữ nguyên số đoán cũ.
- Phát hiện phụ: Group 6 "Index Middle Ring" có ngón áp út (ring) ở tư thế
  **lưng chừng** (không thẳng hẳn như index/middle, không cuộn hẳn như
  pinky) — dữ liệu thật giữ nguyên sắc thái này thay vì ép về nhị phân
  thẳng/cuộn như model cũ.
- Cập nhật lại test đã pin cứng góc cũ (`test_group_02.py`..`test_group_10.py`,
  `test_group_01.py`) theo số liệu mới. `mypy --strict` sạch, `pytest`
  91/91 pass, đã render lại `fsw-r-viz` xác nhận bằng mắt (`IndexBent` giờ
  thấy rõ ngón trỏ gập khác `Index`, Group 6 thấy đúng ring lưng chừng).

## Làm full toàn bộ 261 base symbol (cả 10 group Category 1)

Sau khi đã có pipeline dữ liệu thật (dataset benchmark) chạy ổn cho 11 base
symbol mẫu, người dùng yêu cầu làm full toàn bộ base symbol còn lại của cả
10 group cùng phương pháp. Xây 2 script tự động hoá trong scratchpad:

- `gen_group.py`: với 1 group + danh sách `base_symbol_number` cần thêm,
  tự động (1) lấy tên thật từng symbol bằng cách tải trang
  `signwriting.org` tương ứng và regex tiêu đề `<title>` (không đoán tên),
  (2) tính góc khớp thật từ file `.npy` MediaPipe cục bộ (cùng phương pháp
  median-flexion đã dùng cho 11 symbol đầu), (3) in ra code Python đã sẵn
  sàng dán vào file group (đúng pattern `@register_symbol` + class kế thừa
  template group + docstring nguồn).
- `gen_test.py`: đọc lại chính file group `.py` vừa cập nhật (parse
  `@register_symbol`/tên class bằng regex), sinh ra file test parametrize
  hoá đầy đủ (`pytest.mark.parametrize` trên danh sách toàn bộ symbol trong
  group) — thay cho việc viết tay từng hàm test riêng như 11 symbol đầu
  (không scale được lên hàng trăm symbol).

Chạy tuần tự cho từng group (từ nhỏ đến lớn để dễ phát hiện lỗi sớm): Group
4 (8), Group 1 (14), Group 10 (16), Group 2 (16), Group 7 (22), Group 8
(19), Group 6 (30), Group 3 (38), Group 9 (40), Group 5 (58, lớn nhất). Mỗi
group sau khi thêm: `mypy --strict` sạch + `pytest tests/test_group_0N.py`
pass toàn bộ trước khi sang group kế tiếp.

**Kết quả: đủ 261/261 base symbol Category 1 (Hands), cả 10/10 group.**
`mypy --strict` sạch (37 file), `pytest` **1358/1358 pass** (tăng từ 91 khi
mới xong 11 symbol mẫu). Sau khi hoàn thành, 2 test kiểm tra "symbol chưa
đăng ký sẽ raise `ValueError`" (`test_registry.py`,
`test_fswr_converter.py`) bị hỏng — lý do: 2 test này trỏ tới key `"S14d10"`
(group 5, base_symbol_number 2), giờ đã là symbol hợp lệ và có đăng ký, nên
không còn raise nữa. Đã sửa: vì toàn bộ range hex hợp lệ của Category 1
(`0x100–0x204`) giờ đã đăng ký kín (không có khoảng trống nào giữa 10
group, đã verify bằng cách cộng dồn `_HAND_GROUP_START` + size từng group),
không còn cách nào tạo ra 1 FSW key "hợp lệ nhưng chưa đăng ký" thật để test
qua string. Chuyển sang test trực tiếp phần lõi: `test_registry.py` gọi
thẳng `registry.build_symbol()` với 1 `ParsedFSWSymbol` tự tạo (group/
base_symbol_number không tồn tại trong bảng registry); `test_fswr_converter.py`
monkeypatch `build_symbol` để xác nhận `ast_to_fswr()` truyền đúng
`ValueError` lên trên. `fsw-r-viz` (`mypy --strict` + `pytest`) vẫn xanh
sau thay đổi lớn này ở `fsw-r`.

## Refactor tầng Group sang data-driven + bảng ISWA valid combinations

Sau khi Category 1 xong 261/261, đo lại thực tế thì thấy tầng `groups/`
(kiến trúc Template Method — `SymbolGroupN` cung cấp template, `BaseSymbolX`
override) đã sụp đổ trên thực tế:

| Chỉ số | Giá trị |
|---|---|
| Base symbol override `get_joint_pose()` (không dùng template) | **251/261 (96%)** |
| Base symbol thực sự dùng `_default_joint_pose()` của group | 10/261 (đúng 1/group) |
| `get_wrist_orientation()` có nội dung **y hệt** `return self._default_wrist_orientation()` | **261/261 (100%)** |
| Dòng code `src/fsw_r/groups/` | 5810 dòng, cho 261 class chỉ khác nhau ở 15 con số/class |

Kết luận: đây là **dữ liệu bị lưu dưới dạng class**, không phải hành vi
(behavior) thật sự khác nhau giữa các symbol. Đồng thời phát hiện thêm 1 vấn
đề đúng đắn khác: `FSWBaseSymbol.__init__` chỉ validate `fill`/`rotation`
theo range TOÀN CỤC (0-5 / 0-15), trong khi ISWA thật ra định nghĩa tập hợp
lệ RIÊNG cho từng base symbol (652 base × 6 fill × 16 rotation = 62.592 tổ
hợp khả dĩ, nhưng chỉ 37.811 — 60,4% — là symbol thật) — framework cũ chấp
nhận và render cả những symbol không tồn tại (vd `01-05-002` với `fill=0`)
mà không báo lỗi.

**Phần 1 — bảng ISWA valid combinations (làm trước, độc lập):**

Nguồn dữ liệu: font TTF chính thức `@sutton-signwriting/font-ttf`
(`SuttonSignWritingLine.ttf`) — cmap của font này chính là danh sách trắng
37.811 symbol thật (đã verify: font Line và font Fill cho cùng tập id).
`scripts/gen_valid_combinations.py` tải font qua `npm pack` (fetch package
thật, không scrape web), decode cmap bằng công thức nghịch đảo của
`convert.key2id` (`sutton-signwriting/core`), ghi ra
`data/iswa_valid_combinations.json`. Script tự kiểm chứng số liệu ra so với
số liệu đã verify độc lập trước (tổng 37.811 symbol, 652 base, tỉ lệ 60,4%,
8 ngoại lệ của Category 1) và exit code khác 0 nếu sai khớp — chạy lại cho
ra JSON **byte-for-byte giống hệt** file đã commit.

`core/iswa_data.py` load bảng này (`importlib.resources`, load 1 lần lúc
import) và expose `valid_combinations_for(base_hex)` /
`is_valid_symbol(base_hex, fill, rotation)`. `FSWBaseSymbol.__init__` giờ
validate theo bảng này thay vì range toàn cục — vd tạo `01-05-002` với
`fill=0` giờ raise `ValueError` nêu rõ `fills=[1]` là tập hợp lệ thật, thay
vì âm thầm chấp nhận. Hệ quả phụ: 7 base symbol (trong Group 5 và 10) không
hỗ trợ `fill=0` — 2 test cũ giả định `fill=0` luôn hợp lệ với mọi symbol
phải sửa lại (skip đúng 7 case đó thay vì assert sai).

**Phần 2 — HandSymbol thay 261 class:**

1. `scripts/export_joint_poses.py` (migrate 1 lần): import toàn bộ
   `groups/*.py` cũ, gọi `get_joint_pose()` thật của từng class đã đăng ký,
   ghi ra `data/hand_joint_poses.json` (261 entry, kèm tên thật + `_meta`
   ghi rõ nguồn/phương pháp/giới hạn dữ liệu MediaPipe — giữ nguyên, không
   mất, so với docstring cũ). KHÔNG tính lại góc nào — chỉ trích xuất số đã
   có.
2. `core/pose_table.py` load JSON này thành `HAND_POSE_TABLE`
   (`symbol_id -> HandJointPose`) + `HAND_NAME_TABLE`, fail fast lúc import
   nếu JSON thiếu/sai cấu trúc.
3. `core/hand_symbol.py`: 1 class `HandSymbol` duy nhất cho cả 261 base
   symbol — `get_joint_pose()` tra `HAND_POSE_TABLE[self.symbol_id]`,
   `get_wrist_orientation()` vẫn `return self._default_wrist_orientation()`
   (công thức generic, không đổi).
4. `core/registry.py` viết lại: bỏ decorator `@register_symbol` + dict 261
   entry, `build_symbol()` giờ chỉ cần `symbol_id in HAND_POSE_TABLE` là đủ.
   Giữ `_OVERRIDES: dict[str, Constructor]` làm chỗ mở rộng cho tương lai
   (phương án C) — hiện rỗng (0/261 symbol cần override hành vi riêng).
5. **Kiểm chứng không đổi hành vi trước khi xoá `groups/`:** script tạm (không
   commit) so `get_joint_pose()`/`get_wrist_orientation()`/`hand_side`/
   `symbol_id` của cả 261 class cũ vs `HandSymbol` mới, qua ~6100 tổ hợp
   (symbol × fill × rotation) — khớp tuyệt đối. Chỉ sau khi pass mới xoá
   `groups/` (10 file, 5810 dòng).
6. `demo.py` (`fsw-r`) và `demo.py`/2 file test (`fsw-r-viz`) trước đó import
   thẳng class cụ thể từ `groups/*` — sửa lại dùng `symbol_from_fsw()` /
   `HandSymbol(...)` trực tiếp. Render lại 2 ảnh demo của `fsw-r-viz`:
   `index_finger_fills.png` (dùng "Index", không đổi logic) ra **byte-for-byte
   giống hệt** ảnh trước refactor — bằng chứng trực quan công thức
   rotation/fill không hề đổi.

**Test suite viết lại, số lượng GIẢM MẠNH — đây là kết quả mong muốn, không
phải hồi quy:** phần lớn trong 1358 test cũ (10 file `test_group_0N.py`,
mỗi file parametrize hoá đầy đủ theo từng symbol trong group) đang so sánh
dữ liệu với chính nó — vd "`get_joint_pose()` có bằng đúng giá trị nó được
khởi tạo từ không" là tautology 1 khi góc khớp chuyển thành tra bảng
(`HandSymbol.get_joint_pose()` CHỈ làm mỗi việc tra `HAND_POSE_TABLE`). Tệ
hơn, nhiều thuộc tính (wrist orientation bất biến theo symbol, joint pose
bất biến theo fill/rotation) vốn KHÔNG phụ thuộc symbol nào cả — công thức
chỉ nhìn `fill`/`rotation` — nên test lặp lại cùng 1 khẳng định 261 lần
không có thêm giá trị. Viết lại thành:
- `test_pose_table.py`: tính toàn vẹn của bảng 261 entry (đủ số lượng,
  không thiếu ngón/khớp, mọi flexion trong khoảng vật lý hợp lý), cộng vài
  giá trị chốt cụ thể (Index, Index Bent) để bắt lỗi hỏng dữ liệu âm thầm.
- `test_hand_symbol.py`: đúng phần THẬT SỰ khác nhau theo từng symbol —
  dựng object + `symbol_id`/`name` đúng (261 case), và round-trip qua
  `symbol_from_fsw()` thật cho cả 261 base hex (261 case, kiểm tra công thức
  base_hex mỗi group không lệch 1 đơn vị nào) — cộng đúng 1 test (không
  parametrize) khoá bất biến "joint pose không đổi theo fill/rotation".
- `test_wrist_orientation.py`: giữ nguyên các test hành vi quan trọng nhất
  từ `test_group_01.py` cũ (bug gimbal-lock, quy tắc 180°, Six Palm
  Facings...), chỉ đổi từ `BaseSymbol01_01_001_Index` sang `HandSymbol` —
  vẫn dùng "Index" làm ví dụ vì công thức không phụ thuộc symbol nào.
- `test_hand_side.py`/`test_registry.py`/`test_fswr_converter.py`/
  `test_iswa_data.py`: cập nhật để dựng `HandSymbol` trực tiếp thay vì
  import class đã xoá, giữ nguyên nội dung test.

Kết quả: `pytest` từ **1358 → 596** (fsw-r-viz vẫn 4/4), `mypy --strict`
sạch (**41 → 25 file** — do 10 file `groups/*.py` + `__init__.py` bị xoá),
dòng code `src/fsw_r` từ **~6300 → 858**. `renderer.py` vẫn hoàn toàn không
biết gì về `HandSymbol` cụ thể (chỉ phụ thuộc `FSWRenderableSymbol` +
`HandRigProvider`, cả 2 đều abstract) — nguyên tắc category/group-agnostic
của renderer không đổi qua refactor này.

## `base_hex` làm khoá duy nhất xuyên suốt pipeline

Sau đợt refactor data-driven ở trên, phát hiện thêm 1 vấn đề kiến trúc
khác: `base_hex` (danh tính gốc của mọi symbol ISWA) bị **vứt đi ngay lúc
parse rồi dựng lại ở tầng dưới** —
`parse_fsw_symbol_key()` tách `base_hex` thành `(group, base_symbol_number)`
rồi bỏ luôn số gốc; `FSWBaseSymbol.__init__` sau đó **dựng lại** `base_hex`
từ `HAND_GROUP_START[group-1] + (base_symbol_number-1)`. Hệ quả đo được:

1. **Parser không đọc nổi key ngoài Category 1** — `parse_fsw_symbol_key`
   raise `ValueError` cho bất kỳ key nào ngoài range Hands
   (`0x100–0x204`), dù `data/iswa_valid_combinations.json` (từ Phần 1) đã
   có sẵn dữ liệu cho toàn bộ 652 base symbol của cả 7 category.
2. **2 hệ khoá song song phải giữ đồng bộ thủ công**: bảng valid
   combinations khoá `base_hex`, còn `hand_joint_poses.json` khoá
   `symbol_id` (chuỗi `"01-05-002"`) — 2 cách biểu diễn cùng 1 con số,
   không có gì đảm bảo chúng luôn khớp nhau ngoài kỷ luật code thủ công.
3. **Lỗi im lặng ở chỗ dựng lại `base_hex`**: `group` ngoài phạm vi 1-10 ra
   `IndexError`; `group` hợp lệ nhưng `base_symbol_number` quá lớn tính ra
   1 `base_hex` thuộc group/category KHÁC mà không báo gì.
4. **Thêm Category 2 trước đó sẽ phải sửa 6/9 file trong `core/`** — trái
   hẳn nguyên tắc "thêm 1 category chỉ thêm code, không sửa code cũ" đã đặt
   ra từ đầu dự án.

**Sửa theo 4 phần, mỗi phần test xanh rồi mới sang phần tiếp, commit riêng
từng phần:**

**Phần A — `iswa_data.py` thành nguồn sự thật đầy đủ về cấu trúc ISWA.**
Mở rộng từ chỉ có `HAND_GROUP_START` (10 ranh giới Category 1) thành đủ
`GROUP_START` (30 ranh giới, toàn bộ ISWA) + `CATEGORY_START` (7 ranh
giới) — lấy trực tiếp từ `fsw-structure.js` thật (tải qua `npm pack`, xem
mục "Các category ISWA" ở `ROADMAP.md` để biết chi tiết + 1 lỗi đã phát
hiện và sửa: bảng category thật có 7 phần tử chứ không phải 8 như bản nháp
`ROADMAP.md` cũ đoán — Trunk và Limb dùng chung 1 category). Thêm các hàm
dẫn xuất thuần (`category_of`, `group_of`, `base_symbol_number_of`,
`symbol_id_of`, `base_hex_of`) — tất cả tính từ `base_hex`, không có state.
Test round-trip đầy đủ cả 652 giá trị
(`base_hex_of(category_of(b), group_of(b), base_symbol_number_of(b)) == b`)
+ test biên ở mọi ranh giới category/group.

**Phần B — `base_hex` chảy xuyên suốt, không bị tách/dựng lại.**
`ParsedFSWSymbol` và `FSWBaseSymbol` giờ chỉ giữ `base_hex` (+ `fill`,
`rotation`) — `category`/`group`/`base_symbol_number`/`symbol_id` thành
**property tính lúc cần** (gọi hàm ở Phần A), không còn field lưu trữ
riêng nào có thể lệch pha với `base_hex`. `parse_fsw_symbol_key()` giờ chỉ
validate range ISWA đầy đủ (`0x100–0x38b`), không chặn theo category nữa —
`parse_fsw_symbol_key("S22b03")` (1 key Movement thật) giờ parse thành
công; việc "category đó có được hỗ trợ không" chuyển hẳn xuống
`registry.py` (đúng tầng của nó).

**Phần C — bảng pose tổng quát hoá + registry dispatch theo category.**
`core/pose_table.py`'s `PoseTable` giờ là class generic
(`Generic[PoseT]`), khoá theo `base_hex`, thân class **không hề nhắc tới
`HandJointPose`** — kiểu dữ liệu cụ thể do hàm `parse` truyền vào lúc khởi
tạo quyết định. `data/hand_joint_poses.json` đổi khoá top-level từ
`symbol_id` sang `base_hex` (giữ `symbol_id` làm 1 field bên trong mỗi
entry để đọc bằng mắt còn dễ + dùng trong thông báo lỗi) — đã verify bằng
script tạm (không commit) diff từng entry trước/sau: **không đổi 1 giá trị
góc khớp nào**, chỉ đổi cấu trúc khoá. `registry.py` viết lại
`build_symbol()` để dispatch theo `category_of(base_hex)` qua
`_CATEGORY_SYMBOL: dict[int, Constructor]` (hiện `{1: HandSymbol}`) thay vì
kiểm tra `symbol_id` có trong bảng pose hay không — `symbol_from_fsw("S22b03")`
giờ raise đúng thông báo trung thực `"Category 2 is not supported yet"`
thay vì lỗi parse chung chung.

**Phần D — `hand_side` thành abstract, per-category.** `FSWBaseSymbol.hand_side`
trước đó là property concrete giả định MỌI category đều mã hoá tay trong
`rotation` giống Category 1. Kiểm chứng trên
`sign-language-processing/signbank-plus` (257.800 sign) phát hiện **quy tắc
này KHÔNG áp dụng cho Category 2** (Movement) — xem số liệu đầy đủ ở
`ROADMAP.md` Pha 2. `hand_side` giờ abstract, trả `HandSide | None`;
`HandSymbol` implement lại đúng quy tắc cũ (hành vi Category 1 không đổi 1
chút nào). `HandMeshRenderer3D.render()` raise `ValueError` rõ ràng nếu
`hand_side is None` thay vì truyền `None` xuống `HandRigProvider` một cách
không định nghĩa.

**Bài kiểm tra khả năng mở rộng (theo đúng yêu cầu của brief — báo cáo
trung thực, không tự nói "đạt" nếu chưa đạt):** giờ muốn thêm Category 2
(Movement) cần:
- **Sửa đúng 1 dòng** trong 1 file `core/` đã có sẵn: thêm
  `{2: MovementSymbol}` vào `_CATEGORY_SYMBOL` trong `registry.py`. Không
  file `core/` nào khác (`fsw_symbol_key.py`, `fsw_base_symbol.py`,
  `iswa_data.py`, `renderer.py`) cần sửa — tất cả đã category-agnostic.
- Cộng thêm code **HOÀN TOÀN MỚI** (không phải sửa code cũ):
  1 kiểu dữ liệu mới ("motion path", không tái dùng `HandJointPose`), 1
  class `MovementSymbol` mới (giống `HandSymbol` nhưng implement
  `hand_side` khác — xem phát hiện fill/rotation ở `ROADMAP.md`), 1
  `PoseTable[MotionPath](...)` instance mới + hàm parse riêng, 1 file
  `data/movement_paths.json` mới. Đây là việc **thêm**, không phải sửa hạ
  tầng chung — đúng tinh thần "thêm category = thêm code, không sửa code
  cũ" đã đặt ra.
- Renderer animation (interpolate theo thời gian) vẫn là việc thật sự mới,
  chưa có hạ tầng — `HandMeshRenderer3D` hiện chỉ render 1 pose tĩnh.

Kết quả: `pytest` **615/615 pass** (fsw-r), `mypy --strict` sạch (26 file),
`fsw-r-viz` vẫn 5/5 pass + ảnh demo render byte-identical (không đổi công
thức số nào qua cả 4 phần). `grep -rn "symbol_id" src/` xác nhận
`symbol_id` chỉ còn xuất hiện ở vai trò hiển thị/thông báo lỗi/field mô tả
trong JSON — không còn làm khoá tra cứu ở bất kỳ đâu.

## Pha 2 — Category 2 (Movement): contract trừu tượng generic + `MovementSymbol`

### Phần 0 — phát hiện: "hạ tầng đã sẵn sàng" là SAI

Bắt tay làm `MovementSymbol` thì phát hiện ngay: `core/renderable_symbol.py`'s
`FSWRenderableSymbol` khai `get_joint_pose() -> HandJointPose` làm
**abstract method cứng** — nghĩa là MỌI symbol (kể cả Category 2, vốn không
có góc khớp mà có quỹ đạo chuyển động) đều bị ép implement đúng chữ ký đó.
`MovementSymbol` không kế thừa nổi class này. `PoseTable` và
`registry.py`'s category dispatch (từ đợt refactor `base_hex` trước) đã
generic thật, nhưng **contract render thì chưa** — ghi chú "hạ tầng đã sẵn
sàng cho Pha 2" ở `ROADMAP.md` là sai, đã sửa lại (xem commit riêng, trước
khi viết bất kỳ dòng nào của `MovementSymbol`).

### Phần A — tách contract trừu tượng theo category

`core/renderable_symbol.py`: `FSWRenderableSymbol` giờ chỉ là **marker
chung** (không method nào) — `FSWHandRenderable` (Category 1,
`get_joint_pose()`) và `FSWMotionRenderable` (Category 2,
`get_motion_path()`) là 2 subclass riêng khai đúng contract của category
mình. `HandMeshRenderer3D.render()` (core) và `plot_hand.py` (fsw-r-viz)
đổi type hint sang `FSWHandRenderable` cụ thể — **không thêm `isinstance`
phân nhánh theo category ở đâu cả**, đúng ràng buộc đề ra: nhầm category là
lỗi kiểu tĩnh (mypy), không phải nhánh runtime. `registry.py`/
`fswr_converter.py` vốn đã dùng kiểu chung `FSWRenderableSymbol` từ đợt
refactor trước nên không cần đổi gì.

### Phần B — phát hiện cấu trúc `(path_type × plane)`

10 group của Category 2 KHÔNG phải 10 khái niệm độc lập (khác Category 1,
nơi 10 group là 10 dáng tay giải phẫu độc lập, không phân rã được) — chúng
là tích của 2 trục trực giao, đọc thẳng ra được từ chính TÊN group thật
(ISWA Manual Chapter 2):

| Group | Tên thật | path_type | plane | is_hit |
|---|---|---|---|---|
| 11 | Contact | CONTACT | *(không rõ)* | |
| 12 | Finger Movement | FINGER | *(không rõ)* | |
| 13 | Straight Wall Plane | STRAIGHT | WALL | |
| 14 | Straight Diagonal Plane | STRAIGHT | DIAGONAL | |
| 15 | Straight Floor Plane | STRAIGHT | FLOOR | |
| 16 | Curves Wall Plane | CURVED | WALL | |
| 17 | Curves Hit Wall Plane | CURVED | WALL | ✓ |
| 18 | Curves Hit Floor Plane | CURVED | FLOOR | ✓ |
| 19 | Curves Floor Plane | CURVED | FLOOR | |
| 20 | Circles | CIRCLE | *(không rõ)* | |

Hệ quả: 242 base symbol phủ được bằng **5 path primitive (`PathType`) + 3
plane (`MovementPlane`) + 1 bảng tra 10 dòng**, không cần "đo" như Category
1's 261 dáng tay riêng biệt. `MotionPath`/`PathType`/`MovementPlane` thêm
vào `core/types.py`. `core/movement_paths.py`'s `sample_trajectory()` sinh
điểm 3D thật (dùng `scipy.spatial.transform.Rotation`, không tự viết
quaternion) — canonical shape theo `path_type` → xoay quanh Z bằng đúng
công thức compass của Category 1 (`(rotation % 8) * 45°`, tái dùng nguyên
văn) → đưa vào `plane` (tái dùng cách xử lý Wall/Floor Plane của Category
1). Test khoá: `STRAIGHT` trong `WALL` nằm trong mặt XY (Z≈0), trong
`FLOOR` nằm trong mặt XZ (Y≈0).

### Phần C — `MovementSymbol` + sinh bảng bằng công thức

`scripts/gen_movement_paths.py` sinh `data/movement_paths.json` (242 entry,
khoá `base_hex`) **bằng công thức** từ bảng 10 dòng ở Phần B +
`GROUP_START` — khác hẳn Category 1 (phải "đo" từng symbol từ
`3d-hands-benchmark`), vì hình học Category 2 hoàn toàn suy ra được từ
group. `core/pose_table.py` thêm `MOVEMENT_PATH_TABLE: PoseTable[MotionPath]`
(instance thứ 2, class `PoseTable` không cần sửa gì). `core/movement_symbol.py`'s
`MovementSymbol(FSWMotionRenderable)` là class duy nhất cho cả 242 base
symbol. `registry.py`: `_CATEGORY_SYMBOL = {1: HandSymbol, 2: MovementSymbol}`.

**Quyết định `hand_side = None` cho Category 2 (bằng chứng đo trên
`sign-language-processing/signbank-plus`, 257.800 sign, lọc sign chỉ có
đúng 1 symbol tay):**

| Tay (suy từ Cat 1) | Cat 2 rotation 0-7 | Cat 2 rotation 8-15 |
|---|---|---|
| RIGHT | 62,2% | 37,8% |
| LEFT | 58,5% | 41,5% |

Nếu `rotation ≥ 8 → LEFT` đúng cho Cat 2 thì hàng LEFT phải gần 100% — 2
hàng gần như giống hệt nhau, tức **`rotation` không mã hoá tay ở Category
2** (nó là hướng/gương của bản thân động tác).

| Tay (suy từ Cat 1) | Cat 2 fill=0 | Cat 2 fill=1 |
|---|---|---|
| RIGHT | 97,4% | 0,5% |
| LEFT | 72,0% | 26,7% |

`fill` có tín hiệu rõ hơn nhiều (fill=1 nhiều hơn ~53 lần khi tay trái —
khớp quy ước SignWriting: fill code 0/1/2 = ISWA fill 1/2/3 =
phải/trái/cả hai) nhưng vẫn còn nhiễu thật (LEFT vẫn 72% dùng fill=0).
**Chưa đủ tin cậy để implement thành quy tắc cứng** — `MovementSymbol.hand_side`
trả `None`, trung thực hơn đoán sai ~28%. Cần đối chiếu Lessons in
SignWriting chương 6 trước khi chốt quy tắc thật. Chưa thêm `HandSide.BOTH`
(chưa cần, vì hiện `None` chứ chưa gán giá trị nào).

### Danh sách giả định CHƯA kiểm chứng (tách riêng, không chôn trong docstring)

1. `plane` của group 11 (Contact), 12 (Finger Movement), 20 (Circles) —
   tên group không nói rõ; lưu `null`, `sample_trajectory()` fallback về
   WALL lúc render (lựa chọn ít tuỳ tiện nhất, không phải quy tắc đã xác nhận).
2. `is_hit` — mới là cờ mang theo, CHƯA có ngữ nghĩa hình học/render nào cả.
3. `curvature`/`amplitude`/`repeat` — hằng số theo `path_type`/group, KHÔNG
   suy từ `base_symbol_number` — chưa rõ nguồn nào cho biết các symbol
   trong cùng 1 group khác nhau cụ thể ra sao (ISWA chắc có mã hoá, nhưng
   chưa xác định được).
4. Hình dạng canonical của từng `PathType` (đường thẳng, cung tròn, dao
   động nhỏ cho FINGER...) — tự thiết kế hợp lý, không suy từ đo đạc/spec ISWA nào.
5. Công thức xoay `rotation`/`plane` cho Category 2 — tái dùng nguyên công
   thức đã chart-verify của Category 1, CHƯA verify độc lập cho Category 2.
6. `MovementSymbol.get_wrist_orientation()` — cũng tái dùng công thức
   Category 1 (`_default_wrist_orientation()`), cùng lý do/rủi ro như trên.
7. `hand_side` của Category 2 — xem quyết định `None` ở trên, đây là điểm
   chưa chốt lớn nhất, không phải chi tiết nhỏ.

### Bài kiểm tra khả năng mở rộng (Category 5 — Body, group 27-28, 18 base symbol)

Báo cáo trung thực theo đúng yêu cầu, **không tô hồng**: thêm Category 2 lần
này KHÔNG chỉ sửa đúng 1 dòng `registry.py` như ghi chú (đã sửa) ở
`ROADMAP.md` từng khẳng định — thực tế còn cần sửa THÊM `core/types.py`
(thêm `MotionPath`/`PathType`/`MovementPlane`) và `core/pose_table.py`
(thêm `MOVEMENT_PATH_TABLE` + hàm parse), cả hai đều là file `core/` ĐÃ CÓ
SẴN. Điểm quan trọng: **mọi thay đổi ở 2 file này đều là THÊM MỚI thuần tuý
(thêm class/hàm mới), không sửa/xoá 1 dòng code cũ nào** — khác hẳn kiểu
"sửa lại logic cũ" mà nguyên tắc ban đầu muốn tránh. Với Category 5, dự
kiến cần đúng những việc THÊM MỚI tương tự:
- `core/types.py`: thêm 1 kiểu pose mới (vd `BodyPose`) — thêm class, không sửa gì cũ.
- `core/renderable_symbol.py`: thêm 1 abstract contract mới (vd
  `FSWBodyRenderable(FSWRenderableSymbol)`) — thêm class, không sửa gì cũ.
- `core/pose_table.py`: thêm 1 `PoseTable[BodyPose]` instance + hàm parse —
  thêm hàm/biến, không sửa gì cũ.
- `core/registry.py`: thêm đúng 1 dòng `{5: BodySymbol}` vào `_CATEGORY_SYMBOL`.
- File mới hoàn toàn: `core/body_symbol.py`, `data/body_poses.json` +
  script sinh, có thể `core/body_geometry.py` nếu cần hình học riêng.

Không có file nào cần SỬA LOGIC ĐÃ CÓ (chỉ thêm mới) — nên Phần A (tách
contract) coi như đã đạt đúng mục tiêu, chỉ là "1 dòng registry.py" ở
`ROADMAP.md` cũ nói chưa đủ chính xác, đã sửa lại thành mô tả đúng thực tế
trên.

## Pha 3 — `SignTimeline` (MVP-1): trục thời gian FSW không có sẵn

### Vấn đề

Tới hết Pha 2, framework trả lời được *"ký hiệu này là tư thế/quỹ đạo gì?"*
nhưng CHƯA trả lời được *"các ký hiệu đó xảy ra khi nào, ở đâu, do tay nào?"*
FSW mô tả 1 sign bằng **bố cục không gian 2D** (danh sách ký hiệu + toạ độ
`(x, y)`); dựng video cần **chuỗi trạng thái theo thời gian**. `SignTimeline`
(package mới `fsw_r/timeline/`) là tầng dịch giữa 2 thứ đó — **chỉ tiêu thụ
đầu ra của `core/fswr_converter.py`, không sửa file nào trong `core/`** (đã
xác nhận bằng `git diff --stat` sau mỗi commit của pha này — luôn rỗng).

```
tuple[PositionedSymbol, ...]  --[build_timeline]-->  SignTimeline  --[sample]-->  chuỗi pose theo fps
   (core/fswr_converter.py)        (timeline/build.py)                (timeline/sample.py)
```

### Phạm vi MVP-1 — và lý do chọn đúng phạm vi này

Sign có **đúng 1 ký hiệu tay** (Category 1), **tối đa 1 ký hiệu chuyển động**
(Category 2), **không có ký hiệu category nào khác**. Đo trên SignBank+
(257.800 sign): phạm vi này chiếm **6,2%** (~16.000 sign thật).

Đây là quyết định thiết kế, không phải cắt giảm cho tiện: MVP-1 bỏ qua được
TOÀN BỘ bước cần suy đoán — 1 track duy nhất nên không có bài toán gán
chuyển động cho tay nào; 1 ký hiệu tay nên không nhập nhằng "hai tay đồng
thời" vs "một tay hai thời điểm"; thứ tự thời gian do hướng mũi tên quyết
định nên không cần dùng `y` làm proxy thời gian. Kết quả: **mọi bước trong
MVP-1 đều tất định**. Sign ngoài phạm vi raise `UnsupportedSignError` nêu rõ
lý do (bao nhiêu ký hiệu tay/chuyển động, có category nào khác) — không đoán
bừa rồi trả timeline sai.

### Kiến trúc 5 giai đoạn

| Giai đoạn | File | Việc làm |
|---|---|---|
| D1. Phân loại vai trò | `classify.py` | `category_of()` → `SymbolRole` (tra bảng) |
| D2. Gán track | `classify.py`/`build.py` | `hand_side` (Cat 1) → track; ký hiệu chuyển động gán vào track duy nhất đang có |
| D3. Phân đoạn thời gian | `build.py` | không chuyển động → 1 keyframe; có chuyển động → N keyframe từ `sample_trajectory()` |
| D4. Neo không gian | `anchor.py` | `(x, y)` signbox → toạ độ body-space 3D |
| D5. Lấy mẫu/nội suy | `sample.py` | SLERP (hướng cổ tay) + tuyến tính (góc khớp, vị trí) → chuỗi `PoseFrame` theo fps |

**Bảng độ tin cậy** (nội dung có giá trị cho báo cáo/luận văn):

| Giai đoạn | Cơ sở | Độ tin cậy ở MVP-1 |
|---|---|---|
| Phân loại vai trò | `category_of()` | Tất định |
| Gán track | `hand_side` Cat 1 | Tất định |
| Phân đoạn thời gian | 1 ký hiệu tay → không nhập nhằng | Tất định |
| Neo không gian | Chuẩn hoá + `plane` | Có cơ sở, **chưa hiệu chỉnh tỉ lệ** |
| Nội suy | SLERP + tuyến tính | Tất định |

### Phát hiện & quyết định kỹ thuật đáng chú ý

1. **Dấu trục y.** Đo trên 60.000 sign SignBank+: y trung vị ký hiệu đầu/mặt
   (Cat 4) = 483, y trung vị ký hiệu tay (Cat 1) = 496. Đầu ở TRÊN tay trên cơ
   thể nhưng có y NHỎ HƠN → `y` tăng XUỐNG DƯỚI (toạ độ màn hình). `anchor()`
   đảo dấu `v = (500 - y) / 250`. Đây là dòng code rủi ro nhất trong cả
   package — sai dấu thì mọi động tác lộn ngược mà **không test nào khác bắt
   được** (không có gì "rõ ràng sai" như trái/phải bị đổi chỗ). Khoá lại bằng
   `test_smaller_y_gives_a_higher_position` (E1).

2. **`sample_trajectory()` tái dùng trực tiếp, không viết lại.** Trục z không
   có trong signbox — suy từ `MotionPath.plane` (đã xử lý ở Pha 2). `build.py`
   gọi thẳng `core/movement_paths.py`'s `sample_trajectory()`.

3. **Số lượng keyframe cho ký hiệu chuyển động — lệch có chủ đích so với chữ
   nghĩa gốc của brief.** Brief tả "2 keyframe (đầu quỹ đạo, cuối quỹ đạo)",
   nhưng nếu chỉ 2 keyframe thì `PathType.CURVED`/`CIRCLE` sẽ bị D5 nội suy
   tuyến tính thành ĐƯỜNG THẲNG — đúng thứ mà quy tắc "đừng nội suy đè lên
   quỹ đạo mũi tên đã định nghĩa" (D5) muốn tránh. Đã tổng quát hoá: dùng
   **1 keyframe cho mỗi điểm** `sample_trajectory()` trả về (không chỉ 2) —
   với `PathType.STRAIGHT` các điểm giữa thẳng hàng nên hành vi giống hệt
   trường hợp 2 keyframe; chỉ khác biệt thật sự với CURVED/CIRCLE. Ghi rõ
   trong code (`build.py`) đây là diễn giải có chủ đích, không phải bỏ qua
   yêu cầu.

4. **Quaternion double-cover — đã KIỂM CHỨNG TRỰC TIẾP, không giả định.**
   Brief yêu cầu kiểm tra xem `scipy.spatial.transform.Slerp` đã tự xử lý
   double-cover (`q` và `-q` biểu diễn cùng 1 phép quay) chưa. Test trực
   tiếp: dựng 2 rotation cách nhau 10°, cố tình đảo dấu quaternion của 1 bên
   (ép `dot < 0` — điều kiện gây lỗi "đi đường dài") rồi feed vào `Slerp`
   (scipy 1.15.3) — kết quả vẫn đi đúng đường ngắn (10°, không phải 350°).
   **Kết luận: scipy đã tự xử lý đúng, KHÔNG cần thêm code lật dấu thủ
   công** (thêm vào sẽ là code thừa, gây hiểu nhầm). Khoá lại bằng 2 test
   (`test_slerp_takes_the_short_path`, `test_scipy_slerp_itself_already_handles_double_cover`)
   để bắt hồi quy nếu 1 version scipy tương lai đổi hành vi này.

5. **Bug phát hiện qua test, không phải qua đọc code.** Viết test "Category 4
   → `UnsupportedSignError`" thì phát hiện: `build_timeline()` ban đầu chỉ
   gate theo `SymbolRole`, nhưng Category 4 dùng CHUNG `SymbolRole.POSTURE`
   với Category 1 (theo đúng bảng `SymbolRole` ở brief) — nên 1 ký hiệu
   Category 4 sẽ bị đếm nhầm thành "ký hiệu tay thứ 2" thay vì bị từ chối
   đúng lý do "category không hỗ trợ". Đã sửa: gate theo SỐ CATEGORY thật
   (1 và 2), không chỉ theo role. (Test dùng object giả lập, không phải FSW
   key thật — Category 4 chưa đăng ký trong `core/registry.py`, nên 1 key
   Category 4 thật đã bị `fsw_to_fswr()` chặn từ trước khi tới `timeline`.)

### Danh sách giả định CHƯA kiểm chứng (tách riêng, không chôn trong docstring)

1. `DEFAULT_SIGN_DURATION = 0.8s` (`build.py`) — chưa có nguồn dữ liệu thời
   lượng thật nào; Category 3 (Dynamics) dự kiến mới cung cấp được.
2. `SIGNBOX_TO_BODY_SCALE = 0.1` (`anchor.py`) — chưa hiệu chỉnh với cơ thể
   3D thật, chỉ là hằng số hợp lý tạm thời.
3. Ánh xạ TUYẾN TÍNH signbox → không gian cơ thể (`anchor()`) — thực tế
   chuyển động cơ thể người có thể phi tuyến (vd góc vai), chưa kiểm chứng.
4. Chưa có ràng buộc giải phẫu (khớp gập vượt quá góc thật) — xem phát hiện
   MediaPipe bên dưới, ghi nhận nhưng CHƯA sửa trong pha này.
5. `hand_side` của Category 2 — kế thừa quyết định `None` từ Pha 2 (chưa
   chốt quy tắc thật), D2 chỉ "né" được vấn đề này nhờ MVP-1 luôn có đúng 1
   track — MVP-2 sẽ phải giải quyết thật.
6. Neo `is_hit` (Category 2's `MotionPath`) — vẫn chưa có ngữ nghĩa hình học
   nào áp dụng ở tầng timeline (kế thừa từ Pha 2).

### Vấn đề đã biết, CHƯA xử lý trong pha này: góc khớp vượt giới hạn giải phẫu

Kiểm tra trực tiếp trên `data/hand_joint_poses.json` (không phải suy đoán):
lọc góc gập khớp PIP (Proximal Interphalangeal) của 4 ngón (trỏ, giữa, áp
út, út) vượt ngưỡng gập tối đa hợp lý của người thật (~110°):

- **119/261 symbol (45,6%)** có ít nhất 1 khớp PIP vượt 110°. Giá trị PIP
  cao nhất tìm thấy: **167°** (`01-06-020` ring, `01-10-001` pinky,
  `01-10-014` ring).
- Phân bố theo ngón (số symbol vi phạm/ngón, có thể trùng nhau nếu 1 symbol
  vi phạm nhiều ngón): **ring 95, pinky 93, middle 55, index 32**.
- Thứ tự này khớp với mức độ bị CHE KHUẤT khi nắm tay (ring/pinky khuất
  nhất, index lộ nhất) — gợi ý đây là **sai lệch có hệ thống của MediaPipe ở
  ngón bị che**, không phải nhiễu ngẫu nhiên.

⚠️ **Lưu ý khác biệt với brief:** brief nêu số liệu "136/261 (52,1%)" — kiểm
tra độc lập với đúng ngưỡng/joint brief mô tả (PIP > 110°) cho ra **119/261
(45,6%)**, không phải 136/261. Phân bố theo ngón (ring 95, pinky 93, middle
55, index 32) và giá trị lớn nhất (167°) khớp CHÍNH XÁC với số liệu brief
nêu, xác nhận đúng phương pháp (PIP, ngưỡng 110°) — chỉ riêng tổng/tỉ lệ
brief nêu không tái lập được, nhiều khả năng là sai số tính toán ở nguồn đưa
ra brief. Dùng số đã tự kiểm chứng (119/261, 45,6%) trong tài liệu, ghi rõ
chênh lệch này thay vì lặng lẽ chọn 1 trong 2 số.

**Không sửa trong pha này** — đây là việc riêng, đã ghi vào `ROADMAP.md`
làm ưu tiên tiếp theo. **Cập nhật:** Pha 6 ("Tầng đánh giá", phía dưới) đã
đo lại chính xác hơn — kiểm cả 8 khớp (không riêng PIP) qua giới hạn AAOS có
trích nguồn, ra **224/261 (85,8%)**, khác con số ước lượng 52,1%/119-261 ở
đây (mục đích/phạm vi đo khác nhau, xem mục "Pha 6" để biết chi tiết và lưu
ý về khả năng lệch định nghĩa CMC ngón cái).

## Pha 4 — Category 3 (Dynamics) & Category 5 (Trunk & Limb / Body): tầng ký hiệu

Task riêng, phạm vi cố ý hẹp: **chỉ dựng tầng ký hiệu** (symbol object + bảng
dữ liệu) cho 2 category còn thiếu ngoài Cat 1/2/4 — **không đụng
`fsw_r/timeline/`**, việc nối Cat 3 (thời gian) và Cat 5 (khung tham chiếu
không gian) vào timeline là pha sau (xem "Việc còn để ngỏ" cuối mục này và
`ROADMAP.md`). Đã làm Category 5 trước (rủi ro thấp, đúng pattern có sẵn),
Category 3 sau (buộc phải đổi kiểu trả về của `build_symbol()`).

### A1 — tên symbol `0x36d` (bắt buộc tra trước khi thiết kế)

Tra trực tiếp `signbank.org/iswa/36d_sg.html` (ISWA 2010 HTML Reference thật,
không đoán): **`0x36d` = "Shoulder Hip Spine"** (`05-01-001-01`), Category 5:
Body, thuộc `SymbolGroup_27` (Trunk). Trang này thực chất là trang **của cả
group 27** (9 base symbol `0x36d`-`0x375` cùng liệt kê trên 1 trang, đánh số
theo base đầu group — không phải 1 trang/1 base symbol như đoán ban đầu);
tương tự `376_sg.html` liệt kê cả group 28 (Limb).

Xác nhận đúng giả thuyết brief đặt ra: `0x36d` là **ký hiệu mốc/tham chiếu
tổng hợp** ("Shoulder Hip Spine" = vai-hông-cột sống gộp chung), không phải 1
tư thế cụ thể — khớp với việc nó chiếm 43,2% token Category 5 và có phạm vi
fill/rotation rất hẹp (3 fill, 4 rotation) so với các base khác trong group.

Tên đầy đủ 18 base symbol (tra được, không đoán):

| Group | base_hex | Tên thật (signbank.org) |
|---|---|---|
| 27 Trunk | `0x36d` | Shoulder Hip Spine |
| 27 Trunk | `0x36e` | Shoulder Hip Positions |
| 27 Trunk | `0x36f` | Shoulder Hip Move Wall Plane |
| 27 Trunk | `0x370` | Shoulder Hip Move Floor Plane |
| 27 Trunk | `0x371` | Shoulder Tilts (from Waist) |
| 27 Trunk | `0x372` | Torso Straight Stretch Wall |
| 27 Trunk | `0x373` | Torso Curved Bend Wall |
| 27 Trunk | `0x374` | Torso Twist Floor Plane |
| 27 Trunk | `0x375` | Upper Body Tilts (from Hip Joints) |
| 28 Limb | `0x376` | Limb Combinations |
| 28 Limb | `0x377`-`0x37d` | Limb Length 1..7 |
| 28 Limb | `0x37e` | Fingers |

Group 28 (Limb) hoá ra KHÔNG phải 9 khớp giải phẫu riêng biệt (vai/khuỷu/hông/
gối...) như có thể đoán từ tên category — mà là các khối dựng hình cho 1
"chi" (tay hoặc chân) sơ đồ hoá với **độ dài thay đổi** ("Limb Length 1"..7"),
dùng để vẽ sơ đồ người que với tỉ lệ khác nhau, cộng 1 base "Combinations" và
1 base "Fingers". `BodyPose` phản ánh đúng cấu trúc thật này (xem A4 dưới),
không ép vào khuôn "18 khớp xương" không có thật.

### A2 — dữ liệu đo Category 5 (đã có sẵn từ brief, đối chiếu khớp)

Corpus SignBank+ (257.800 sign): 155.420 token Category 5, xuất hiện trong
23,3% sign. `0x36d` một mình chiếm 43,2% token; 3 base phủ 73,2%, 9 base phủ
94,2%. Valid fills/rotations lấy thẳng từ `iswa_valid_combinations.json`
(nguồn thật, font cmap ISWA) — đối chiếu khớp CHÍNH XÁC với số liệu tra được
trên signbank.org (`0x36d`: 3 fill/4 rotation cả 2 nguồn; `0x376`: 1 fill cả
2 nguồn) — không phải số tự bịa, xác nhận nguồn đáng tin.

`fill`/`rotation` của Category 5 **lệch rất mạnh**: 92,5% token là fill=0,
88,7% ở nửa rotation 0-7 — lệch hơn cả Category 1 (chia đều 6 fill) và
Category 2 (fill/rotation dù nhiễu vẫn có tín hiệu, ~60/40). Không đủ cơ sở
để đoán công thức — `BodyPose` KHÔNG biến thiên theo fill/rotation (khoá theo
`base_hex` thôi, giống `HandJointPose`), xử lý đúng như đã làm với
`hand_side` của Category 2 (để mặc định, ghi rõ chưa xác minh, không đoán).

### A4 — thiết kế `BodyPose` (sau khi có kết quả A1)

`BodyPose` (`core/body_types.py`) KHÔNG phải rig khớp-góc như `HandJointPose`
— phản ánh đúng cấu trúc "sơ đồ thân/chi" đã xác minh ở A1:
- `part: BodyPart` (`TRUNK`/`LIMB`) + `motion_type: str` — lấy **trực tiếp,
  có thể truy vết** từ tên thật đã tra (REFERENCE/POSITIONS/MOVE_WALL/
  MOVE_FLOOR/TILT_WAIST/STRETCH_WALL/BEND_WALL/TWIST_FLOOR/TILT_HIP cho
  Trunk; LENGTH/COMBINATIONS/FINGERS cho Limb).
- `limb_length_units: int | None` — lấy trực tiếp từ tên "Limb Length N"
  (N=0 cho Combinations/Fingers, không có độ dài cố định) — Limb only.
- `trunk_rotation: Rotation | None` / `shoulder_offset: NDArray | None` —
  **hằng số AUTHORED (identity/zero)** cho cả 9 base Trunk, KHÔNG có số nào
  được bịa riêng cho từng base (vd không có cơ sở nào để nói "Torso Curved
  Bend Wall" nghiêng bao nhiêu độ khác "Upper Body Tilts") — Trunk only.

`FSWBodyRenderable(get_body_pose())` — nhánh contract mới, thuần tuý thêm
vào `renderable_symbol.py`, không sửa 4 nhánh cũ (`FSWHandRenderable`/
`FSWMotionRenderable`/`FSWFaceRenderable`/`FSWHeadRenderable`).
`data/body_poses.json` sinh bằng `scripts/gen_body_poses.py`, `_meta` ghi rõ
`values_source: AUTHORED, not measured`.

### B1 — dữ liệu đo Category 3 (đã có sẵn từ brief, tên tra thêm để xác nhận)

Tra `signbank.org/iswa/2f7_sg.html` (Group 21 "Dynamics & Timing", cả 8 base
trên 1 trang): **Fast, Slow, Tense, Relaxed, Same Time, Same Time
Alternating, Every Other Time, Gradual** — khớp đúng brief.

Xác nhận đúng cấu trúc "2 mẫu" brief nêu, tra được TRỰC TIẾP từ valid
fills/rotations thật của từng base (không suy đoán):

| base | tên | biến thiên theo | %token corpus |
|---|---|---|---|
| `0x2f7` | Fast | `fill` (1-4) | 13,4% |
| `0x2f8` | Slow | `rotation` (1-8) | 4,0% |
| `0x2f9` | Tense | `fill` (1-4) | 32,3% |
| `0x2fa` | Relaxed | `fill` (1-4) | 1,3% |
| `0x2fb` | Same Time | `rotation` (1-8) | 34,6% |
| `0x2fc` | Same Time Alternating | `rotation` (1-8) | 9,5% |
| `0x2fd` | Every Other Time | `rotation` (1-8) | 4,9% |
| `0x2fe` | Gradual | `rotation` (1-8) | 0,1% |

**4 base biến thiên theo `fill` (rotation cố định 0), 4 base biến thiên theo
`rotation` (fill cố định 0) — không base nào dùng cả hai.** Ý nghĩa của biến
thiên nội-base (vd "Fast" fill 1 khác fill 4 thế nào) KHÔNG được giải mã —
`DynamicsModifier` khoá theo `base_hex` thôi, mọi (fill, rotation) hợp lệ của
1 base trả về cùng 1 `DynamicsModifier`, ghi rõ trong `_meta`.

`DynamicsModifier` (`speed`/`repeat`/`tension`/`alternating`) gán theo tên
thật: Fast/Slow → `speed` (0,7/1,4, minh hoạ, không hiệu chỉnh theo thời gian
sign thật nào); Tense/Relaxed → `tension`; Same Time / Same Time Alternating
/ Every Other Time → `alternating` (+ `repeat=2` cho "Every Other Time",
base duy nhất có ý nghĩa lặp rõ ràng từ tên); "Gradual" không khớp trọn vẹn
field nào (ý nghĩa thật là nhịp độ thay đổi DẦN TRONG lúc thực hiện sign) —
để mặc định, ghi rõ trong `_meta.unverified_assumptions`, không ép vào 1
field không đúng nghĩa.

### B3 — rủi ro kiến trúc thật: kiểu trả về của `build_symbol()`

Đúng như brief cảnh báo: `DynamicsSymbol` phải KHÔNG phải `FSWRenderableSymbol`
(brief cấm thêm `FSWDynamicsRenderable` vào cây render — 1 ký hiệu Dynamics
không render ra gì) → `build_symbol()`/`symbol_from_fsw()` không thể tiếp
tục khai kiểu trả về `FSWRenderableSymbol` khi `_CATEGORY_SYMBOL` chứa cả
`DynamicsSymbol`.

**Đã rà toàn bộ nơi gọi trước khi đổi** (`fswr_converter.py`, `timeline/
build.py`, `timeline/classify.py`, `fsw-r-viz`'s `demo.py`/`plot_hand.py`/
`plot_glyph.py`) — mọi nơi cần kiểu cụ thể hơn đều đã tự `isinstance`-narrow
trước khi gọi bất kỳ method nào chỉ có ở `FSWRenderableSymbol` trở xuống (mà
`FSWRenderableSymbol` tự nó cũng không thêm method nào so với
`FSWBaseSymbol` — nó là marker rỗng). Kết luận: nới kiểu trả về của
`build_symbol()` và `PositionedSymbol.symbol` từ `FSWRenderableSymbol` sang
`FSWBaseSymbol` là **an toàn tuyệt đối, xác minh được, không phải giả định**
— đúng hướng "ít xâm lấn" brief gợi ý, **không cần sửa `timeline/`** (xác
nhận bằng `git diff --stat` rỗng cho cả 2 commit Category 3 và Category 5).

### Giả định CHƯA kiểm chứng (Category 3 & 5)

- **Category 3**: toàn bộ giá trị `speed`/`repeat`/`tension`/`alternating`
  là AUTHORED (đọc tên, không đo) — không có dataset nào ánh xạ ký hiệu
  Dynamics sang hệ số thời gian số.
- **Category 3**: biến thiên nội-base theo fill (Fast/Tense/Relaxed, 1-4) và
  theo rotation (Slow/Same Time family/Gradual, 1-8) hoàn toàn chưa giải mã.
- **Category 3**: "Gradual" (`0x2fe`) không khớp field nào của
  `DynamicsModifier` — giữ mặc định, không đoán.
- **Category 5**: toàn bộ giá trị `BodyPose` (`trunk_rotation`,
  `shoulder_offset`, kể cả các hằng số identity/zero) là AUTHORED, không đo
  — không có dataset nào ánh xạ ký hiệu Body sang tư thế 3D.
- **Category 5**: ngữ nghĩa `fill`/`rotation` chưa xác định (92,5% fill=0,
  88,7% rotation 0-7 trong corpus — quá lệch để đoán công thức).

### Lưu ý khác biệt với acceptance criterion 2 của brief

Brief yêu cầu "1.264 test cũ pass nguyên, không sửa cái nào" — điều này
**không khả thi tuyệt đối 100%**: `tests/test_registry.py`'s
`test_build_symbol_raises_for_unsupported_category` vốn khẳng định base
`0x2f7` (Category 3) raise `ValueError` vì "category 3 chưa hỗ trợ" — 1 khi
Category 3 THẬT SỰ được hỗ trợ (đúng mục tiêu của chính task này), khẳng
định đó không còn đúng nữa theo định nghĩa, không phải do sơ suất. Test này
vốn đã đổi target 1 lần trước đó (khi Category 2 được hỗ trợ) theo đúng
comment cũ của nó — đây là lần đổi thứ 2, cùng lý do. Đã sửa để trỏ sang
`0x37f` (Category 6, Location — vẫn chưa hỗ trợ sau task này), giữ nguyên ý
nghĩa test (category chưa đăng ký → raise). **1.327/1.328 test cũ khác giữ
nguyên không sửa** — chỉ 1 test này buộc phải đổi target vì hệ quả tất yếu
của việc thêm Category 3, đã ghi rõ ở đây thay vì lặng lẽ sửa.

### Việc còn để ngỏ (Category 3 & 5, ngoài phạm vi task này theo Phần 0)

- Nối `SymbolRole.TIMING` (Category 3) vào `timeline/build.py`'s
  `DEFAULT_SIGN_DURATION` — Category 3 là category DUY NHẤT mã hoá thông
  tin thời gian mà `SignTimeline` hiện thiếu (xem `ROADMAP.md`).
- Nối `SymbolRole.ANCHOR` (Category 5) vào `timeline/anchor.py` — dùng
  `BodyPose` làm khung tham chiếu không gian thật cho vị trí tay, thay vì
  toạ độ signbox tuyến tính đơn giản hiện tại.
- `BodyPose.trunk_rotation`/`shoulder_offset` chưa có cách tính thành 1
  anchor/skeleton 3D thật trong scene — hiện chỉ là mô tả cấu trúc, giống
  `MotionPath` trước khi có `sample_trajectory()`.
- Renderer riêng cho Category 3/5 (`fsw-r-viz`) chưa làm — Category 3 không
  cần (không render gì), Category 5 cần nhưng ngoài phạm vi task này.

## Pha 5 — Tầng export sang `.pose` + video (bước 1-2)

Task riêng: biến `tuple[PoseFrame, ...]` (đã có từ Pha 3) thành **video
thật**, thay vì dừng ở tư thế tĩnh hay PNG sequence. Phạm vi cố ý hẹp — chỉ
bước 1 (forward kinematics: 15 góc khớp → 21 landmark) và bước 2 (nối
`SignTimeline` → chuỗi frame → file `.pose` → video/GIF); two-bone IK cánh
tay + thân tĩnh (bước 3) và nối Category 3 (time-warp) vào duration (bước 4)
là pha sau. **Không sửa `core/` hay `timeline/`** — gói mới `fsw_r/export/`
đặt trên, chỉ tiêu thụ đầu ra của `timeline/sample.py` (`git diff --stat`
xác nhận rỗng ở mọi commit của task này).

### Vì sao chọn `pose-format` thay vì tự viết renderer

1. `data/hand_joint_poses.json` (Category 1) vốn tính từ MediaPipe
   (`wrist → mcp → pip → dip → tip`, xem mục "Thay toàn bộ góc khớp đoán
   bằng dữ liệu thật" phía trên). `pose-format` dùng đúng topology MediaPipe
   Holistic (`pose_format.utils.holistic.HAND_POINTS`, 21 điểm/tay) — **không
   phải retarget** sang một topology khác, không mất mát ở khâu ánh xạ.
2. Không phải tự viết renderer (mesh, skinning, camera) — phần tốn công
   nhất nếu tự làm; `PoseVisualizer` có sẵn.
3. `.pose` là định dạng chung của cộng đồng sign language processing (chính
   nhóm `sign-language-processing` làm cả `pose-format` lẫn
   `3d-hands-benchmark`) → output **so sánh được** với pose trích từ video
   sign thật — điều kiện cần cho evaluation sau này.

### Kiến trúc tầng export

```
export/
  bone_lengths.py        # tỉ lệ đốt xương -- có trích nguồn
  forward_kinematics.py  # HandJointPose + wrist -> 21 landmark
  pose_export.py         # PoseFrame tuple -> pose_format.Pose (.pose)
```
`fsw-r-viz/render_pose_video.py` (package `fsw-r-viz`, không phải `fsw-r`,
vì `save_video()`/`save_gif()` cần OpenCV/PIL/ffmpeg-adjacent tooling — layer
đúng như `.pose` là data, video là visualization).

**B — Forward kinematics:** chuỗi động học tiến tích luỹ phép quay của khớp
cha (không áp góc độc lập từng khớp vào hệ toàn cục), dùng
`scipy.spatial.transform.Rotation` như phần còn lại của repo — tái hiện
đúng pattern đã CHỨNG MINH ở `fsw-r-viz/hand_geometry.py`
(`_finger_chain`/`_thumb_chain`), không import chéo (hướng dependency là
`fsw-r-viz` → `fsw-r`, không ngược lại) mà viết lại, dùng hằng số **có
nguồn** thay vì số ước lượng không trích dẫn của module cũ đó.

Tên 21 landmark lấy **trực tiếp từ thư viện**
(`pose_format.utils.holistic.HAND_POINTS`), và được parse theo TÊN (không
theo vị trí cố định trong danh sách) khi dựng dict trả về — đây là chỗ rủi
ro cao nhất brief nêu ("sai thứ tự một điểm là hỏng cả bàn tay"), xử lý sao
cho một thay đổi thứ tự `HAND_POINTS` ở phiên bản khác vẫn ra dict đúng nhãn
(chỉ việc pin phiên bản chính xác mới thật sự đổi ý nghĩa).

**Độ dài đốt xương — giả định mới, có trích nguồn:** repo trước đây KHÔNG
có dữ liệu này (`hand_joint_poses.json` chỉ có góc khớp, không có độ dài).
Trích từ Wicaksono et al., *Radiological analysis of finger length ratio and
dimensional profile of finger anatomy morphology* (Journal of Musculoskeletal
Surgery and Research, đo trên dân số Indonesia trưởng thành qua X-quang) —
độ dài đốt gần/giữa/xa của 4 ngón + đốt gần/xa của ngón cái, tính bằng mm.
Những gì KHÔNG có trong nguồn này (độ dài xương bàn tay từng ngón, độ dài
xương bàn tay ngón cái, khoảng cách ngang giữa các khớp đốt bàn ngón, góc
gắn ngón cái, hệ số mm→đơn vị body-space) đều **ước lượng riêng, ghi rõ
từng mục** trong `export/bone_lengths.py`'s docstring — không trộn lẫn số
có nguồn với số tự đoán mà không phân biệt.

**C — Xuất `.pose`:** header dùng `holistic_components()` đầy đủ 5 component
chuẩn (không cắt bớt xuống còn 2 component tay — giữ topology chuẩn để file
tương thích công cụ khác), các component chưa có dữ liệu (`POSE_LANDMARKS`,
`FACE_LANDMARKS`, `POSE_WORLD_LANDMARKS`) để confidence 0 mọi frame. **Xác
nhận, không chỉ giả định:** `NumPyPoseBody` tự MASK dữ liệu ở nơi
confidence=0 (bọc trong `numpy.ma.MaskedArray`) — thư viện tự công nhận
"confidence 0 = thiếu" ở tầng cấu trúc dữ liệu, không chỉ là quy ước.

Chỗ rủi ro cao nhất của cả task (đúng như brief cảnh báo): `pose-format`
dùng toạ độ ẢNH (x phải, **y xuống**), còn `timeline/anchor.py` đã đảo dấu y
1 lần để dùng toạ độ TOÁN (y lên) — phải đảo dấu y **lần thứ hai** lúc xuất.
Sai chỗ này thì video lộn ngược mà mọi test khác vẫn xanh (không có test nào
khác chạm vào y-ảnh) — khoá bằng test E2 riêng.

**D — Xuất video:** `render_pose_to_video()` thử `save_video()`
(cần gói `vidgear` + ffmpeg thật), bắt lỗi rộng (`except Exception`, có chủ
đích — nhiều kiểu lỗi khác nhau có thể xảy ra tuỳ môi trường thiếu gì), rồi
fallback sang `save_gif()` (chỉ cần Pillow) kèm in cảnh báo rõ ràng — **đã
thực thi thật** trên máy hiện tại (không có `vidgear`, không có ffmpeg thật),
không phải nhánh code chưa từng chạy.

### Kết quả

`demo/mvp1_sign.gif` (`fsw-r-viz`, đã commit — không phải `output/`, thư mục
đó bị gitignore) — sign MVP-1 thật (Index + Straight Wall Plane movement),
20 frame @ 512×512, xác nhận bằng mắt: bàn tay nhận ra được (đúng
handshape), dịch chuyển xuống dưới qua các frame (đúng hướng movement
symbol), không lộn ngược (xác nhận trục y đúng).

### Lỗi môi trường thật đã tìm ra và sửa (không phải lỗi của task này, nhưng bị lộ ra bởi nó)

Thêm `mediapipe`/`pose-format` vào cùng process với `fsw-r-viz/plot_glyph.py`
làm lộ 1 bug thật đã có từ trước: shim `os.register_at_fork` (viết để
`signwriting.visualizer` import được trên Windows, vốn thiếu hàm POSIX-only
này) để lại 1 no-op giả VĨNH VIỄN trên `os` sau khi dùng xong — khiến
`concurrent.futures.thread` (mà `pose_format`/`mediapipe` cần) import lỗi ở
BẤT KỲ lần import nào sau đó trong cùng process, dù bản thân
`concurrent.futures` "import được" (đã cache lỗi dở dang trong
`sys.modules`). Test nào import `fsw_r.export.pose_export` SAU khi
`plot_glyph.py` đã chạy thì lỗi; chạy riêng thì qua — phải bisect thu hẹp
xuống đúng 1 module mới tìm ra, không đoán. Sửa bằng cách giới hạn phạm vi
shim đúng 1 lần import rồi `delattr` lại — Windows thật sự không có hàm này,
trả về trạng thái đó mới là trung thực, không phải một tính năng mới.

### Ranh giới đóng góp — cần cho báo cáo/paper

> Phần của dự án: FK từ góc khớp ISWA sang 21 landmark, ánh xạ signbox 2D
> sang không gian cơ thể 3D, tầng `SignTimeline`.
> Phần dùng thư viện: định dạng `.pose` và `PoseVisualizer` của
> `pose-format 0.14.1`.

### Giả định CHƯA kiểm chứng (bổ sung ở pha này)

- Độ dài xương bàn tay từng ngón, độ dài xương bàn tay ngón cái, khoảng
  cách ngang giữa các khớp đốt bàn ngón, góc gắn ngón cái vào lòng bàn tay
  — KHÔNG có trong nguồn trích dẫn (nguồn chỉ đo độ dài đốt ngón), ước lượng
  riêng, ghi rõ trong `export/bone_lengths.py`.
- `HAND_MM_TO_BODY_UNITS` (mm thật → đơn vị body-space của `timeline/`) —
  chưa hiệu chỉnh theo tham chiếu thật nào, chọn sao cho 1 bàn tay thật cùng
  bậc độ lớn với 1 dịch chuyển trajectory điển hình.
- `BODY_UNITS_TO_PIXELS`/`FRAME_WIDTH`/`FRAME_HEIGHT` (hệ số chuẩn hoá
  signbox → pixel khi xuất `.pose`) — hằng số có tên, nhưng chưa hiệu chỉnh
  theo tham chiếu thật.
- `SIGNBOX_TO_BODY_SCALE` (kế thừa từ Pha 3, `timeline/anchor.py`) — vẫn
  chưa hiệu chỉnh, task này không đụng vào (không sửa `timeline/`).

### Vấn đề đã biết, KHÔNG xử lý trong pha này

52,1% (con số brief nêu; số tự kiểm chứng độc lập trước đó ở mục "Pha 3" là
119/261 = 45,6% với đúng phân bố theo ngón/giá trị lớn nhất — xem ghi chú ở
đó) tư thế Category 1 có ít nhất 1 góc khớp vượt giới hạn giải phẫu hợp lý
(PIP tới 167°, người gập tối đa ~110°) — **hệ quả dự kiến**: video sẽ có vài
handshape ngón cong bất thường. Đây là dự kiến, không phải lỗi tầng export —
không clamp, không tinh chỉnh `hand_joint_poses.json` trong task này (task
riêng, đã ghi ở mục "Vấn đề đã biết, CHƯA xử lý" của Pha 3).

## Pha 6 — Tầng đánh giá (FK accuracy + ràng buộc giải phẫu)

Task riêng, **task ĐO, không phải task SỬA**: framework chạy end-to-end từ
Pha 5 nhưng chưa có con số đánh giá nào — mọi thứ trước đó là *verification*
(hệ thống làm đúng thiết kế), chưa phải *evaluation* (kết quả đúng thực tế
không). Trả lời 2 câu hỏi quyết định hướng đi tiếp theo, gói mới
`fsw_r/validation/` + `scripts/fetch_ground_truth.py`/`eval_fk_accuracy.py`/
`eval_anatomical.py` — không sửa `core/`, `timeline/`, `export/`.

### Nguồn ground truth và giấy phép

- `sign-language-processing/3d-hands-benchmark` v0.10.3 (MIT) — nguồn GỐC,
  **cùng nguồn** `data/hand_joint_poses.json` đã dùng.
- `sign-language-processing/synthetic-signwriting` (MIT) — chỉ đóng gói lại
  thành `hands.npy` cho tiện, không phải dataset khác. Tải qua
  `scripts/fetch_ground_truth.py` vào `data/external/` (gitignore, không
  commit — file thật ~18MB, không phải 38MB như brief ước tính, đã xác nhận
  bằng `Content-Length` thật khi tải).
- `pose_format` (`sign-language-processing/pose`, MIT) — cho
  `PoseNormalizer` (chuẩn hoá) và `holistic_hand_component`.

### Phần B — Chuẩn hoá: 1 bug thật tìm ra và sửa

Dùng đúng cấu hình `PoseNormalizer` mà
`synthetic_signwriting/hands/hands.py` dùng (đọc trực tiếp source thật, không
suy từ brief): `plane=(WRIST, PINKY_MCP, INDEX_FINGER_MCP)`,
`line=(WRIST, MIDDLE_FINGER_MCP)`, `size=150`.

**Phát hiện thật, kiểm chứng bằng thực nghiệm, không phải giả định**:
`PoseNormalizer` của chính thư viện **KHÔNG idempotent** khi chuẩn hoá lại dữ
liệu ĐÃ chuẩn hoá — pháp tuyến của mặt phẳng có 2 hướng hợp lệ (±N), và
`get_normal()` chọn 1 hướng qua tích có hướng thô, không có quy ước dấu cố
định. Khi 3 điểm mặt phẳng đã nằm phẳng đúng z=0 (kết quả tất yếu của lần
chuẩn hoá trước), dấu tích có hướng trở thành ngẫu nhiên theo nhiễu số thực.
Kiểm chứng trên CẢ dữ liệu ground truth thật (không chỉ FK): chuẩn hoá 2 lần
lệch tới ~130 đơn vị (thang size=150) — không phải lỗi riêng của
`forward_kinematics.py`.

Hệ quả nghiêm trọng hơn cả test idempotence: **2 pose chuẩn hoá ĐỘC LẬP** (ground
truth thật vs. FK output) có thể rơi vào 2 phía đối xứng gương của sự mơ hồ
này một cách ngẫu nhiên — làm hỏng MỌI số MPJPE trước khi đo được gì. Đã sửa
bằng cách canonical hoá dấu z sau khi gọi `PoseNormalizer` (không đổi
plane/line/size — chỉ thêm bước cố định dấu, dùng z trung bình của 5 đầu
ngón làm neo — điểm xa mặt phẳng mơ hồ nên tín hiệu mạnh, không gần 0 như
chính 3 điểm mặt phẳng). Sau sửa: `normalize(normalize(x)) == normalize(x)`
đúng tới sai số làm tròn (~3e-6).

### Phần A3 — Kiểm chứng index → base_hex

`base_hex = 0x100 + hand_index`, xác nhận qua `get_hand_signwriting_symbol()`
thật trong `hands.py`. Kiểm chứng chéo với `iswa_valid_combinations.json`
(783 cặp `(base, fill)` — 261 base × 3 fill Wall Plane):

**Đính chính khung brief đưa ra**: brief nói "7/8 trùng khớp... bảng của repo
bắt thêm `0x15b`" — kiểm tra trực tiếp cho ra **7/7 khớp chính xác tuyệt đối**
với danh sách `[77, 79, 81, 92, 94, 246, 260]` hardcode trong `hands.py`
(quy ra base: `0x14d, 0x14f, 0x151, 0x15c, 0x15e, 0x1f6, 0x204`), không phải
7/8. `0x15b` THẬT SỰ có trong bảng "8 base có fill set khác chuẩn" của repo,
nhưng là loại khác hẳn: `fills=[0,1,2,3]` (fill=0 hợp lệ, chỉ thiếu 2 fill
Floor Plane 4-5) — không liên quan gì đến "fill=0 không hợp lệ" mà
`hands.py`'s danh sách đang xử lý. 2 hiện tượng khác nhau, gộp chung nhầm.

**Phát hiện thêm, `hands.py` không lọc**: ground truth của chính thư viện
tham chiếu bao gồm CẢ 3 fill Wall Plane (0,1,2) cho MỌI base, không kiểm tra
`iswa_valid_combinations.json` trước. Với 7 base ngoại lệ trên (chỉ hợp lệ ở
fill=1), điều này nghĩa là **14/783 cặp (base,fill) dùng làm ground truth
thực ra không hợp lệ theo ISWA thật**. Task này KHÔNG lọc lại (mục tiêu là so
sánh công bằng với đúng phương pháp `hands.py`), chỉ ghi nhận — xem
`reports/fk_accuracy.json`'s `index_to_base_hex_verification`.

### Câu 1 — Sai số vòng khứ hồi góc khớp (C1/C2)

Toàn bộ kết quả số trong `reports/fk_accuracy.json`/`.md` (từ chạy thật trên
`hands.npy`, không phải số minh hoạ).

| | mean | median | p75 | p95 | max |
|---|---|---|---|---|---|
| **fsw-r (261 pose/symbol)** | **48,72** | 46,49 | 50,99 | 66,19 | 193,37 |
| Baseline: 1 pose trung bình (261→1) | 64,84 | 64,03 | 72,25 | 83,31 | 181,79 |
| Baseline: 1 pose/group (261→10) | 60,44 | 59,87 | 68,10 | 81,15 | 197,18 |

(Đơn vị: khoảng cách landmark sau chuẩn hoá, thang `size=150` — quãng
wrist→middle_MCP dài đúng 150 đơn vị, dùng làm tham chiếu để đọc số.)

**261 tham số THẮNG rõ cả 2 baseline** (48,72 so với 60,44/64,84 — giảm
24-25%) — bằng chứng số cho thấy làm riêng góc khớp từng symbol có giá trị
thật, không phải 261 tham số dư thừa. Nhưng **sai số tuyệt đối vẫn đáng kể**
(~33% quãng tham chiếu 150) — không nhỏ.

MPJPE theo ngón — **ngón cái tệ hẳn** so với 4 ngón còn lại:

| Ngón | mean | median |
|---|---|---|
| **thumb** | **80,29** | 71,33 |
| pinky | 47,76 | 41,62 |
| ring | 45,58 | 39,99 |
| index | 43,21 | 36,82 |
| middle | 38,92 | 35,05 |

MPJPE theo loại khớp — CMC/IP (chỉ ngón cái) cao nhất, xác nhận thêm ngón
cái là nguồn lỗi chính, không chỉ hiệu ứng tích luỹ dọc chuỗi (TIP mới là
"tích luỹ" thật cho 4 ngón còn lại, và nó cũng cao — 70,16 — nhưng thấp hơn
IP=90,63 của ngón cái).

### Câu 1b — Kiểm chứng giả thuyết che khuất (C4)

Kỳ vọng: ring > pinky > middle > index (mức độ bị che khuất khi nắm tay).
**Thực tế đo được: pinky > ring > index > middle — KHÔNG khớp giả thuyết.**
Ghi nhận đúng như brief yêu cầu ("nếu khác, báo lại"), không ép số liệu.
Occlusion vẫn có thể là 1 phần nguyên nhân (pinky/ring đều nằm trong top 2
tệ nhất, khớp phần nào), nhưng thứ tự chính xác thì không đúng như dự đoán —
kết luận "che khuất là NGUYÊN NHÂN DUY NHẤT" không có đủ bằng chứng.

### Câu 2 — Vi phạm giới hạn giải phẫu (C3)

`fsw_r/validation/anatomical_limits.py`: giới hạn theo AAOS (American
Academy of Orthopaedic Surgeons, tài liệu goniometry lâm sàng chuẩn) cho
MCP/PIP/DIP 4 ngón + CMC/MCP/IP ngón cái — dùng đầu khoảng trên của các
nguồn khác nhau (100°/120°/90° cho MCP/PIP/DIP) làm NGƯỠNG (không phải giá
trị "trung bình" AAOS hay dùng, vì câu hỏi ở đây là "có khả dĩ không", không
phải "có phải tay trung bình không"). 2 giới hạn đánh dấu rõ là ƯỚC LƯỢNG
(không tìm được trích dẫn chắc chắn): `finger_mcp.abduction`, `thumb_mcp`'s
ngưỡng trên (biến thiên cá nhân theo 1 nghiên cứu lên tới 126°, không có số
trần rõ ràng).

Kết quả thật (`reports/anatomical.json`/`.md`):
- **224/261 (85,8%) symbol có ≥1 vi phạm flexion** — **cao hơn hẳn** số đã
  ước lượng trước đó (136/261=52,1% brief nêu; 119/261=45,6% tự kiểm chứng ở
  Pha 3 — cả 2 chỉ tính riêng PIP). Lý do khác biệt: đánh giá này kiểm TẤT CẢ
  8 khớp (không riêng PIP), và bị áp đảo bởi **CMC ngón cái (201/261 symbol
  vi phạm)** — nhiều hơn cả PIP (187).
- **⚠️ Lưu ý quan trọng về con số CMC**: giá trị `thumb.cmc.flexion` trong dữ
  liệu trải 8°-90° (median 37°), phần lớn chỉ VƯỢT NHẸ ngưỡng 30° đã chọn
  (trích từ 1 nghiên cứu: mean 22°, SD 6,8 → ~95% dữ liệu trong 8-36°) —
  KHÁC hẳn kiểu vi phạm "167° so với trần 110°" của PIP (vượt xa, rõ ràng
  bất khả). Nhiều khả năng đây là **lệch định nghĩa khớp** (góc "cmc.flexion"
  trong dữ liệu benchmark có thể đo khác quy ước lâm sàng hẹp đã trích dẫn)
  chứ không phải 77% bàn tay thật sự phi giải phẫu. Không tự sửa ngưỡng để
  "đẹp số" — ghi rõ nghi vấn này, để task sau kiểm chứng kỹ hơn.
- Riêng PIP (so sánh trực tiếp được với số liệu Pha 3): 187 lượt vi phạm góc
  (không phải số symbol) — nhất quán về hướng với phát hiện Pha 3, dù ngưỡng
  khác (120° ở đây, 110° ở Pha 3) nên không so trực tiếp 1-1 được.
- Vi phạm abduction: **0/261** — nhất quán với việc `abduction` trong
  `hand_joint_poses.json` đã biết là số CHƯA đo (ước lượng cũ, phần lớn gần
  0), không mang tín hiệu để vi phạm giới hạn 20° đã đặt.

**Tương quan vi phạm giải phẫu ↔ sai số FK (C3, yêu cầu cuối)**: Pearson
r = **0,014** (gần như 0, n=261) — **KHÔNG có tương quan đáng kể**. Giả
thuyết "2 vấn đề cùng 1 gốc (sai lệch hệ thống của MediaPipe ở ngón bị che)"
**không được số liệu ủng hộ**. Ghi nhận đúng như đo được, không ép khớp.

### Mục quyết định (E.2) — khuyến nghị dựa trên số liệu, KHÔNG tự đổi kiến trúc

**Tóm tắt bằng chứng, có phần mâu thuẫn nhau, nêu đầy đủ chứ không chọn phần
đẹp:**
- 261 tham số góc khớp thắng rõ cả 2 baseline (giảm sai số 24-25%) → có giá
  trị thật, không phải overfitting/dư thừa.
- Nhưng sai số tuyệt đối không nhỏ (~33% thang tham chiếu) → không thể nói
  "đủ tốt, không cần làm gì thêm".
- Giả thuyết "che khuất là nguyên nhân" (C4) VÀ giả thuyết "vi phạm giải
  phẫu cùng gốc với sai số FK" (C3) đều **không được số liệu xác nhận** —
  câu chuyện "MediaPipe làm sai ngón bị che, dẫn tới cả góc khớp phi giải
  phẫu lẫn FK sai" ĐẸP về mặt trực giác nhưng KHÔNG có bằng chứng thống kê
  ủng hộ ở đây.
- Ngón cái là nguồn lỗi lớn nhất, rõ rệt, nhất quán (MPJPE cao nhất theo
  ngón VÀ theo loại khớp CMC/IP) — đây là tín hiệu THỰC SỰ mạnh, không mơ hồ
  như 2 giả thuyết trên.

**Khuyến nghị**: **giữ nguyên kiến trúc góc khớp** (không chuyển sang lưu
landmark trực tiếp) — lý do:
1. Bằng chứng baseline cho thấy góc khớp per-symbol có thông tin thật, có
   giá trị đo được.
2. Ưu điểm gốc của kiến trúc góc khớp (áp được lên rig 3D bất kỳ, không
   khoá cứng vào 1 bộ landmark cụ thể) vẫn còn nguyên giá trị — vấn đề tìm
   thấy không phải "góc khớp là ý tưởng sai", mà là "hình học tái dựng
   (`export/`) và/hoặc góc ngón cái cụ thể cần soát lại".
3. Chuyển sang landmark trực tiếp sẽ không tự động sửa vấn đề chính đã tìm
   ra (ngón cái) — landmark ngón cái từ MediaPipe cũng chịu cùng độ tin cậy
   thấp do bị che khuất khi chụp, chỉ là né được việc tự làm FK, không né
   được nguồn nhiễu gốc.

**Nhưng KHÔNG khuyến nghị "coi như xong"** — việc ưu tiên trước khi đầu tư
IK cánh tay/thân người (tránh khuếch đại lỗi có sẵn, đúng lý do Phần 0 nêu
để làm task đo này trước IK):
1. Điều tra riêng ngón cái: đối chiếu định nghĩa `thumb.cmc` trong
   3d-hands-benchmark's quy trình đo với định nghĩa lâm sàng CMC flexion đã
   trích — khả năng cao đây là lệch định nghĩa, không phải lỗi đo.
2. Soát lại `export/bone_lengths.py`'s giả định hình học ngón cái
   (`_THUMB_BASE_OFFSET_MM`, `_THUMB_BASE_ROTATION` — đã tự nhận là "WEAKER"
   trong chính docstring của nó) — đây rất có thể là nguồn lỗi tái dựng
   (reconstruction), tách biệt với chất lượng dữ liệu góc khớp gốc.
3. KHÔNG dựa vào giả thuyết che khuất (C4) hay tương quan giải phẫu-FK (C3)
   để định hướng sửa lỗi — cả 2 không được số liệu xác nhận ở đây.

Không tự sửa gì trong task này (đúng ràng buộc "task ĐO, không phải task
SỬA") — mọi mục trên là khuyến nghị, đã đưa vào `ROADMAP.md`.

### Giả định CHƯA kiểm chứng (bổ sung ở pha này)

- Toàn bộ `JOINT_LIMITS` trong `anatomical_limits.py` trừ 2 mục đã đánh dấu
  `ESTIMATED_LIMITS` — có trích nguồn AAOS, nhưng là "ngưỡng khả dĩ" tự chọn
  (đầu khoảng trên các nguồn khác nhau), không phải 1 con số chuẩn hoá duy
  nhất — flag rõ trong docstring của module.
- Giới hạn hyperextension (góc âm) đặt bằng 0 cho mọi khớp — không tìm được
  nguồn cho giới hạn duỗi quá mức cụ thể, có thể ĐẾM THIẾU vi phạm theo
  hướng ngược lại.
- Nghi vấn lệch định nghĩa `thumb.cmc.flexion` giữa dữ liệu benchmark và
  ngưỡng lâm sàng đã trích (xem "Câu 2" ở trên) — chưa xác minh được, chỉ
  nêu nghi vấn có căn cứ số liệu (phân bố tập trung ngay trên ngưỡng, không
  vượt xa như PIP).

## Pha 7 — Video ra hình người ký hiệu (scale + thân tĩnh + two-bone IK)

Task riêng: video trước pha này chỉ là 1 bàn tay trôi lơ lửng, nét mảnh —
chẩn đoán đo được: **21/576 điểm có confidence > 0** (chỉ bàn tay), bàn tay
chiếm **94×183px** trong khung 512px (~36% chiều cao). Mục tiêu: ra được
**hình người ký hiệu** — có thân, vai, cánh tay nối vào bàn tay. Không sửa
`core/`, `timeline/`, `validation/`; không hiệu chỉnh hằng số hình học bàn
tay (`bone_lengths.py`, `_THUMB_BASE_ROTATION`) — việc đó dành cho task
riêng (dùng MPJPE 48,72 đã đo ở Pha 6 làm cơ sở).

### Phần A — Sửa scale (làm trước, có commit riêng)

`PoseVisualizer`'s độ dày nét chỉ phụ thuộc kích thước KHUNG HÌNH
(`round(sqrt(w*h)/150)`), không phụ thuộc kích thước chủ thể — bàn tay nhỏ
+ nét dày cố định → nhìn như que tăm. Đo trực tiếp (không đoán):
`BODY_UNITS_TO_PIXELS` cũ (150.0) cho bàn tay 94×183px; tính lại theo công
thức `150 × (0.75×512) / 183.22 ≈ 314.4`, chọn **314.0** — đo lại sau khi
sửa ra đúng **74,9%** chiều cao khung. Commit riêng, xuất 2 ảnh so sánh
(`demo/mvp1_sign_1_before_scale.gif`/`_2_after_scale.gif`) trước khi sang
Phần B, đúng yêu cầu brief.

### Phần B — Thân tĩnh + two-bone IK

**B1 — 33 điểm `POSE_LANDMARKS`**: đọc thứ tự thật từ
`pose_format.utils.holistic.holistic_components()` (không gõ tay) —
xác nhận đúng bảng chỉ số brief nêu (vai=11,12; khuỷu=13,14; cổ tay=15,16;
mặt=0,7-10; hông=23,24; pinky/index/thumb=17-22; chân=25-32). Xác nhận
`BODY_LIMBS` thật (`(15,21),(16,20),(18,20),(15,19),(16,18),(15,17),(16,22),
(13,15),(14,16),(11,13),(12,14),(11,12),(11,23),(12,24),(23,24)`) — đúng
brief cảnh báo: bỏ trống 17-22 sẽ làm đứt hình vẽ giữa cổ tay và bàn tay.

**B2 — `export/body_geometry.py`** (tư thế thân tĩnh): 4 tỉ lệ có trích
nguồn thật — Drillis & Contini (1966) "Body Segment Parameters", lấy trực
tiếp từ bản tái hiện trong Winter, D.A., *Biomechanics and Motor Control of
Human Movement*, Hình 4.1 (tải được trang thật, không suy đoán số):
shoulder width = 0,259H, hip width = 0,191H, upper arm = 0,186H, forearm =
0,146H (H = chiều cao giả định 1700mm, một số tròn phổ biến, ĐÁNH DẤU giả
định). Chiều dài thân (vai→hông) và vị trí các điểm đầu (mũi/tai/miệng)
KHÔNG lấy được từ chính nguồn này (nhãn trục dọc trong hình gốc không đọc
rõ được qua bản fetch) — tách riêng, đánh dấu ƯỚC LƯỢNG minh bạch, không
gán nhầm cho nguồn trích dẫn. **Không dùng `Category 5 BodyPose`** (đúng
ràng buộc — `body_poses.json` vẫn là placeholder rỗng, xem `_meta` của
chính file đó).

**B3 — `export/arm_ik.py`** (two-bone IK): **nghiệm đóng bằng lượng giác**
(định lý cosin + đúng 1 lần gọi `Rotation.from_rotvec()` áp góc đã biết
quanh trục đã biết) — **không** dùng `scipy.optimize` hay solver lặp, có
test riêng parse AST của module để xác nhận không import `scipy.optimize`
(không chỉ dựa vào `grep` thủ công). Pole vector (hướng khuỷu bẻ về) là
hằng số ƯỚC LƯỢNG có tên (`POLE_DIRECTION_RIGHT`/`_LEFT`, đối xứng qua trục
x) — "khuỷu hướng ra sau và xuống dưới" theo đúng brief, không có nguồn đo.
3 trường hợp biên (ngoài tầm với, quá gần, trùng vị trí) đều xử lý không
raise/NaN, có test riêng cho từng trường hợp.

**B4 — nối vào `frames_to_pose`**: landmark bàn tay tính **1 lần/track/
frame**, dùng lại cho cả component tay THẬT lẫn 6 điểm trùng lặp trong
`POSE_LANDMARKS` — đây là điều **đảm bảo** (không chỉ test) cổ tay khớp
nhau tuyệt đối giữa 2 nơi (C6), vì cùng 1 giá trị được ghi vào cả 2 chỗ.
Vai/hông tĩnh luôn được điền bất kể track nào đang hoạt động (đúng "tư thế
tĩnh"); khuỷu/cổ tay/3 điểm trùng lặp của 1 bên chỉ điền khi track bên đó
đang hoạt động.

### Phát hiện thật khi kiểm chứng bằng video thực tế (không chỉ đoán)

Sau khi lắp xong Phần B, **render thử và xem** (đúng kỷ luật "đo, không
đoán" của cả dự án) lộ ra: `BODY_UNITS_TO_PIXELS=314.0` (hiệu chỉnh riêng
cho BÀN TAY ở Phần A) làm cả người **tràn ra ngoài khung** — bounding box
thân+tay đo được `4,40 × 6,38` đơn vị body-space, ở tỉ lệ 314 thành
`1382×2003px`, phần lớn ngoài khung 512×512 (thấy rõ: hông tràn khỏi đáy
khung, bàn tay như trôi lơ lửng tách rời thân). Ban đầu (sai) giả định "vẫn
ra hình đầy đủ, hợp lý" mà KHÔNG kiểm chứng — bị chính việc render lộ ra
ngay. Sửa bằng đo lại đúng phương pháp Phần A: **68.0** đưa bounding box về
~85% chiều cao khung.

Riêng việc đổi tỉ lệ chưa đủ — vai nằm ở body-space y=0 (theo đúng hiệu
chỉnh `timeline/anchor.py`), nhưng hông cách vai xa hơn nhiều so với đầu
cách vai gần — trung điểm thật của cả hình (`-1,91`, đo trực tiếp) không
phải y=0. Thêm hằng số mới `VERTICAL_CENTER_OFFSET = -1.91` (đo được, không
đoán), trừ vào toạ độ y TRƯỚC khi nhân tỉ lệ trong `_body_to_pixel`. Sau
sửa: xác nhận bằng mắt — hình thân đầy đủ, cánh tay nối rõ vào bàn tay, dấu
"gập khuỷu xuống dưới rồi vòng lên cổ tay" khớp đúng pole vector đã đặt
(kiểm tra bằng số pixel thật, không chỉ nhìn hình), không còn phần nào bị
cắt khỏi khung.

### Kết quả

Số điểm confidence > 0: **21 → 35** cho 1 sign MVP-1 thật (1 tay — đúng
phạm vi MVP-1). Brief ước lượng "khoảng 60+" — kiểm tra bổ sung với 1
frame giả lập **2 tay** cho ra đúng **61** điểm, xác nhận số "60+" của
brief giả định 2 tay, còn MVP-1 (chỉ 1 tay theo thiết kế `timeline/
build.py`) tự nhiên thấp hơn — không phải thiếu sót, ghi rõ khác biệt thay
vì ép số cho khớp. `reports/fk_accuracy.md` xác nhận **không đổi** sau
toàn bộ pha này (chạy lại `eval_fk_accuracy.py`, diff rỗng) — đúng yêu cầu
C7, vì pha này không chạm vào FK bàn tay/dữ liệu góc khớp.

`demo/mvp1_sign_1_before_scale.gif` → `_2_after_scale.gif` → `_3_after_body.gif`
(= `mvp1_sign.gif` hiện tại): 3 file so sánh trực quan đã commit.

### Giả định CHƯA kiểm chứng (bổ sung ở pha này)

- Tỉ lệ nhân trắc học thân người: 4 tỉ lệ CÓ nguồn (Drillis & Contini
  1966, qua Winter Hình 4.1); `ASSUMED_STATURE_MM=1700` (chiều cao giả
  định) và mọi thứ tính từ đó KHÔNG có nguồn dân số cụ thể — ước lượng.
- Chiều dài thân (vai→hông), vị trí điểm đầu (mũi/tai/miệng) — ƯỚC LƯỢNG,
  không lấy được từ Drillis-Contini (nhãn trục dọc không đọc rõ qua bản
  fetch).
- Hướng pole vector của khuỷu tay (`POLE_DIRECTION_RIGHT`/`_LEFT`) — ƯỚC
  LƯỢNG, theo đúng mô tả định tính của brief ("ra sau, xuống dưới"), không
  có số đo thật.
- `BODY_UNITS_TO_PIXELS` (68.0) và `VERTICAL_CENTER_OFFSET` (-1.91) — hiệu
  chỉnh MỚI (đo trực tiếp trên 1 sign cụ thể, không phải hằng số vật lý)
  — có thể cần đo lại nếu hình dạng/tỉ lệ nhân vật thay đổi ở pha sau.
- Tư thế thân là TĨNH — chưa dùng `Category 5 BodyPose` (đang là
  placeholder rỗng, xem `_meta` của `body_poses.json`) — cố ý, ghi TODO
  cho pha sau khi có dữ liệu thật.
- Cross-check chưa đối chiếu: 0,108H (Drillis-Contini, độ dài bàn tay) =
  183,6mm ở H=1700mm, so với chuỗi ngón giữa tự tính của FK
  (`bone_lengths.py`) = 151,1mm — lệch ~18%, nhiều khả năng do
  `FINGER_METACARPAL_LENGTH_MM`'s công thức ước lượng ("1,5×PP", đã tự
  đánh dấu "WEAKER") chứ không phải tỉ lệ Drillis-Contini sai — không sửa
  trong task này (ngoài phạm vi, brief cấm hiệu chỉnh hằng số bàn tay).

## Pha 8 — Thống nhất scale bàn tay ↔ thân người

Task riêng (tiếp Pha 7): video Pha 7 đã ra hình người, nhưng **bàn tay nhỏ bất
tương xứng với thân**. Chẩn đoán gốc rễ (đo, không đoán): `bone_lengths.py`
dùng số mm rời rạc **KHÔNG neo vào chiều cao nào**, còn `body_geometry.py` suy
mọi thứ từ `ASSUMED_STATURE_MM=1700`. Hai module scale từ 2 cơ sở khác nhau →
bàn tay ~1,5× quá nhỏ so với thân (đo: palm/shoulder = 0,149 vs nhân trắc ~0,24).

### A — Neo cả hai vào MỘT chiều cao

- **`export/anthropometry.py` (module lá MỚI)**: giữ 2 hằng số cơ sở
  (`ASSUMED_STATURE_MM`, `HAND_MM_TO_BODY_UNITS`). Trước đây `ASSUMED_STATURE_MM`
  nằm ở `body_geometry.py`, `HAND_MM_TO_BODY_UNITS` ở `bone_lengths.py`, và
  `body_geometry` import từ `bone_lengths`. Neo bàn tay vào cùng stature sẽ bắt
  `bone_lengths` import ngược `body_geometry` → **vòng import**. Tách 2 hằng số
  ra module lá phá vòng: cả hai chỉ import từ module lá, không import lẫn nhau.
- **`bone_lengths.py`**: mọi độ dài giờ là `_RAW_* × _HAND_SCALE`, với
  `_HAND_SCALE` neo độ dài bàn tay duỗi vào `HAND_LENGTH_TO_STATURE ×
  ASSUMED_STATURE_MM`. **Tỉ lệ tương đối giữa các đốt/ngón KHÔNG đổi** (nhân
  đồng nhất 1 hệ số) — chỉ đổi scale tổng thể. Nguồn tỉ lệ tương đối vẫn là
  Wicaksono et al. (đã trích ở Pha 5).
- **Vì sao `HAND_LENGTH_TO_STATURE = 0,1197` chứ không phải 0,108 nhân trắc**:
  bàn tay này có palm/hand ~0,43 (không phải ~0,50 như nhân trắc), nên ở 0,108
  palm/shoulder tụt xuống ~0,18 — dưới sàn test bất biến. 0,1197 là giá trị đồng
  thời thoả cả 3 bất biến GIVEN hình dạng cố định; là hệ quả trực tiếp của lệch
  metacarpal ~0,43-vs-0,50 mà brief đặt NGOÀI phạm vi (sửa nó = đổi hình dạng
  tương đối = đổi MPJPE).

### Bug scale KHÔNG đồng đều (phát hiện thật lúc verify MPJPE, không đoán)

`_THUMB_BASE_OFFSET_MM` (điểm gắn gốc ngón cái vào lòng bàn tay) hardcode trong
`forward_kinematics.py`, **KHÔNG phải hằng số của `bone_lengths.py`** → lần đầu
KHÔNG được nhân `_HAND_SCALE`. Hậu quả: xương ngón cái phóng to 1,347× nhưng
điểm gắn giữ nguyên → **hình dạng tương đối ngón cái đổi** → chạy lại
`eval_fk_accuracy.py` ra MPJPE **48,72 → 48,74** (median 46,49 → 46,65). Đúng
loại lỗi criterion "MPJPE không được đổi" dùng để bắt (nếu chỉ đọc diff `.md`
rỗng do script bail lúc thiếu ground truth thì đã bỏ sót). Sửa: export
`HAND_SCALE` từ `bone_lengths.py`, nhân vào offset để **toàn bàn tay** (kể cả
điểm gắn ngón cái) phóng đều. Sau sửa MPJPE trở lại **48,72 chính xác** —
`reports/fk_accuracy.md` diff RỖNG.

### Bảng đo trước/sau (thật, chạy FK)

| Tỉ lệ | Trước | Sau | Cửa sổ chấp nhận | Cơ sở |
|---|---|---|---|---|
| palm / shoulder | 0,149 | 0,200 | [0,20; 0,28] | Drillis-Contini vai 0,259H |
| palm / forearm | 0,264 | 0,355 | [0,33; 0,43] | Drillis-Contini cẳng tay 0,146H |
| hand-length / stature | 0,089 | 0,120 | [0,10; 0,12] | nhân trắc học ~0,108H |

(hệ số scale ĐỒNG NHẤT = 1,347; độ dài bàn tay duỗi 151,1mm → 203,5mm)

### ⚠️ Đo "palm" bằng `MIDDLE_FINGER_MCP`, KHÔNG phải `_TIP`

Test bất biến B1/B2 đo palm = khoảng cách cổ tay → **MCP ngón giữa** (khớp
đốt bàn-ngón, đầu của bộ xương lòng bàn tay CỐ ĐỊNH), nên bất biến với việc
GẬP ngón. Nếu đo tới **TIP**, đầu ngón dịch về phía cổ tay khi ngón cong →
palm co lại theo tư thế → test sẽ đo TƯ THẾ chứ không phải giải phẫu. Có test
riêng (`test_b4_palm_length_is_invariant_to_finger_flexion`) chứng minh: gập
cả bàn tay thành nắm đấm KHÔNG đổi palm-đo-bằng-MCP. (Ngược lại, B3 đo
hand-length tới TIP là ĐÚNG, vì đo trên bàn tay DUỖI hoàn toàn, flexion=0.)

### A3 — hiệu chỉnh lại tỉ lệ pixel

Bàn tay to hơn → bounding box thân+tay cao hơn (6,38 → 7,77 đơn vị) →
`BODY_UNITS_TO_PIXELS` 68,0 → **56,0** (đưa 7,77u ≈ 85% chiều cao khung),
`VERTICAL_CENTER_OFFSET` -1,91 → **-1,21** (trung điểm bbox mới, đo trực tiếp).

### Kết quả

5 test bất biến MỚI (`tests/test_hand_body_scale.py` B1-B5) đều pass.
`reports/fk_accuracy.md` **KHÔNG đổi** (MPJPE=48,72; diff rỗng sau khi sửa bug
thumb-offset) — vì `validation/` chuẩn hoá qua `PoseNormalizer(size=150)` khử
scale tổng thể, nên scale ĐỒNG ĐỀU không đổi MPJPE (chứng minh cả toán học:
`normalize(k·X)==normalize(X)`, lẫn thực nghiệm: fetch ground truth + chạy lại
eval). GIF thứ 4 `demo/mvp1_sign_4_unified_scale.gif` đã commit (tiếp chuỗi so
sánh 3 giai đoạn). **0 file `core/`, `timeline/`, `validation/` bị sửa**
(`git diff --stat` xác nhận); mọi kích thước bàn tay VÀ thân giờ suy từ MỘT
hằng số chiều cao.

Ngoài lề (drive-by): sửa 1 lỗi mypy `[type-arg]` CÓ TỪ TRƯỚC ở
`tests/test_head_symbol.py` (`np.ndarray` thiếu tham số generic, từ commit
HeadSymbol không liên quan) để `mypy --strict` sạch hoàn toàn — thuần
annotation, không đổi runtime.

### Giả định CHƯA kiểm chứng (cập nhật ở pha này)

- `HAND_LENGTH_TO_STATURE = 0,1197`: KHÔNG phải nhân trắc 0,108 — chọn để thoả
  đồng thời 3 bất biến GIVEN hình dạng bàn tay cố định (palm ~0,43 hand). Nằm
  sát sàn B1 [0,20] và đỉnh B3 [0,12] — khít có chủ đích, là triệu chứng của
  lệch metacarpal 0,43-vs-0,50 (ngoài phạm vi, sửa sẽ đổi MPJPE).
- Lệch cross-check 18% ghi ở Pha 5 (0,108H=183,6mm vs chuỗi FK 151,1mm) giờ
  ĐÓNG một phần: bàn tay đã neo vào stature (203,5mm ở 0,1197H), nhưng lệch
  palm-proportion vẫn còn (chưa rederive metacarpal — sẽ đổi MPJPE).
- `BODY_UNITS_TO_PIXELS=56,0` / `VERTICAL_CENTER_OFFSET=-1,21` thay cho số Pha 7
  (68,0 / -1,91) — vẫn là hiệu chỉnh trên ĐÚNG 1 sign, cần đo lại nếu tỉ lệ
  nhân vật đổi ở pha sau.

## `fsw-r-viz`: visualization

- `hand_geometry.py`: forward-kinematics gần đúng (độ dài xương, vị trí gốc
  từng ngón) để dựng stick-figure từ `HandJointPose`, cộng
  `mirror_for_left_hand()` — lật trục x (không xoay) để mô phỏng việc chọn
  rig LEFT riêng biệt, vì package này không có rig/mesh thật.
- `plot_hand.py`: vẽ matplotlib 3D (`render_symbol_to_file`,
  `render_symbols_grid`), lưu PNG (headless, backend Agg).
- `demo.py`: render 2 ảnh lưới — `index_finger_rotations.png` (rotation
  sweep, fill=0 cố định, 3 RIGHT + 1 LEFT) và `index_finger_fills.png` (fill
  sweep 0-5, rotation=0 cố định, "Six Palm Facings") — xác nhận trực quan
  rotation chỉ đổi hướng ngón, fill chỉ đổi mặt bàn tay/mặt phẳng cánh tay.

## Trạng thái hiện tại

- **Category 1 (Hands) đã xong 100%: 261/261 base symbol, đủ 10/10 group —
  data-driven qua `HandSymbol` + `data/hand_joint_poses.json`, không còn
  261 class riêng (`groups/` đã xoá).**
- **`base_hex` là khoá duy nhất xuyên suốt pipeline** (không còn bị tách
  rồi dựng lại) — `registry.py` dispatch theo category (`_CATEGORY_SYMBOL`).
- **Category 2 (Movement) đã xong: đủ 242/242 base symbol**, data-driven
  qua `MovementSymbol` + `data/movement_paths.json` (sinh bằng công thức,
  không đo) — nhưng `hand_side` trả `None` (chưa chốt quy tắc thật) và
  nhiều tham số hình học vẫn là giả định chưa kiểm chứng, xem mục "Pha 2 —
  Category 2" ở trên.
- **`SignTimeline` (Pha 3, MVP-1) đã xong** — package mới `fsw_r/timeline/`,
  chỉ tiêu thụ đầu ra `core/fswr_converter.py`, **0 file `core/` bị sửa**
  (`git diff --stat` xác nhận). Phủ 6,2% sign thật (SignBank+). Chi tiết ở
  mục "Pha 3 — `SignTimeline`" phía trên.
- **Category 3 (Dynamics) và Category 5 (Trunk & Limb / Body) đã xong ở
  tầng ký hiệu: đủ 8/8 + 18/18 base symbol** — `DynamicsSymbol`/`BodySymbol`
  + `data/dynamics_modifiers.json`/`data/body_poses.json` (AUTHORED, tên
  tra thật từ signbank.org). **0 file `timeline/` bị sửa** (`git diff
  --stat` xác nhận) — cố ý, việc nối 2 category này vào `SignTimeline` là
  pha sau. Chi tiết ở mục "Pha 4 — Category 3 & 5" phía trên.
- **Tầng export `.pose` + video (Pha 5, bước 1-2) đã xong** — gói mới
  `fsw_r/export/` (`fsw-r`) + `render_pose_video.py` (`fsw-r-viz`), **0
  file `core/` hoặc `timeline/` bị sửa** (`git diff --stat` xác nhận).
  `demo/mvp1_sign.gif` đã commit — bằng chứng video thật đầu tiên của dự
  án. Chi tiết ở mục "Pha 5 — Tầng export" phía trên.
- **Tầng đánh giá (Pha 6) đã xong** — gói mới `fsw_r/validation/` +
  `scripts/fetch_ground_truth.py`/`eval_fk_accuracy.py`/`eval_anatomical.py`,
  **0 file `core/`, `timeline/`, `export/` bị sửa** (`git diff --stat` xác
  nhận). Kết quả thật đã commit ở `reports/`: MPJPE=48,72 (thang 150,
  thắng cả 2 baseline), 224/261 symbol vi phạm ≥1 giới hạn giải phẫu (đa số
  do CMC ngón cái, nghi lệch định nghĩa — xem mục "Pha 6" phía trên), giả
  thuyết che khuất (C4) và tương quan giải phẫu-FK (C3) **đều không được số
  liệu xác nhận** — ghi nhận trung thực, không ép khớp kỳ vọng. Khuyến nghị:
  giữ kiến trúc góc khớp, ưu tiên điều tra ngón cái trước khi làm IK.
- **Video ra hình người ký hiệu (Pha 7) đã xong** — bàn tay trôi lơ lửng
  trước đây giờ có thân + cánh tay two-bone IK, **0 file `core/`,
  `timeline/`, `validation/` bị sửa** (`git diff --stat` xác nhận),
  `reports/fk_accuracy.md` không đổi (chạy lại xác nhận diff rỗng). Số
  điểm confidence > 0: 21 → 35 (1 tay, đúng phạm vi MVP-1). 3 file demo so
  sánh trực quan đã commit (`mvp1_sign_1/2/3_*.gif`). Chi tiết ở mục "Pha 7"
  phía trên, gồm 1 phát hiện thật lúc kiểm chứng bằng video (không phải
  đoán): hiệu chỉnh Phần A cho riêng bàn tay không đủ cho cả người, phải đo
  và sửa lại (`BODY_UNITS_TO_PIXELS`, `VERTICAL_CENTER_OFFSET`) sau khi
  render thử.
- **Thống nhất scale bàn tay ↔ thân (Pha 8) đã xong** — bàn tay và thân giờ
  suy từ MỘT chiều cao (`export/anthropometry.py` mới phá vòng import), bàn
  tay ~1,5× to lên đúng tỉ lệ nhân trắc (palm/shoulder 0,149 → 0,200). **0
  file `core/`, `timeline/`, `validation/` bị sửa** (`git diff --stat` xác
  nhận), `reports/fk_accuracy.md` **KHÔNG đổi** (MPJPE=48,72) — sau khi bắt
  và sửa 1 bug scale không đồng đều (`_THUMB_BASE_OFFSET_MM` chưa nhân
  `HAND_SCALE`, từng làm MPJPE lệch 48,72→48,74). 5 test bất biến mới
  (`test_hand_body_scale.py`), GIF thứ 4 (`mvp1_sign_4_unified_scale.gif`)
  đã commit. Chi tiết ở mục "Pha 8" phía trên.
- **Khung hình demo dễ đọc hơn (Pha 9) đã xong** — cắt khung ở ngang hông
  (không còn hình thang đặc vai-hông-hông do `PoseVisualizer` vẽ) + thêm 6
  điểm mắt (đầu có hình dạng thật), **0 file `core/`, `timeline/`,
  `validation/` bị sửa** (`git diff --stat` xác nhận), `reports/fk_accuracy.md`
  **KHÔNG đổi**. Số điểm confidence > 0: 35 → 39. `BODY_UNITS_TO_PIXELS`
  56,0 → 94,0, `VERTICAL_CENTER_OFFSET` -1,21 → -0,22 (đo lại bounding box
  thật sau khi cắt hông). GIF thứ 5 (`mvp1_sign_5_readable_frame.gif`) đã
  commit, kèm 1 quan sát trung thực (chỗ khuỷu tay chúc xuống lộ rõ hơn do
  phóng to tỉ lệ, hình học 3D không đổi — không sửa vì ngoài phạm vi task).
  Chi tiết ở mục "Pha 9" phía trên. **Quan sát này đã được XÁC NHẬN LÀ BUG
  THẬT và SỬA ở Pha 10** (không phải chỉ "lộ rõ hơn do phóng to" như đánh
  giá ban đầu — nguyên nhân gốc là hằng số pole-vector, xem mục "Pha 10").
- **Sửa bug hướng xoay IK + chỉnh khung hình demo (Pha 10) đã xong, phần
  hiệu chỉnh elbow SAU ĐÓ PHÁT HIỆN BỊ SAI, đã sửa ở Pha 11 (xem bên
  dưới)** — vai không còn chiếm 81% chiều rộng khung (phần này ĐÚNG, vẫn
  giữ nguyên). **0 file `core/`, `timeline/`, `validation/` bị sửa**
  (`git diff --stat` xác nhận), `reports/fk_accuracy.md` **KHÔNG đổi**.
  `BODY_UNITS_TO_PIXELS` 94,0 → 69,8 (nhắm vai 60% chiều rộng khung, đo
  được — vẫn đúng). GIF thứ 6 (`mvp1_sign_6_arm_ik_fix.gif`) đã commit lúc
  đó; nhìn có vẻ cải thiện (không còn tam giác nhọn) nhưng thực ra cánh tay
  bị làm PHẲNG SAI — xem mục "Pha 11" phía trên để biết lý do và cách sửa.
- **Sửa lại bất biến IK sai — hồi quy từ Pha 10 (Pha 11) đã xong** — bất
  biến `test_c1` của Pha 10 ép khuỷu tay có CẢ cận dưới (sai giải phẫu — 1
  elbow thõng xuống dưới vai/cổ tay khi giơ tay lên là tư thế ĐÚNG, không
  phải bug), khiến Pha 10 hiệu chỉnh sai `POLE_DIRECTION_*` về Y=0. Đã bỏ
  cận dưới (chỉ giữ cận trên), trả pole về `(∓0,3, -1,0, 1,0)` (giá trị gốc
  Pha 9). `VERTICAL_CENTER_OFFSET` đo lại lần 3: 0,53 → -0,22 (quay gần về
  Pha 9). **0 file `core/`, `timeline/`, `validation/` bị sửa**,
  `reports/fk_accuracy.md` **KHÔNG đổi**. GIF thứ 7
  (`mvp1_sign_7_elbow_invariant_fix.gif`) đã commit, xem lại bằng mắt xác
  nhận cánh tay trở lại hình chữ V đúng, giữ được khung hẹp của Pha 10. Bài
  học: **1 test có thể khoá hành vi SAI** — bất biến hình học phải kiểm
  chứng với tư thế thật trước khi đưa vào test. Chi tiết ở mục "Pha 11"
  phía trên.
- `fsw-r`: `mypy --strict` **sạch hoàn toàn** (`src/`+`tests/`, 84 file — lỗi
  cũ `[type-arg]` ở `test_head_symbol.py` đã sửa drive-by ở Pha 8), `pytest`
  **1.441/1.441 pass** (1.264
  trước Pha 4 + 67 test Pha 4 + 19 test Pha 5 + 31 test Pha 6 + 21 test
  Pha 7 + 5 test Pha 8 (`test_hand_body_scale.py` B1-B5) + 5 test Pha 9
  (`test_readable_demo_frame.py` C1-C5, C6 là toàn bộ suite còn lại, không
  phải test riêng) + 29 test Pha 10 (`test_arm_configuration.py` C1-C4, C6
  tham số hoá; C5/C7 trỏ tới coverage có sẵn, không test riêng — Pha 11
  KHÔNG thêm test mới, chỉ sửa lại đúng 1 trong 29 test này):
  `test_arm_ik.py`,
  `test_body_geometry.py`, `test_body_and_arm.py`
  — đúng 2 test cũ buộc phải đổi ở Pha 8 trở về trước (1 ở Pha 4, xem mục
  đó; 1 ở Pha 7 —
  `test_non_hand_components_stay_present_at_zero_confidence` khẳng định
  `POSE_LANDMARKS` luôn confidence 0, đúng ngược lại mục tiêu chính của
  Pha 7 — tách thành 2 test, giữ nguyên phần vẫn đúng (FACE/WORLD landmarks
  vẫn rỗng) — và `test_pixel_normalization_uses_named_constants` đổi điểm
  kiểm tra theo `VERTICAL_CENTER_OFFSET` mới), cộng đúng 2 test cũ khác bị
  Pha 9 buộc phải đổi tiền đề (hông không còn confidence 1 — xem mục "Pha
  9" phía trên), cộng đúng 1 test cũ bị Pha 10 buộc phải đổi mục tiêu
  (`test_readable_demo_frame.py`'s C5 — khung hình đổi mục tiêu từ chiều
  cao 70-90% sang chiều rộng vai, xem mục "Pha 10" phía trên — Pha 11 đo
  lại con số này LẦN 3, xem mục "Pha 11").
- **Video cận cảnh bàn tay (Pha 12) đã xong** — video toàn thân không đọc
  được handshape (MCP cách nhau 8,4px, dưới độ dày nét 3px của
  `PoseVisualizer`) — thêm video THỨ HAI (`render_hand_closeup.py`, file
  mới, chỉ trong `fsw-r-viz/`), không sửa video toàn thân. Neo cổ tay,
  phóng theo kích thước RIÊNG của bàn tay (3,6×, đo được — không phải fit
  bbox quỹ đạo, chỉ 2,3×): MCP tối thiểu 8,4px → 30px, bàn tay chiếm 80%
  chiều cao khung. `HAND_CLOSEUP_THICKNESS=2` (so bằng mắt với 3). **0 file
  `fsw-r/src/fsw_r/` bị sửa** (`git diff --stat` xác nhận), video toàn
  thân (`mvp1_sign_7_elbow_invariant_fix.gif`) không đổi (`git status`
  xác nhận). GIF thứ 8 (`mvp1_sign_8_hand_closeup.gif`) đã commit, xem lại
  bằng mắt xác nhận đọc được: ngón trỏ duỗi thẳng tách biệt rõ 3 ngón còn
  lại nắm — kèm 1 quan sát trung thực (GIF chỉ 1 frame do handshape tĩnh
  suốt cả sign + Pillow tự gộp frame giống hệt nhau, không phải lỗi). Chi
  tiết ở mục "Pha 12" phía trên.
- **Chuyển động khớp ngón tay — Group 12 (Pha 13) đã xong** — trước task
  này, `joint_pose` giống hệt nhau ở MỌI keyframe của mọi sign chuyển
  động (bàn tay cứng bị kéo dọc quỹ đạo, không thấy khớp dù đã phóng to ở
  Pha 12). Sửa đúng ngữ nghĩa ISWA (Group 12 = khớp ngón cử động, cổ tay
  đứng yên — trước đó `movement_paths.py` mô hình SAI thành cả bàn tay lắc
  qua lại). Tra tên thật 5/20 base dẫn đầu (76,1% token) trên signbank.org
  TRƯỚC khi thiết kế: `0x221` Hinge Up Down Large (38,2%), `0x225` Hinge
  Alternating Large (16,0%), `0x216` Squeeze Large Single (8,9%), `0x21b`
  Flick Large Single (7,9%), `0x222` Hinge Up Down Small (5,1%) — số valid
  fills/rotations mỗi trang khớp chính xác bảng đo sẵn của brief. Kiểu mới
  `FingerArticulation` (`core/types.py`) + `data/finger_articulations.json`
  (20 entry, AUTHORED, `_meta` ghi rõ 5 base có tên thật/15 base mặc định)
  + `core/finger_articulation.py`'s `articulate_joint_pose()` (công thức
  sin, clamp bằng `JOINT_LIMITS` — dùng, không sửa `validation/`). **Được
  phép sửa `core/` và `timeline/` (task này, khác các task trước)** —
  `timeline/build.py` giờ tính lại `joint_pose` theo từng keyframe khi có
  Group 12; `sample.py` không cần sửa gì (nội suy tuyến tính có sẵn tự
  biến chuỗi keyframe dao động thành chuyển động mượt). Đo được: chênh
  lệch góc lớn nhất qua các frame vượt xa 15° cho cả 5 base dẫn đầu
  (28,3°-59,6°); clamp xác nhận hoạt động đúng trên 1 base có base data
  vốn đã vi phạm giới hạn từ Pha 6. **0 file `validation/` bị sửa**
  (`git diff --stat` xác nhận, chỉ import `JOINT_LIMITS`),
  `reports/fk_accuracy.md` **KHÔNG đổi**. GIF thứ 9
  (`mvp1_sign_9_finger_movement.gif`) đã commit — xem lại bằng mắt phát
  hiện lần xem đầu chọn nhầm frame preview (bị "phách" trùng pha), đã tự
  bắt lỗi bằng số trước khi kết luận, chọn lại đúng cặp frame thấy rõ ngón
  trỏ duỗi/nắm. Chi tiết ở mục "Pha 13" phía trên.
- **Góc nhìn 3/4 cho video cận cảnh bàn tay (Pha 14) đã xong** — GIF Pha 13
  cho thấy khớp ngón "co ngắn" thay vì "gập" vì `PoseVisualizer` chiếu
  trực giao lên XY, còn chuyển động MCP thật đo được lại chủ yếu nằm ở Y
  VÀ Z (đầu ngón giữa dịch X=0,000 Y=-0,458 Z=-0,207 giữa frame 7/13) — Z
  bị bỏ hoàn toàn khi chiếu. Thêm tham số `view_angle_deg` cho
  `render_hand_closeup.py`, xoay landmark quanh trục Y TRƯỚC bước neo/phóng
  có sẵn (đúng thứ tự yêu cầu). Đo đánh đổi thật (không suy diễn): 60°
  cho biên độ gập thấy được tăng, tách ngón MCP tối thiểu giảm còn 17,3px
  (vẫn margin so với ngưỡng 15px), 90° tụt xuống 8,2px — chọn 60°
  (`HAND_CLOSEUP_VIEW_ANGLE_DEG`). **Tự bắt 1 lỗi khi triển khai**: làm
  đúng gợi ý code của brief (mặc định tham số = 60°) làm hỏng 3 test cũ
  Pha 12 — phát hiện qua chạy test, sửa lại mặc định về 0,0 cho cả 3 hàm,
  giữ hằng số 60° dùng tường minh ở đúng 1 chỗ gọi mới. **0 file
  `fsw-r/src/fsw_r/` bị sửa** (`git diff --stat` xác nhận), `test_render_hand_closeup.py`
  (6 test Pha 12) pass y hệt không sửa gì — xác nhận 0° là no-op thật.
  2 GIF (`mvp1_sign_10_closeup_front.gif`/`_3q.gif`) đã commit, xem lại
  bằng mắt: ở 0° ngón trỏ chỉ ngắn đi, ở 60° CÙNG 2 frame cho thấy ngón
  trỏ đổi hướng rõ ràng (thẳng đứng → chéo lên-phải) — đúng là cung gập,
  không phải co ngắn. Chi tiết ở mục "Pha 14" phía trên.
- `fsw-r`: `mypy --strict` sạch (92 file), `pytest` **1.481/1.481 pass**
  (1.475 sau Pha 15 + 6 test MVP-2 ở Pha 16 `test_build.py`; 2 test MVP-1
  buộc đổi nghĩa đã cập nhật — xem Pha 16).
- **MVP-2 (sign 2 tay) đã xong (Pha 16)** — `SignTimeline` giờ dựng 1 HOẶC 2
  track tay; chuyển động gán cho tay theo **quy tắc arrowhead-fill CITED**
  (fill%3 = phải/trái/cả-hai, đối chiếu Lessons in SignWriting + Arrow
  Chooser). Coverage 6,2%→~20,9% sign. Đường 1-tay giữ nguyên byte-for-byte.
  Sửa `timeline/build.py`+`classify.py` (bản chất là feature timeline) + 1
  docstring `core/movement_symbol.py`; `hand_joint_poses.json` không đụng.
  Chi tiết ở mục "Pha 16".
- **Hoà giải thang signbox↔thân (Pha 17) đã xong** — `anchor()` từng chuẩn
  hoá signbox về ±1 trong khi thân ở ±2.2 (Pha 7/8), lệch chưa hoà giải làm
  2 tay MVP-2 đè nhau. Giờ signbox ánh xạ tới nửa-rộng-vai → 2 tay tách đúng
  theo vị trí sign đặt. **Lớp 2 (độ rõ hình dạng 2 tay ở tỷ lệ full-body)
  chưa làm** — xem Pha 17. `pytest` 1.481 (1 test anchor cập nhật giá trị).
- **Hiệu chỉnh hình học ngón cái (Pha 15) đã xong** — 2 hằng số ngón cái
  không nguồn (`_THUMB_BASE_OFFSET_MM`/`_THUMB_BASE_ROTATION`) giờ **FITTED**
  vào ground truth trên tập **held-out 70/30 phân tầng** (seed 42): test
  MPJPE **48,14 → 45,07 (6,4%, KHÔNG overfit — train cải thiện đúng 6,4%)**,
  thắng cả 2 baseline (59,07/55,67). `fk_accuracy.md` toàn-261 **48,72 →
  45,60**, thumb per-finger **80,29 → 63,93**. **0 file `core/`/`timeline/`/
  `validation/`; `hand_joint_poses.json` không đổi 1 byte.** GIF so sánh
  `mvp1_sign_11_closeup_3q.gif`. Chi tiết ở mục "Pha 15" phía trên.
- `fsw-r-viz`: `mypy --strict` sạch (4 lỗi cũ không liên quan — 2
  `FuncAnimation` type stub, 1 `ndarray` generic, xác nhận có từ trước Pha
  4/5 qua `git stash`), `pytest` **42/42 pass** (tăng từ 5/5 khi
  `fsw-r-viz` còn chỉ có Category 1 — đã qua Pha 4 (Head&Face merge, nhóm
  khác) + Pha 5 (`test_render_pose_video.py`) + Pha 12 (6 test
  `test_render_hand_closeup.py` C1-C5, C6 là toàn bộ suite) + Pha 14 (9
  test `test_hand_closeup_view_angle.py` B1-B4 + 1 test chéo-kiểm) từ lúc
  đó).
- Demo trực quan (`python -m fsw_r_viz.demo`) render đúng cả rotation lẫn
  fill: joint pose giống hệt nhau ở mọi rotation/fill/hand_side, chỉ hướng
  ngón (rotation) hoặc mặt bàn tay/mặt phẳng cánh tay (fill) thay đổi.
- `demo.py` của `fsw-r` giờ có 3 phần: rotation sweep, FSW sign string 2 tay
  (AST→FSWR), và fill sweep — đều dựng instance qua `symbol_from_fsw(...)`
  với key FSW thật, không còn gọi thẳng constructor với int tự đặt.

## Pha 9 — Khung hình demo dễ đọc hơn (cắt ngang hông + thêm mắt)

Task nhỏ, thuần thẩm mỹ cho ảnh trong báo cáo (không đổi dữ liệu, không đổi
tham số 3D, không ảnh hưởng MPJPE). Vấn đề khởi điểm: GIF demo
(`mvp1_sign_4_unified_scale.gif`) khó đọc — `PoseVisualizer` vẽ thân
(vai↔vai↔hông↔hông) thành 1 hình thang đặc chiếm ~2/3 khung hình (đúng
topology `BODY_LIMBS` thật của MediaPipe, không phải bug), trong khi bàn
tay chỉ là 1 cụm điểm nhỏ; đầu chỉ có 5 điểm (mũi, 2 tai, 2 khoé miệng) nên
trông như 2 chấm, không có hình dạng đầu thật.

**Phần A — cắt khung ở ngang hông.** Video ký hiệu thật chỉ quay nửa thân
trên — hông nằm ngoài phạm vi không gian ký hiệu mà framework này mô
hình hoá. `export/pose_export.py`'s `_pose_landmarks_for_frame()` không còn
gán `LEFT_HIP`/`RIGHT_HIP` (index 23, 24) — 2 điểm này giờ giữ confidence 0
mặc định, cùng cách xử lý với chân (25-32) và mắt trước Pha này.
**Đã xác nhận bằng cách đọc thật source `PoseVisualizer._draw_frame()`**
(không giả định): quy tắc vẽ cạnh là `sel = np.flatnonzero(vis[a] & vis[b])`
— 1 cạnh `BODY_LIMBS` chỉ được vẽ nếu CẢ 2 đầu có confidence > 0, nên bỏ
xuất hông tự động làm biến mất luôn 2 cạnh vai-hông/hông-hông (không cần
logic riêng "đừng vẽ limb này"). Đã render lại thật để xác nhận bằng mắt
(không chỉ tin vào việc đọc code) — hình thang đặc đã biến mất.
`TORSO_LENGTH_MM`/`hip_position()` trong `body_geometry.py` **vẫn giữ
nguyên định nghĩa** (chỉ không export ra `.pose` nữa) — có thể cần lại cho
Category 5 (BodyPose) sau này.

**Phần B — thêm mắt cho đầu có hình dạng.** Thêm 6 điểm
`LEFT/RIGHT_EYE_INNER/EYE/EYE_OUTER` (`POSE_LANDMARKS` index 1-6) qua hàm
mới `static_eye_landmarks()` trong `body_geometry.py`. Khác với
`NOSE_FORWARD_OFFSET_MM`/`EAR_SIDE_OFFSET_MM`/`MOUTH_DROP_MM` có sẵn (mm
phẳng, không neo theo chiều cao), **mọi offset mắt mới đều neo theo
`ASSUMED_STATURE_MM`** (`export/anthropometry.py`) — vd
`EYE_HEIGHT_ABOVE_HEAD_CENTER_MM = 0.05 * ASSUMED_STATURE_MM` — đúng yêu
cầu của task này, đồng thời lộ ra 1 điểm KHÔNG nhất quán tồn tại từ trước
(3 hằng số mũi/tai/miệng chưa neo) — ghi nhận trung thực, không sửa luôn
(ngoài phạm vi task, "không đổi tham số 3D").

**Phần C — hiệu chỉnh lại khung hình.** Đo lại bounding box thật của sign
demo chuẩn (`M508x515S10000493x485S22a04500x500`) qua TOÀN BỘ frame đã
sample (không chỉ frame 0), sau khi cắt hông: 4,40 × 4,35 đơn vị thân
(giảm mạnh so với 7,77 chiều cao khi còn hông). `BODY_UNITS_TO_PIXELS` cũ
(56,0, chỉnh cho Pha 8) giờ chỉ lấp ~48% chiều cao khung — dưới mục tiêu
70-90%. Đã đo và tính lại: **`BODY_UNITS_TO_PIXELS = 94,0`** (mục tiêu
~80%, đo thực tế ra 79,8%), **`VERTICAL_CENTER_OFFSET = -0,22`** (đổi từ
-1,21 — điểm thấp nhất trong khung giờ là bàn tay lúc di chuyển thấp nhất,
không còn là hông).

**Số điểm confidence > 0:** 35 → **39** (bỏ 2 hông, thêm 6 mắt = +4 ròng).

**Quan sát trung thực cần ghi lại (không phải bug mới, không sửa vì ngoài
phạm vi "không đổi tham số 3D" của task này):** sau khi phóng to tỉ lệ
(56→94 px/đơn vị) và bỏ "vật cản mắt" là hình thang hông, đoạn tay phải
vai→khuỷu→cổ tay giờ lộ rõ 1 chỗ khuỷu tay chúc xuống dưới đường
vai-cổ tay khá rõ — dễ thấy hơn hẳn so với các bản render trước. Đã kiểm
tra trực tiếp bằng toạ độ pixel in ra: hình học BODY-SPACE không đổi
(khuỷu tay lệch ~1,687 đơn vị thân dưới đường vai ở cả bản 68px/đơn vị cũ
lẫn bản 94px/đơn vị mới — cùng độ lớn tuyệt đối, chỉ là phóng to tỉ lệ theo
mọi thứ khác). Nguồn gốc là hằng số pole-vector có sẵn từ trước
(`POLE_DIRECTION_RIGHT`/`POLE_DIRECTION_LEFT` trong `arm_ik.py`), việc này
task hiện tại bị cấm đụng vào. Đánh giá: kết quả tổng thể vẫn là cải thiện
rõ rệt về độ dễ đọc (không còn hình thang đặc, đầu giờ có hình dạng mắt/
đầu thật) — đã quyết định commit thay vì dừng lại, nhưng ghi nhận ở đây
theo đúng tinh thần minh bạch của dự án thay vì giấu đi.

**Kiểm chứng:** `mypy --strict` sạch cả 2 package (`fsw-r`: 87 file,
`fsw-r-viz` không thêm lỗi mới); `pytest` **1.407 test cũ pass nguyên,
không sửa test nào ngoài 2 test bị chính mục tiêu task này làm sai tiền đề**
(`test_c4_shoulder_is_above_hip_in_image_space` → đổi sang so sánh
NOSE/SHOULDER thay vì SHOULDER/HIP, cùng bảo vệ lỗi lật trục y;
`test_inactive_side_arm_points_stay_zero_confidence` → bỏ HIP khỏi danh
sách "phải confidence 1") + 6 test mới (`test_readable_demo_frame.py`,
C1-C6 theo đúng brief). `git diff --stat` xác nhận 0 file `core/`,
`timeline/`, `validation/` bị sửa. `reports/fk_accuracy.md` không đổi (chạy
lại xác nhận diff rỗng — 1 lần rerun ra chênh lệch ở chữ số thập phân thứ
15-16 của `.json` do nhiễu dấu phẩy động không kết hợp giữa các lần chạy
process riêng biệt, không phải hồi quy thật; đã revert file `.json` bằng
`git checkout` thay vì commit diff giả). GIF thứ 5
(`mvp1_sign_5_readable_frame.gif`) đã render, **xem lại bằng mắt** (frame
đầu/giữa/cuối) trước khi commit, và đã commit cùng `demo/mvp1_sign.gif`
(file "mới nhất" chính tắc, xác nhận byte-for-byte giống hệt bản đánh số).

**Giả định chưa kiểm chứng mới thêm (vị trí mắt):** 5 tỉ lệ
(`EYE_HEIGHT_ABOVE_HEAD_CENTER_MM`, `EYE_INNER/CENTER/OUTER_OFFSET_MM`,
`EYE_FORWARD_OFFSET_MM`, đều là phần trăm của `ASSUMED_STATURE_MM`) là ước
lượng riêng của tác giả, KHÔNG có nguồn nhân trắc học trích dẫn được (khác
với các hằng số hình thân/tay trước đó có nguồn Drillis-Contini) — chỉ đảm
bảo đúng thứ tự hình học (mắt trên mũi, dưới đỉnh đầu, đối xứng qua trục
dọc), không đảm bảo đúng tỉ lệ giải phẫu thật.

## Pha 10 — Sửa bug hướng xoay IK + chỉnh khung hình demo

Task nhỏ, chỉ trong `export/` (không đổi dữ liệu, không ảnh hưởng MPJPE).
Vấn đề khởi điểm: GIF `mvp1_sign_5_readable_frame.gif` (Pha 9) nhìn TỆ HƠN
bản trước — một đường ngang chạy gần hết chiều rộng khung (vai chiếm 81%
chiều rộng), và một tam giác nhọn chĩa xuống dưới (khuỷu tay thấp hơn CẢ
vai lẫn cổ tay ~160px, về mặt giải phẫu là cánh tay gập ngược). Bỏ hông
(Pha 9) không tạo ra lỗi mới — nó chỉ LỘ RA 2 lỗi có sẵn từ trước (Pha 7)
mà trước đó bị hình thang hông che khuất.

**Phần A — điều tra chẩn đoán của brief trước khi sửa bất cứ gì.** Brief
giả thuyết: bước xoay `Rotation.from_rotvec(cross(aim, bend) * angle)
.apply(aim)` có bug dấu (xoay SAI HƯỚNG, ra xa `bend_direction` thay vì về
phía nó), và đề xuất công thức trực tiếp `cos(angle)*aim +
sin(angle)*bend_direction` thay thế. **Đã kiểm chứng bằng đại số (công
thức Rodrigues) VÀ bằng số (5 cặp `aim`/`bend_direction` trực giao ngẫu
nhiên) trước khi đổi bất cứ gì**: code cũ (dùng `Rotation.from_rotvec`)
**ĐÃ CHO RA ĐÚNG** kết quả `cos(angle)*aim + sin(angle)*bend_direction` —
không hề có bug dấu. Đổi sang công thức trực tiếp (bỏ phụ thuộc
`scipy.spatial.transform.Rotation` cho hàm này) nhưng đã xác nhận riêng:
thay đổi này MỘT MÌNH không đổi số nào (elbow ra y hệt trước/sau).

**Nguyên nhân THẬT** (đo bằng số trên toàn bộ 20 frame thật của sign demo
chuẩn + 4 cấu hình biên tổng hợp — cổ tay ngang vai, cao hơn, thấp hơn, và
dang xa sang ngang — không đoán): `POLE_DIRECTION_RIGHT`/`LEFT` cũ = `(∓0.3,
-1.0, 1.0)` có thành phần Y (xuống) áp đảo. `_bend_direction` tính thành
phần của pole VUÔNG GÓC với `aim` (Gram-Schmidt) — với hình học không gian
ký hiệu của project này, `aim` rất thường gần NGANG (cổ tay vươn về giữa
thân trong khi vai nằm xa ở bên hông — xem `body_geometry.shoulder_position()`),
nên phần "xuống" của pole gần như không bị loại bỏ. Cộng với góc gập lớn
(cổ tay thường gần vai hơn nhiều so với tầm với tối đa, buộc gập sâu), phần
dư "xuống" đó áp đảo `bend_direction` và kéo khuỷu tay xuống rất sâu, vượt
qua cả vai lẫn cổ tay — đúng là "tam giác nhọn chĩa xuống" trong ảnh.

**Sửa: hiệu chỉnh lại hằng số pole, đo lại chứ không đoán.**
`POLE_DIRECTION_RIGHT`/`LEFT` giờ có thành phần xuống (Y) = **0 chính xác**
— một pole vector CỐ ĐỊNH trong world-space với bất kỳ độ lệch "xuống" nào
đều không thể đồng thời thoả "khuỷu nằm giữa vai và cổ tay" cho cấu hình cổ
tay NGANG VAI (khi đó ràng buộc thu hẹp về đúng "khuỷu.y == vai.y", không
còn dư địa xuống) VÀ cho cấu hình cổ tay THẤP hơn vai (có dư địa). Đo trên
20 frame thật: độ lệch xuống dù nhỏ (Y=-0.05) đã vi phạm bất biến (margin
chỉ 0,008, gần như bằng 0); Y=0 thoả với dư địa thoải mái (margin tệ nhất
0,126/0,15). Giả định cũ "khuỷu tay hướng ra sau VÀ xuống" (ước lượng riêng
của Pha 7, chưa có nguồn nhân trắc học) hoá ra KHÔNG đúng với hình học cụ
thể của project này một khi đo thật — đã sửa lại thay vì giữ nguyên kèm
ghi chú.

**Phần B — chỉnh lại khung hình theo chiều rộng vai.** Vai đo được chiếm
81% chiều rộng khung (quá sát mép) ở `BODY_UNITS_TO_PIXELS=94,0` (Pha 9,
hiệu chỉnh theo CHIỀU CAO, chưa từng kiểm tra chiều rộng). Đo lại, nhắm
giữa khoảng mục tiêu (55-65% theo Phần B của brief, [50,70]% theo test C6):
chọn 60% → `BODY_UNITS_TO_PIXELS = 69,8` (512×0,60/4,403). Hệ quả PHỤ (không
phải mục tiêu riêng của task): việc sửa khuỷu tay ở Phần A cũng tự thu nhỏ
bounding box theo chiều cao (không còn khuỷu kéo điểm thấp nhất xuống far),
nên chiều cao đo được giảm từ 4,35 xuống 2,85 đơn vị thân — ở scale mới chỉ
còn ~39% chiều cao khung (so với mục tiêu 70-90% của Pha 9, giờ đã lỗi thời
vì mục tiêu khung hình đổi từ "chiều cao" sang "chiều rộng vai").
`VERTICAL_CENTER_OFFSET` đo lại theo bounding box mới: -0,22 → **0,53**.

**Phần C — 6 test bất biến cấu hình cánh tay mới, đúng loại test brief
trước còn thiếu.** File mới `test_arm_configuration.py`: C1 (khuỷu nằm
trong khoảng dọc vai-cổ tay, ε=0,15, 4 cấu hình × 2 bên = 8 case), C2
(khuỷu nghiêng đúng phía pole, tích vô hướng dương, 8 case), C3 (độ dài
xương giữ nguyên, 8 case), C4 (đối xứng gương 2 tay, 4 case), C5 (3 trường
hợp biên — đã có sẵn ở `test_arm_ik.py`, không nhân bản, chỉ trỏ tới), C6
(vai chiếm 50-70% chiều rộng khung). C7 là toàn bộ suite còn lại.

**1 test cũ (không phải nhiều) bị sửa vì CHÍNH MỤC TIÊU của task này đổi
nó, không phải vì test đó đang khoá hành vi sai:**
`test_readable_demo_frame.py`'s `test_c5_figure_occupies_70_to_90_percent_of_frame_height`
(Pha 9's C5) → đổi tên thành `test_c5_figure_height_stays_in_a_measured_range_after_ik_fix`,
cận mới `[0,30, 0,50]` (đo được ~38,8%) — mục tiêu khung hình của Pha 10 là
CHIỀU RỘNG VAI (test C6 mới), không phải chiều cao; chiều cao giờ chỉ là hệ
quả phụ được test lại cho có "khoá hồi quy", không còn là mục tiêu thiết
kế. Ghi chú đầy đủ lý do ngay trong comment của test.

**Kiểm chứng:** `mypy --strict` sạch (`fsw-r`: 84 file), `pytest`
**1.441/1.441 pass** (1.412 cũ + 29 test mới trong `test_arm_configuration.py`).
`git diff --stat` xác nhận 0 file `core/`, `timeline/`, `validation/` bị
sửa. `reports/fk_accuracy.md` không đổi (MPJPE=48,72, chạy lại xác nhận —
task này không đụng `bone_lengths.py`/`forward_kinematics.py`). Grep xác
nhận không có `scipy.optimize`, không vòng lặp iterative trong `arm_ik.py`.
GIF thứ 6 (`mvp1_sign_6_arm_ik_fix.gif`) đã render, **xem lại bằng mắt**
(frame đầu/giữa/cuối, so sánh trực tiếp với GIF trước-sửa) — xác nhận tam
giác nhọn chĩa xuống đã biến mất ở MỌI frame kiểm tra, thay bằng chuỗi
vai→khuỷu→cổ tay gần thẳng/dốc thoải (đúng hình dạng chấp nhận được theo
brief) — và đã commit cùng `demo/mvp1_sign.gif`.

## Pha 11 — Sửa lại bất biến IK sai (hồi quy từ Pha 10)

Task rất nhỏ, chỉ đụng `export/arm_ik.py` và `tests/test_arm_configuration.py`
(cộng 2 file phụ thuộc dây chuyền: `pose_export.py`'s hằng số căn giữa dọc,
`tests/test_readable_demo_frame.py`'s test hồi quy chiều cao). Sửa MỘT bất
biến sai đã lọt vào Pha 10, gây hồi quy hình học cánh tay.

**Vấn đề:** Pha 10 thêm test `test_c1_elbow_stays_within_the_shoulder_wrist_vertical_span`,
ép khuỷu tay nằm TRONG khoảng dọc giữa vai và cổ tay (cả cận trên LẪN cận
dưới). **Cận dưới sai về giải phẫu**: khi giơ tay lên ngang vai để ký hiệu,
khuỷu tay buông thõng xuống DƯỚI cả vai lẫn cổ tay — đó là tư thế tự nhiên
đúng (hình chữ V: vai cao → khuỷu thấp → cổ tay đưa lên), không phải gập
ngược. Để thoả cận dưới sai này, Pha 10 hiệu chỉnh `POLE_DIRECTION_RIGHT/LEFT`
về `(∓0.15, 0.0, 1.0)` (thành phần xuống = 0), làm cánh tay phẳng thành gần
như 1 đường ngang thay vì chữ V. Đo trên `M508x515S10000493x485S22a04500x500`:
khuỷu.y (pixel) từ 394 (Pha 9, đúng) tụt xuống còn 288 (Pha 10, sai) — gần
bằng vai (293) và cổ tay (289), tức cánh tay gần như thẳng.

**Sửa:**
1. **Bất biến đúng — chỉ có cận trên**: `elbow[1] <= max(shoulder[1], wrist[1]) + eps`.
   Không có cận dưới — khuỷu thõng xuống bao nhiêu là do tư thế quyết định.
   Đổi tên test thành `test_c1_elbow_never_rises_above_both_shoulder_and_wrist`,
   docstring ghi rõ VÌ SAO không có cận dưới để người sau không "sửa" ngược
   lại.
2. **Trả `POLE_DIRECTION_RIGHT/LEFT` về `(∓0.3, -1.0, 1.0)`** (giá trị gốc
   của Pha 9) — đã kiểm chứng lại (không giả định) với bất biến ĐÚNG trên cả
   4 cấu hình × 2 bên tay, 4/4 pass với dư địa thoải mái.
3. **Giữ nguyên mọi thứ khác của Pha 10**: công thức
   `cos(angle)*aim + sin(angle)*bend_direction` (đúng và ổn định hơn về số
   học, không liên quan tới bug này — đã kiểm chứng lại vẫn không phải
   nguồn lỗi), `BODY_UNITS_TO_PIXELS = 69,8` (rộng vai 60%, không phụ thuộc
   pole direction nên không cần đổi).
4. **`VERTICAL_CENTER_OFFSET` đo lại lần 3**: 0,53 (Pha 10, tạm thời) →
   **-0,22** (quay lại gần đúng giá trị Pha 9, vì bounding box body-space
   giờ gần như y hệt Pha 9 — chỉ pole direction đổi, hình học thân/đầu
   không đổi).
5. `tests/test_readable_demo_frame.py`'s test hồi quy chiều cao (không phải
   mục tiêu thiết kế, chỉ là khoá hồi quy) đo lại lần 3: chiều cao khung tăng
   trở lại từ ~39% lên ~59% (khuỷu thõng xuống hợp lệ trở lại làm bounding
   box cao hơn) — cận `[0,30, 0,50]` → **`[0,50, 0,70]`**.

**Lưu ý về số liệu pixel trong Part C1 của brief:** brief kỳ vọng khuỷu.y
(pixel) "quay về khoảng 390-400" — con số này đo ở scale Pha 9
(`BODY_UNITS_TO_PIXELS=94,0`). Task này giữ nguyên scale mới của Pha 10
(69,8, theo đúng yêu cầu "giữ nguyên phần chỉnh khung hình"), nên TOÀN BỘ
số đo pixel co lại theo tỉ lệ 69,8/94≈0,74 — khuỷu.y đo được ở scale mới là
**358** (không phải 390-400). Đã kiểm chứng bằng số: hình học BODY-SPACE
của khuỷu tay (không phụ thuộc scale) giống hệt Pha 9 (elbow_y=-1,686 đơn
vị thân ở cả 2 lần đo), và quy đổi ngược sang scale 94,0 cho ra đúng 393,8
≈ 394 — khớp hoàn toàn với brief. Tiêu chí THẬT SỰ quan trọng ("khuỷu thấp
hơn CẢ vai lẫn cổ tay") vẫn đúng ở bất kỳ scale nào (358 > 293 và 358 >
289) — ghi nhận khác biệt số liệu trung thực thay vì âm thầm đổi scale để
khớp con số cụ thể của brief (việc đó sẽ vi phạm "giữ nguyên phần chỉnh
khung hình" của Pha 10).

**Kiểm chứng:** `mypy --strict` sạch (84 file), `pytest` **1.441/1.441
pass nguyên** (không có test nào MỚI thêm — chỉ sửa lại 1 test sai của Pha
10 + đo lại 1 test hồi quy phụ thuộc). `git diff --stat` xác nhận 0 file
`core/`, `timeline/`, `validation/` bị sửa. `reports/fk_accuracy.md` không
đổi (MPJPE=48,72). GIF thứ 7 (`mvp1_sign_7_elbow_invariant_fix.gif`) đã
render, xem lại bằng mắt (frame đầu/giữa/cuối, so sánh với cả GIF Pha 9 và
Pha 10) — xác nhận cánh tay tạo hình chữ V rõ ràng (không còn đường ngang
phẳng của Pha 10), đồng thời vẫn giữ được khung hình hẹp hơn của Pha 10.

**Bài học ghi nhận (theo đúng yêu cầu brief):** **một test có thể khoá
hành vi SAI** — 1.412 test của Pha 10 (bao gồm cả 29 test mới tự thêm) đều
pass với cánh tay bị làm phẳng sai, vì bất biến TỰ NÓ sai, không phải vì
code không được test. Bất biến hình học phải được kiểm chứng với TƯ THẾ
THẬT (dáng người thật sự làm gì khi giơ tay lên) trước khi đưa vào test,
không chỉ suy luận hình học trừu tượng ("khuỷu nằm giữa 2 điểm neo có vẻ
hợp lý") — một bất biến sai, một khi đã có test khoá lại, còn NGUY HIỂM
HƠN không có test nào, vì nó tạo cảm giác an toàn giả và activelly kéo
việc hiệu chỉnh (ở đây là `POLE_DIRECTION_*`) theo hướng SAI.

## Pha 12 — Video cận cảnh bàn tay (thấy rõ khớp ngón)

Task nhỏ, chỉ trong `fsw-r-viz/` (không đụng `fsw-r/src/fsw_r/` — `git diff
--stat` xác nhận 0 file). Không đổi dữ liệu, không đổi tham số 3D, không
ảnh hưởng MPJPE.

**Vấn đề (đo trên `M508x515S10000493x485S22a04500x500`):** video toàn thân
(khung 512×512) không đọc được handshape — bàn tay chỉ chiếm 59×115px,
khoảng cách nhỏ nhất giữa 2 khớp MCP kề nhau chỉ **8,4px**, trong khi
`PoseVisualizer` vẽ nét dày `round(sqrt(512×512)/150)=3px` — 4 ngón dính
thành 1 mảng. Tăng độ phân giải khung không giải quyết được vì công thức
độ dày nét TỈ LỆ THUẬN với kích thước khung, tỉ lệ nét/khoảng-cách-ngón
không đổi. **Không sửa video toàn thân** — nó vẫn đang làm đúng việc của
nó (tư thế/quỹ đạo); thêm video THỨ HAI chuyên đọc handshape.

**Chiến lược phóng đã chọn: neo cổ tay, phóng theo kích thước RIÊNG của
bàn tay** (không phải bounding box toàn bộ quỹ đạo). Lý do: mục đích video
cận cảnh là đọc handshape, không phải xem quỹ đạo (quỹ đạo đã có ở video
toàn thân). Đo cả 2 cách trước khi chọn:

| Chiến lược | Hệ số phóng | MCP sau phóng |
|---|---|---|
| (a) Fit bbox toàn chuỗi (181px cao, do bị quỹ đạo kéo giãn) | 2,3× | 19px |
| (b) Neo cổ tay, phóng theo kích thước bàn tay (115px, không đổi mọi frame) | **3,6×** | **30px** |

Đã đo xác nhận: `HAND_CLOSEUP_TARGET_FRACTION = 0,8` (bàn tay chiếm 80%
chiều cao khung) áp cho chiều cao đo được (114,8px) ra đúng hệ số 3,57×,
khớp gần như chính xác con số 3,6× đo độc lập trước đó bằng tay — xác nhận
đây là hằng số đúng để đặt tên (không phải hệ số phóng tự nó, hệ số phóng
là ĐẠI LƯỢNG SUY RA từ hằng số này + kích thước bàn tay thực đo được, không
hardcode `3.6`). Kết quả sau phóng: MCP tối thiểu 30,0px (≥ 20px yêu cầu),
bàn tay chiếm đúng 80% chiều cao khung (trong khoảng 70-90%).

**`thickness`:** so sánh bằng mắt 2px vs 3px ở cùng mức phóng 3,6× (cả 2
đều tách bạch 4 ngón rõ ràng ở khoảng cách MCP 30px) — chọn **2px**
(`HAND_CLOSEUP_THICKNESS`) vì nét mảnh hơn phù hợp hơn với các đốt ngón
ngắn (PIP-DIP của ngón cong lại còn ngắn hơn khoảng cách MCP nhiều).

**Triển khai** (`fsw-r-viz/src/fsw_r_viz/render_hand_closeup.py`, file
mới): `hand_closeup_pose(pose, hand)` — biến đổi THUẦN DỮ LIỆU (tách riêng
khỏi phần ghi video, giống cách `frames_to_pose` tách khỏi
`render_pose_video.py`, để test được không cần vidgear/ffmpeg): ép
confidence = 0 mọi component trừ tay mục tiêu; mỗi frame neo lại theo CỔ
TAY của chính frame đó rồi nhân hệ số phóng. **Neo dọc KHÔNG cố định** — tự
tính từ khoảng trải dọc thật của bàn tay (đo qua mọi frame đang hoạt động,
không chỉ frame 0) sao cho khoảng trải đó nằm giữa khung; với handshape mà
ngón chủ yếu vươn về 1 phía so với cổ tay (trường hợp phổ biến), cách này
tự động đặt cổ tay THẤP HƠN tâm khung, đúng yêu cầu brief ("neo cổ tay ở
tâm khung, hoặc điểm thấp hơn tâm") — tính từ dữ liệu thật thay vì đoán
thêm 1 hằng số nữa. Neo ngang CỐ ĐỊNH ở giữa khung (đúng C3).
`render_hand_closeup()`/`fsw_to_hand_closeup_video()` bọc thêm phần
ghi video/GIF (cùng logic fallback với `render_pose_video.py`, không sửa
file đó).

**Quan sát trung thực (không phải bug, ghi nhận để không ai hiểu nhầm sau
này):** GIF cận cảnh của sign demo chuẩn chỉ có **1 frame** trong file dù
input có 20 frame — vì sign này giữ NGUYÊN 1 handshape suốt cả câu (chỉ cổ
tay di chuyển theo quỹ đạo), nên sau khi neo lại theo cổ tay mỗi frame,
hình bàn tay tương đối giống hệt nhau ở MỌI frame (đã kiểm chứng bằng số:
lệch ở chữ số thập phân thứ 4, nhiễu dấu phẩy động, không phải khác biệt
thật). Pillow tự động gộp các frame GIF giống hệt nhau khi ghi (xác nhận
bằng 1 test tái tạo tối giản riêng, không phải lỗi của pipeline này) — kết
quả là file GIF chỉ lưu 1 frame. Đây là hành vi ĐÚNG cho sign cụ thể này
(handshape tĩnh), không phải lỗi hiển thị.

**Xem lại bằng mắt trước khi commit:** với `S10000` (Index), thấy rõ 1
đường thẳng dài (ngón trỏ, duỗi thẳng, cao nhất trong khung) tách biệt hẳn
với 3 đường ngắn hơn (giữa/áp út/út, nắm lại) + ngón cái tách riêng sang
1 bên — đúng tiêu chí brief đề ra. **Phát hiện phụ, ghi nhận trung thực**:
với handshape này, phần "gập" (PIP→DIP→TIP) của 3 ngón cong lại xảy ra gần
như THẲNG THEO TRỤC Z (chiều sâu, hướng vào/ra khỏi camera) — nên trong
hình chiếu 2D (chỉ x,y, giống hệt cách video toàn thân chiếu) chỗ gập
KHÔNG hiện rõ thành 1 góc khuỷu nhìn thấy được, chỉ hiện ra là đoạn ngắn
hơn. Tiêu chí chính (phân biệt ngón trỏ duỗi ↔ 3 ngón còn lại nắm) vẫn đạt
— nhưng "thấy rõ CHỖ GẬP" theo đúng nghĩa đen (góc khuỷu) sẽ cần đổi góc
camera của `PoseVisualizer`, việc đó ngoài phạm vi task này.

**Kiểm chứng:** `mypy --strict` sạch (`fsw-r` không đổi gì nên vẫn 84 file
sạch; `fsw-r-viz` 29 file, không thêm lỗi mới — vẫn 4 lỗi cũ không liên
quan). `pytest` **fsw-r 1.441/1.441 pass nguyên** (0 file bị sửa nên chắc
chắn không đổi), **fsw-r-viz 33/33 pass** (27 cũ + 6 test mới
`test_render_hand_closeup.py` C1-C5, C6 là toàn bộ suite). `git diff
--stat` xác nhận 0 file trong `fsw-r/src/fsw_r/` bị sửa.
`reports/fk_accuracy.md` không đổi (hiển nhiên, vì `fsw-r` không bị đụng
tới ở bất kỳ đâu). GIF thứ 8 (`mvp1_sign_8_hand_closeup.gif`) đã commit
cùng file "mới nhất" chính tắc `mvp1_sign_hand_closeup.gif` (xác nhận
byte-for-byte giống hệt), và `mvp1_sign_7_elbow_invariant_fix.gif` (video
toàn thân) xác nhận KHÔNG đổi (`git status` không có diff trên file đó).

## Pha 13 — Chuyển động khớp ngón tay (Group 12 — Finger Movement)

Khác các task gần đây: task này **được phép sửa `core/` và `timeline/`** —
đây là tính năng thật, không phải sửa lỗi tầng ngoài. Đã dùng
`validation/anatomical_limits.py` (không sửa file đó, chỉ import
`JOINT_LIMITS`).

**Vấn đề (Phần 0):** đo trên `M508x515S10000493x485S22a04500x500`, `joint_pose`
giống hệt nhau ở cả 24 keyframe của MỌI sign chuyển động trước task này —
bàn tay là 1 hình cứng bị kéo dọc quỹ đạo. Mắt người nhận ra khớp qua
CHUYỂN ĐỘNG TƯƠNG ĐỐI giữa các đốt, không phải qua kích thước — nên dù đã
phóng to ở Pha 12, người xem vẫn không "thấy khớp". Đây đúng thiết kế
MVP-1 (không phải bug), nhưng là giới hạn cần vượt.

**Bug ngữ nghĩa phát hiện thêm:** `core/movement_paths.py` mô hình hoá
Group 12 ("Finger Movement") thành CẢ BÀN TAY lắc qua lại trong không
gian — sai theo ISWA thật: Group 12 nghĩa là CÁC KHỚP NGÓN cử động, cổ tay
đứng yên. Sửa chỗ này vừa cho ra chuyển động, vừa đúng ngữ nghĩa hơn —
không phải hack thẩm mỹ.

**Phần A1 — tên 5 base symbol dẫn đầu (76,1% token Group 12 thật), tra
TRƯỚC KHI viết code, qua `signbank.org/iswa/{hex}/{hex}_bs.html`:**

| base | tên ISWA thật | %token | valid fills/rot (đo được, khớp brief) |
|---|---|---|---|
| `0x221` | **Hinge Movement, Up Down Large** | 38,2% | 1-5 / 1-8 |
| `0x225` | **Hinge Movement, Up Down Alternating Large** | 16,0% | 1-4 / 1-8 |
| `0x216` | **Squeeze Large Single** | 8,9% | 1 / 1 |
| `0x21b` | **Flick Large Single** | 7,9% | 1 / 1 |
| `0x222` | **Hinge Movement, Up Down Small** | 5,1% | 1-5 / 1-8 |

Mỗi trang đã tự xác nhận số valid fills/rotations khớp chính xác với bảng
đo sẵn của brief (kể cả `0x221` đã có cross-check độc lập trong
`test_movement_symbol.py`'s `TOP_20_MOST_FREQUENT_BASES` từ trước) — xác
nhận đúng symbol, không nhầm hex.

**Đọc tên → thiết kế `FingerArticulation` (AUTHORED, ghi rõ trong
`data/finger_articulations.json`'s `_meta`):**
- "Hinge" = khớp gập kiểu bản lề → áp cho khớp **MCP** (khớp gốc, "hinge"
  đúng nghĩa). Tên không nêu ngón cụ thể → áp cho **cả 4 ngón không phải
  cái** (index/middle/ring/pinky) cùng lúc — lựa chọn AUTHORED, ghi rõ
  giả định "có thể ISWA thật ra phụ thuộc vào ngón nào đang duỗi trong
  handshape đi kèm, bảng này không mã hoá điều đó."
- "Large"/"Small" → 2 mức biên độ project tự đặt: 30°/15°.
- "Alternating" (chỉ `0x225`) → `phase_offset = π/2`, lệch pha các ngón
  theo thứ tự chuẩn (thumb, index, middle, ring, pinky) — tạo hiệu ứng
  "sóng lăn tăn" qua 4 ngón thay vì cùng lúc. Giá trị π/2 cụ thể là lựa
  chọn riêng, ISWA không nêu số lệch pha.
- "Squeeze" (không nói "up down") → nắm CẢ ngón lại, áp cho **MCP+PIP**
  (khác Hinge chỉ MCP), `cycles=1` ("Single" = 1 lần nắm-thả, không lặp).
- "Flick" → cử động 1 ngón, sắc gọn ở khớp xa → áp riêng cho **ngón trỏ**,
  khớp **PIP+DIP** (không phải MCP), biên độ 35° (lớn hơn Hinge/Squeeze),
  `cycles=1`.
- 15 base còn lại: **mặc định chung** (4 ngón, MCP, 20°, 2 chu kỳ,
  đồng pha) — KHÔNG tra tên riêng, ghi rõ trong `_meta`'s `default_bases`.

**Thiết kế kỹ thuật:**
- `core/types.py`: `FingerArticulation` mới (`fingers`, `joints`,
  `amplitude_deg`, `cycles`, `phase_offset`), cạnh `MotionPath`.
- `core/finger_articulation.py` mới: `articulate_joint_pose(base_pose,
  articulation, t)` — công thức `amplitude_deg * sin(2π·cycles·t + phase)`
  cộng vào flexion gốc, **clamp bằng `JOINT_LIMITS`** (dữ liệu, import từ
  `validation/`, không gọi `validate_pose()`, không sửa `validation/`).
  Ngón nào/khớp nào KHÔNG có trong `articulation.fingers`/`joints` giữ
  nguyên góc gốc.
- `core/renderable_symbol.py`: `FSWMotionRenderable` thêm abstract
  `get_finger_articulation() -> FingerArticulation | None` — bắt buộc với
  MỌI Category 2 symbol (như `get_wrist_orientation()` đã có sẵn), trả
  `None` cho 4/5 path_type còn lại. Không tạo contract riêng
  (`FSWFingerArticulationRenderable`) — `MotionPath` vẫn là mô tả bắt
  buộc duy nhất, `FingerArticulation` là chi tiết PHỤ đặc thù 1 path_type.
- `core/movement_paths.py`: `PathType.FINGER`'s `_canonical_shape()` giờ
  trả về **1 điểm cố định, giống hệt CONTACT** (cổ tay không di chuyển) —
  bỏ công thức lắc cũ. Cập nhật mục UNVERIFIED ASSUMPTIONS.
- `timeline/build.py`: khi `motion_symbol.get_finger_articulation()`
  không `None`, MỖI keyframe tính lại `joint_pose` tại đúng `time` của nó
  (thay vì dùng chung 1 `joint_pose` tĩnh) — đây là thay đổi DUY NHẤT.
  `sample.py` **không sửa gì** — phép nội suy tuyến tính có sẵn giữa các
  keyframe dày đặc (đã dùng cho CURVED/CIRCLE) tự động biến chuỗi keyframe
  dao động thành 1 chuyển động mượt khi lấy mẫu 25fps.

**Kết quả đo:**
- Chênh lệch góc lớn nhất giữa 2 frame bất kỳ, cả 5 base dẫn đầu, đều vượt
  xa 15° yêu cầu: `0x221`=56,7°, `0x225`=59,2°, `0x216`=59,6°, `0x21b`=42,8°,
  `0x222`=28,3°.
- Clamp hoạt động đúng: ví dụ `0x216` (Squeeze, áp cả MCP+PIP), ring PIP
  có base 127° (đã VI PHẠM giới hạn 120° sẵn trong `hand_joint_poses.json`
  — phát hiện cũ từ Pha 6, không phải lỗi mới) — sau dao động bị clamp
  đúng về đúng biên `[97,2, 120,0]`, không vượt 120° dù công thức chưa
  clamp cho ra tới 157°.
- Cổ tay đứng yên tuyệt đối (position giống hệt từng bit) qua mọi frame
  khi `PathType.FINGER` — xác nhận bằng số, không chỉ bằng mắt.

**Xem GIF bằng mắt trước khi commit — 1 lần chọn sai frame preview, tự bắt
lại bằng số trước khi kết luận:** lần xem đầu (frame 0/2/7 của GIF cận
cảnh) tình cờ rơi gần trùng pha (do `cycles=2` qua 20 frame lấy mẫu tạo ra
hiệu ứng "phách" — beat aliasing — với đúng khoảng cách 5 frame giữa các
lần xem), nhìn như KHÔNG có chuyển động gì. Đã KHÔNG kết luận vội — in ra
số `index.mcp` từng frame (0→47→58→57→47→30→13→2→2→13→30→...) xác nhận dao
động có thật, chọn lại đúng cặp frame 7 (duỗi, mcp≈2°) và 13 (nắm, mcp≈58°)
để xem lại — thấy rõ ngón trỏ (đường xanh dương) đổi từ dài (duỗi) sang
ngắn hẳn (nắm lại ngang 3 ngón kia) và ngược lại. GIF thứ 9
(`mvp1_sign_9_finger_movement.gif`, sign Index + `0x221`, qua pipeline
cận cảnh Pha 12) đã commit.

**Kiểm chứng:** `mypy --strict` sạch (`fsw-r` 86 file, `fsw-r-viz` không
đổi/không lỗi mới). `pytest` **fsw-r 1.475/1.475 pass** (1.441 cũ nguyên
vẹn + 34 test mới `test_finger_articulation.py` D1-D6), `fsw-r-viz`
33/33 pass. `git diff --stat` xác nhận 0 file `validation/` bị sửa (chỉ
dùng `JOINT_LIMITS`), 0 file `hand_joint_poses.json` bị đụng.
`reports/fk_accuracy.md` không đổi (MPJPE=48,72, chạy lại xác nhận — task
này không đụng FK).

**Giả định chưa kiểm chứng (bổ sung):** TOÀN BỘ giá trị `FingerArticulation`
(cả 20 base, kể cả 5 base đã tra tên thật) là AUTHORED — không có dataset
nào ánh xạ tên ISWA finger-movement sang góc khớp số. Cụ thể:
- Ngón nào tham gia cho 3 base tên không nêu ngón cụ thể (`0x221`/`0x222`/
  `0x225`) — chọn cả 4 ngón, có thể ISWA thật phụ thuộc handshape đi kèm.
- `phase_offset=π/2` cho "Alternating" — số cụ thể tự chọn, ISWA không nêu.
- "Flick" nhắm vào ngón trỏ, khớp PIP+DIP (không phải MCP) — cách hiểu
  riêng, chưa đối chiếu nguồn nào theo từng ngón.
- 2 mức biên độ (Large=30°, Small=15°) và mặc định 15 base còn lại (20°) —
  minh hoạ, chưa hiệu chỉnh theo chuyển động thật.
- 15 base không nghiên cứu riêng (`default_bases` trong `_meta`) — dùng
  chung 1 placeholder, không phải đọc tên thật của chính chúng.

## Pha 14 — Góc nhìn 3/4 cho video cận cảnh bàn tay

Task nhỏ, thuần tầng viz — **0 file `fsw-r/src/fsw_r/` bị sửa** (`git diff
--stat` xác nhận), không đổi dữ liệu, MPJPE không đổi (`fsw-r` không bị
đụng nên hiển nhiên không đổi).

**Vấn đề (Phần 0):** Pha 13 đã sinh đúng chuyển động khớp ngón (biên độ
56,6° ở MCP), nhưng xem GIF thấy ngón tay trông như CO NGẮN LẠI chứ không
phải GẬP. Đo trực tiếp độ dịch chuyển đầu ngón GIỮA (không phải trỏ) giữa
frame 7 và frame 13 của sign `M508x515S10000493x485S22100500x500`, trong
body-space (đơn vị thân, trước khi xuất pixel):

```
X = +0.000    Y = -0.458    Z = -0.207
```

Khớp lại chính xác con số brief đưa ra. Khi MCP gập, đầu ngón đi theo cung
tròn — vừa xuống (Y) vừa tới trước về phía lòng bàn tay (Z). Nhưng
`PoseVisualizer` chiếu trực giao lên mặt phẳng XY, Z chỉ dùng để quyết
định thứ tự vẽ (painter's algorithm) — hoàn toàn không ảnh hưởng vị trí.
Dữ liệu đúng, chuyển động đúng — camera nhìn thẳng vào mặt phẳng gập nên
cung tròn bị bẹp thành đường thẳng (chỉ còn thấy "ngắn đi", không thấy
"gập").

**Giải pháp:** xoay landmark bàn tay quanh trục Y một góc `view_angle_deg`
TRƯỚC bước neo cổ tay + phóng to hiện có (Pha 12) — biến 1 phần Z thành X,
cung gập hiện ra trong mặt phẳng ảnh.

**Đánh đổi đo được** (đo trực tiếp bằng implementation thật, không suy
diễn từ bảng của brief — số cụ thể khác brief 1 chút do định nghĩa metric
khác nhau, nhưng xu hướng khớp hoàn toàn: góc tăng → thấy gập rõ hơn,
tách ngón giảm):

| Góc xoay | Biên độ gập thấy được (px, đầu ngón giữa) | MCP tối thiểu (px, mọi frame) |
|---|---|---|
| 0° | 103,9 | 27,3 |
| 30° | 106,5 | 24,4 |
| 45° | 109,1 | 21,1 |
| **60°** | **111,6** | **17,3** |
| 90° | 114,0 | 8,2 |

Chọn **60°** (`HAND_CLOSEUP_VIEW_ANGLE_DEG`): vẫn còn dư địa thoải mái so
với ngưỡng 15px của B3 (17,3 > 15, margin ~15%), trong khi 90° tụt xuống
8,2px — dưới hẳn ngưỡng, các ngón sẽ chồng lên nhau không đọc được. Quyết
định này VẪN LÀ THỊ GIÁC (đã render cả 2 GIF 0°/60°, xem bằng mắt, không
chỉ đọc bảng số) — xem "Xem bằng mắt" bên dưới.

**Triển khai:** `render_hand_closeup.py`'s `hand_closeup_pose()`/
`render_hand_closeup()`/`fsw_to_hand_closeup_video()` thêm tham số
`view_angle_deg`, áp `Rotation.from_euler("y", view_angle_deg,
degrees=True)` lên toạ độ tương đối-so-với-cổ-tay TRƯỚC khi đo bounding
box/tính hệ số phóng/neo (đúng thứ tự A2 yêu cầu — xoay trước rồi mới đo,
không ngược lại).

**Sự cố tự bắt được khi triển khai (đáng ghi lại):** code mẫu trong brief
gợi ý đặt mặc định tham số là `HAND_CLOSEUP_VIEW_ANGLE_DEG` (60°) luôn.
Thử theo đúng gợi ý này thì **làm hỏng 3 test cũ của Pha 12** — các lời
gọi cũ không truyền góc (`hand_closeup_pose(pose, hand)`) bỗng ngầm nhận
60° thay vì 0°, khiến test C2 cũ (ngưỡng 20px ở 0°) đo ra 18,9px và fail.
Đã phát hiện qua chạy `pytest` (không phải đoán) — **đổi lại mặc định về
`0.0`** cho cả 3 hàm (khác gợi ý của brief), giữ `HAND_CLOSEUP_VIEW_ANGLE_DEG`
làm hằng số CÓ TÊN dùng tường minh ở đúng 1 chỗ gọi mới (video 3/4), thay
vì làm mặc định ngầm. Kết quả: mọi lời gọi cũ (kể cả test cũ, kể cả
`demo.py`'s `_render_hand_closeup_demo`/`_render_finger_movement_demo`)
giữ nguyên hành vi/byte-for-byte, đúng yêu cầu "không đổi video cận cảnh
0° hiện có" và B1.

**Xem bằng mắt trước khi commit — khác rõ giữa 2 góc:** ở 0°, đường màu
xanh dương (ngón trỏ) chỉ NGẮN ĐI giữa frame 7 (duỗi) và frame 13 (nắm) —
đọc như "co lại", không như "gập". Ở 60°, CÙNG 2 frame đó cho thấy ngón
trỏ ĐỔI HƯỚNG rõ ràng — từ gần thẳng đứng (frame 7) sang chéo lên-phải
(frame 13) — đọc đúng là 1 cung/góc gập thật, không phải co ngắn. Hai GIF
khác nhau rõ rệt, đúng tiêu chí Phần C. GIF `mvp1_sign_10_closeup_front.gif`
(0°) và `mvp1_sign_10_closeup_3q.gif` (60°) đã commit.

**Điểm đáng chú ý cho báo cáo (theo yêu cầu Phần D2):** `.pose` xuất ra từ
`fsw_r.export.pose_export` giữ ĐỦ BA CHIỀU không gian (x, y, z thật, tính
từ forward kinematics), nhưng `PoseVisualizer` — renderer chuẩn của cộng
đồng `pose-format`, công cụ project này chọn dùng vì lý do tương thích hệ
sinh thái (xem PROGRESS.md phần "vì sao chọn pose-format") — chỉ chiếu
HAI chiều lên ảnh, Z chỉ phục vụ thứ tự vẽ. Dữ liệu 3D của project này
giàu hơn thứ công cụ hiển thị tiêu chuẩn khai thác được — góc nhìn 3/4 là
cách LÀM LỘ RA sự thật đó bằng cách "mượn" 1 phần dữ liệu Z vốn đã có sẵn,
không tính toán gì mới.

**Kiểm chứng:** `mypy --strict` sạch (`fsw-r` không đổi gì nên vẫn 86
file sạch; `fsw-r-viz` 30 file, không thêm lỗi mới — vẫn 4 lỗi cũ không
liên quan). `pytest` **fsw-r-viz 42/42 pass** (33 cũ nguyên vẹn — đặc biệt
`test_render_hand_closeup.py` cả 6 test Pha 12 pass y hệt, xác nhận 0° là
no-op thật — + 9 test mới `test_hand_closeup_view_angle.py` B1-B4 và 1
test chéo-kiểm bảng đơn điệu). `fsw-r` **1.475/1.475 pass nguyên** (không
đổi gì, chắc chắn không hồi quy). `git diff --stat` xác nhận 0 file
`fsw-r/src/fsw_r/` bị sửa. `reports/fk_accuracy.md` không đổi (hiển
nhiên).

**Giả định chưa kiểm chứng:** giá trị 60° là lựa chọn thị giác (đã render
+ xem, không chỉ tính toán), không phải tối ưu toán học — brief tự nói rõ
điều này. Chưa thử cho các base Group 12 khác ngoài `0x221`, hay cho
handshape khác Index.

## Pha 15 — Hiệu chỉnh hằng số hình học ngón cái bằng ground truth (FITTED)

**Con số cải thiện ĐẦU TIÊN của dự án đo trên tập HELD-OUT.** Trước pha này
tầng đánh giá chỉ *đo* sai số (ngón cái là nguồn lỗi lớn nhất: per-finger
MPJPE 80,3 vs 39-48 các ngón khác) mà chưa *sửa*. Pha này hiệu chỉnh 2 hằng
số ngón cái **tự khai KHÔNG có nguồn** trong `export/forward_kinematics.py`
— `_THUMB_BASE_OFFSET_MM` (điểm gắn) và `_THUMB_BASE_ROTATION` (góc xoay
gốc) — bằng cách **fit vào ground truth 3d-hands-benchmark**, KHÔNG đụng
`hand_joint_poses.json` (bảng góc khớp "đo từ dataset" giữ nguyên 1 byte —
điều kiện liêm chính của paper).

### Nguồn gốc MỚI: `FITTED`

Bên cạnh `AUTHORED` / `measured` / `derived` / `cited` đã dùng trong tầng
này, 2 hằng số trên giờ mang nhãn **`FITTED`**: giá trị là *bất cứ số nào
tối thiểu hoá MPJPE chuẩn hoá trên tập fit*, không phải trích nguồn nhân
trắc cũng không phải "visually verified". Ghi rõ trong docstring của chính
2 hằng số.

### Phương pháp — BẮT BUỘC chia train/test (phần cốt lõi)

- **Chia theo `base_hex` 70/30, phân tầng theo group ISWA (1-10)**, seed
  **42** cố định. Danh sách base_hex mỗi tập ghi ở
  `reports/calibration_split.json` (train 183 / test 78, commit).
- **Tối ưu `scipy.optimize` Nelder-Mead** (đạo hàm tự do, tất định từ x0),
  1 seed, 1 khởi tạo (= giá trị cũ), KHÔNG thử nhiều seed. Hàm mục tiêu là
  MPJPE **trên tập TRAIN**.
- **Tái dùng nguyên `validation/normalization.normalize_landmarks`** (gồm
  bước canonicalize dấu z sửa bug pháp tuyến `PoseNormalizer` ở tầng đánh
  giá) — KHÔNG viết lại (ràng buộc cứng: viết lại dễ tái phát bug dấu, biến
  mọi số thành rác). Script mới `scripts/calibrate_hand_geometry.py` import
  lại `eval_fk_accuracy.py`'s ground-truth builder + `predict_landmarks`,
  không tái hiện.

### Bốn số (MPJPE chuẩn hoá, size=150)

| | train (183) | test (78, HELD-OUT) |
|---|---|---|
| **trước** | 48,97 | **48,14** |
| **sau** | 45,83 | **45,07** |

- **Số công bố được: test 48,14 → 45,07 = cải thiện 6,4%** (held-out).
- Train cũng cải thiện **đúng 6,4%** → **KHÔNG overfitting** (train/test
  cải thiện đồng đều là dấu hiệu fit tổng quát hoá, không học vẹt tập fit).
- Kiểm chứng chéo: split-weighted "trước" = (183·48,97 + 78·48,14)/261 =
  **48,72** — khớp CHÍNH XÁC `fk_accuracy.md` cũ (toàn 261), xác nhận cách
  tính MPJPE của script tái lập đúng baseline.
- Thấp hơn kỳ vọng "~16%" brief nêu — vì chỉ 4/21 landmark là ngón cái, và
  fit giảm lỗi ngón cái nhưng không về hẳn mức 45. Ghi ĐÚNG số thật, không
  ép.

### Baseline tính lại trên CÙNG tập test (dựng từ train, không rò rỉ test)

- `average_pose_baseline`: **59,07**
- `one_pose_per_group_baseline`: **55,67**

Model per-symbol (test sau = 45,07) thắng rõ cả 2 → per-symbol có giá trị
thật, không phải chỉ đoán trung bình.

### Hằng số trước/sau (FITTED)

| Hằng số | Trước (AUTHORED) | Sau (FITTED) |
|---|---|---|
| `_THUMB_BASE_OFFSET_MM` (raw ratio) | `[26, 15, 0]` | `[27.2162, 15.6248, 0.0009]` |
| `_THUMB_BASE_ROTATION` (zy deg) | `[-65, -20]` | `[-29.7002, -24.5550]` |

Offset gần như không đổi; thay đổi lớn ở **góc xoay z (-65° → -29,7°)** —
đúng "z là trục lỗi trội". Offset vẫn `× HAND_SCALE` (fit trên raw ratio)
nên vẫn neo vào cùng 1 stature như mọi kích thước khác (Pha 8).

### D — Kiểm chứng sau hiệu chỉnh

- **D1** `test_hand_body_scale.py` vẫn pass — hiệu chỉnh ngón cái KHÔNG đụng
  tỉ lệ palm/shoulder (0,201) hay /forearm (0,356) vì các tỉ lệ đó đo trên
  ngón GIỮA, không phải ngón cái.
- **D2** toàn bộ FK test cũ pass, gồm `test_e4_...[thumb]` (nắm đấm → đầu
  ngón cái gần cổ tay hơn duỗi) — không test nào khoá hằng số cũ.
- **D3** pipeline video toàn thân + cận cảnh chạy lại không lỗi.
- **D4 (bằng chứng thị giác, độc lập với MPJPE):** xuất `demo/
  mvp1_sign_11_closeup_3q.gif` (cùng sign + góc 3/4 60° như
  `mvp1_sign_10_closeup_3q.gif` đã commit, chỉ khác hằng số). Nhìn: ngón cái
  (đường đỏ) từ chỗ **vọt lên phải góc dốc** (before) hạ về **góc thoải hơn,
  sát bàn tay hơn** (after) — tự nhiên hơn cho handshape Index. **Hai bằng
  chứng ĐỒNG THUẬN** (hình tự nhiên hơn ↔ thumb MPJPE 80,3 → 63,9), không
  mâu thuẫn.
- **D5** `pytest` **1.475/1.475 pass** với hằng số mới.

### Cập nhật `reports/fk_accuracy.md` (lần đầu con số này được phép đổi)

`fk_accuracy.md` (toàn 261) tự sinh lại: **48,72 → 45,60**; thumb per-finger
**80,29 → 63,93**. ⚠️ **Lưu ý đọc số:** 45,60 là toàn 261 nhưng 183/261 nằm
trong tập fit → KHÔNG phải số tổng quát hoá sạch. **Con số trung thực để
công bố là held-out test 45,07** (ở `fk_calibration.md`), so với test-trước
48,14. 48,72-cũ và 45,60-mới đều toàn-261 nên so trực tiếp được với nhau,
nhưng chúng KHÁC bản chất với số held-out.

### Ràng buộc đã giữ

`git diff --stat`: chỉ `export/forward_kinematics.py` (2 hằng số + docstring)
bị sửa trong `src/`; **0 file `core/`, `timeline/`, `validation/`**;
`hand_joint_poses.json` **không đổi 1 byte** (đã xác nhận). Script mới +
báo cáo mới nằm ở `scripts/`, `reports/`.

## Pha 16 — MVP-2: sign 2 tay + gán chuyển động theo quy tắc CITED

Mở rộng `SignTimeline` từ MVP-1 (1 tay, 6,2% sign) sang **1 HOẶC 2 tay**
(~20,9% sign). Điểm chặn của MVP-1 là câu hỏi "chuyển động thuộc tay nào" —
`MovementSymbol.hand_side=None`, docs cũ ghi "cần đối chiếu Lessons in
SignWriting ch.6". **Đối chiếu đó giờ đã làm** (đúng lựa chọn của chủ dự án:
giải quy tắc ngôn ngữ trước khi code, không đoán).

### Quy tắc hand_side Category 2 (đã GIẢI + có trích dẫn)

SignWriting mã hoá tay thực hiện trong **kiểu đầu mũi tên (arrowhead) của
chuyển động**:
- **đầu mũi tên TỐI = tay PHẢI**, **SÁNG = tay TRÁI**, **"Superposed" = CẢ HAI**.

SignWriter Studio "Arrow Chooser" liệt kê 6 kiểu đầu mũi tên đúng thứ tự
ISWA fill: Right(0), Left(1), Superposed(2), Right-Flipped(3),
Left-Flipped(4), Superposed-Flipped(5) — "flipped" chỉ lật hình mũi tên, giữ
nguyên tay theo tên. Nên **`fill % 3`**: 0→phải, 1→trái, 2→cả-hai. Nguồn:
Sutton *Lessons in SignWriting* (dark/light = right/left); signwriting.org
Arrow Chooser (thứ tự 6 kiểu). Cài ở `timeline/classify.tracks_for_movement`.

**Giải thích "nhiễu 27%" corpus** (tay trái vẫn dùng fill=0 tới 72%): phép
đo cũ chạy trên sign **1 tay** — nơi mũi tên không cần phân biệt tay (không
có tay thứ 2), nên mặc định dùng đầu tối. Fill chỉ mang tín hiệu ở sign **2
tay** — đúng nơi `tracks_for_movement` dùng nó. Nhiễu đến từ miền 1-tay,
không phản bác quy tắc. *(Caveat trung thực: chưa đo lại riêng tập 2-tay —
cần dataset signbank-plus không có local; quy tắc dựa trên tài liệu chính
thức + đo corpus sẵn có, nhất quán 3 nguồn.)*

### Thay đổi (tối thiểu, giữ MVP-1 nguyên vẹn)

- **`timeline/classify.py`**: thêm `tracks_for_movement(movement) -> tuple[
  TrackName, ...]` (quy tắc cited ở trên). "Cả hai" trả tuple 2 track →
  KHÔNG cần thêm `HandSide.BOTH` (đúng lựa chọn của chủ dự án: áp lên cả 2
  track).
- **`timeline/build.py`**: chấp nhận 1-2 posture (2 posture phải khác side);
  route mỗi chuyển động theo quy tắc; tách helper `_build_keyframes` (dùng
  chung cho mỗi track). **Đường 1-tay giữ nguyên byte-for-byte** — fill KHÔNG
  được đọc khi chỉ 1 tay.
- **`core/movement_symbol.py`**: chỉ cập nhật docstring (ghi rõ cross-check
  đã xong, trỏ tới `tracks_for_movement`) — `hand_side` vẫn trả `None` (một
  tay đơn không phải thuộc tính của symbol đứng riêng; fill=2 là "cả hai").
  KHÔNG đổi hành vi.
- **Downstream đã sẵn**: `sample.py` + `export/pose_export.py` vốn đã duyệt
  mọi track (track thiếu → confidence 0), nên không phải sửa.

### Phạm vi CÒN ngoài MVP-2 (vẫn raise, có chủ đích)

- 2 posture **cùng side** ("một tay, hai tư thế") — mơ hồ chưa giải.
- **>1 chuyển động trên CÙNG một tay** ("một tay, hai thời điểm" vs chuỗi) —
  đúng thứ MVP-1 né; giữ tính xác định.
- >2 tay, hay category khác 1/2.

### Kiểm chứng

- `pytest` **1.481/1.481** (1.475 cũ + 6 test MVP-2; **2 test MVP-1 buộc đổi
  nghĩa** đã cập nhật: sign RIGHT+LEFT trước đây raise "exactly 1 hand" nay
  dựng 2 track; message 0-tay đổi "exactly 1 hand"→"1 or 2 hand"). Test mới:
  fill 0→phải / 1→trái / 2→cả-hai, reject 2 cùng-side, reject 2 chuyển
  động/tay, end-to-end 2 tay qua `sample()`.
- `mypy --strict` sạch. **Kiểm chứng trực quan**: render 1 sign 2 tay qua
  `export` → cả 2 tay + 2 cánh tay hiện ra đúng (độ rõ khi 2 tay gần nhau là
  việc render, cùng loại đã xử lý cho 1 tay ở Pha 9-14).
- Đường 1-tay: mọi test MVP-1 tĩnh/động/real-sign pass nguyên.

**Lưu ý ràng buộc:** khác 2 task trước (cấm đụng `timeline/`), MVP-2 **bản
chất là feature của `timeline/`** nên có sửa `timeline/build.py` +
`classify.py` (thêm hỗ trợ, không phá MVP-1) và 1 docstring ở
`core/movement_symbol.py`. `hand_joint_poses.json` không đụng.

## Pha 17 — Hoà giải thang signbox↔thân người (lớp 1 của "2 tay đè nhau")

**Phát hiện khi xem video MVP-2:** 2 tay bị đè lên nhau. Chẩn đoán (đo, không
đoán): `anchor()` chuẩn hoá signbox về **±1**, trong khi thân người (từ Pha
7/8, suy từ `ASSUMED_STATURE_MM`) có vai ở **±2.2** — **hai thang độc lập,
chưa bao giờ hoà giải**, lệch ~2.2×. Đo trực tiếp: 2 cổ tay ở body-x ±0.16
(cách 0.32) trong khi 2 vai cách 4.4 → tay nén về hộp trung tâm bé, cánh tay
với chéo từ vai rộng vào cổ tay giữa. **MVP-1 (1 tay ở giữa) giấu được; MVP-2
(2 tay) phơi ra.**

### Sửa (lớp 1 — định vị)

`anchor()` giờ nhân toạ độ chuẩn hoá với `SIGNBOX_BODY_HALF_EXTENT = 2.20` =
**nửa-rộng-vai** (`SHOULDER_WIDTH_MM × HAND_MM_TO_BODY_UNITS / 2`, từ
`body_geometry`) — nên cạnh signbox ánh xạ tới đường vai, và **2 tay đặt xa
nhau trong sign giờ render tách biệt**. Isotropic (cùng scale u/v, giữ tỉ lệ
sign). Giữ là **hằng số có comment** (không import `body_geometry`) để
`timeline/` tự-chứa — `export/` tiêu thụ `timeline/`, không ngược lại; theo
đúng tiền lệ `pose_export.BODY_UNITS_TO_PIXELS` (hằng số hiệu chỉnh, verify
bằng render). Nếu thang thân đổi thì re-derive.

Thang chuyển động (`SIGNBOX_TO_BODY_SCALE=0.1`) giữ nguyên, tách riêng làm
**cỡ cử chỉ CỤC BỘ** (một wiggle quanh vị trí tay, không phải dịch chuyển cả
signbox) — cập nhật docstring cho rõ.

### Kiểm chứng

- Render sign 2 tay đặt xa (signbox 380/620): **thấy rõ 2 bàn tay tách biệt**
  (trước: xúm vào tâm). Đo: cổ tay ±0.35 (sign sát) → ±1.06 (sign xa), tách
  đúng theo vị trí sign đặt. Không clip khung (bounding box vẫn do thân
  ±2.2/hông/torso chi phối).
- `pytest` **1.481/1.481** (chỉ `test_anchor_normalization` cập nhật giá trị
  →`SIGNBOX_BODY_HALF_EXTENT`; 2 test anchor còn lại là quan hệ, bền; mọi
  test MVP-1/MVP-2/pixel khác pass nguyên — không có test nào khoá vị trí
  tuyệt đối khác). `mypy --strict` sạch.

### CÒN LẠI — lớp 2 (độ RÕ hình dạng), CHƯA làm

Đây mới sửa **định vị** (hết đè khi sign đặt tay xa). Phần "chưa rõ hình dạng
gì" vẫn còn: ở tỷ lệ full-body mỗi bàn tay nhỏ + nét vẽ dày cố định → nhoè
vào nét thân. Đúng vấn đề Pha 12/14 đã giải cho **1 tay** (close-up crop+phóng
to) nhưng chưa có cho **2 tay**. Hướng: close-up khung cả 2 tay, hoặc nét mảnh
hơn/phóng to vùng tay. Xem ROADMAP.md.

## Việc còn để ngỏ / chưa làm

- **Category 1 (Hands), 2 (Movement), 3 (Dynamics), 5 (Trunk & Limb / Body)
  đã xong ở tầng ký hiệu: 261/261 + 242/242 + 8/8 + 18/18 base symbol.**
  Category 4 (Head & Face) cũng đã xong (~110 base, nhóm khác trong dự án
  phụ trách, không phải mục này). **Chỉ còn Category 6 (Location, 8 base)
  và Category 7 (Punctuation, 5 base) chưa làm** — tổng 7 category ISWA
  (Trunk và Limb là 1 category chung, không phải 2 — xem `ROADMAP.md` mục
  "Các category ISWA").
- **Category 3/5 mới chỉ xong tầng ký hiệu, CHƯA nối vào `SignTimeline`**
  (cố ý, ngoài phạm vi task đó — xem mục "Pha 4 — Category 3 & 5" phía trên
  và `ROADMAP.md`'s "Việc còn lại"). Cụ thể: `DEFAULT_SIGN_DURATION` vẫn là
  hằng số giữ chỗ (chưa dùng `DynamicsModifier.speed`), và toạ độ signbox
  vẫn ánh xạ tuyến tính đơn giản (chưa dùng `BodyPose` làm khung tham chiếu).
- **Tầng export `.pose`/video: bước 1-2 (Pha 5) VÀ scale+thân tĩnh+IK
  (Pha 7) đã xong — chỉ còn bước 3-4 thật sự** (nối Category 3 vào duration,
  xem mục "Pha 5 — Tầng export" và "Pha 7" phía trên và `ROADMAP.md`). Cụ
  thể còn thiếu:
  - `DynamicsModifier.speed` chưa nối vào frame count/fps của video xuất ra
    — mọi video vẫn dùng `DEFAULT_SIGN_DURATION` cố định.
  - `Category 5 BodyPose` chưa nối vào tư thế thân (đang TĨNH, dùng
    `body_geometry.py`'s hằng số riêng) — cố ý, `body_poses.json` vẫn là
    placeholder rỗng (xem `_meta` của chính file đó).
  - Độ dài xương (`export/bone_lengths.py`) chỉ có nguồn cho đốt ngón; độ
    dài xương bàn tay, khoảng cách khớp đốt bàn ngón, góc gắn ngón cái đều
    là ước lượng riêng — xem "giả định chưa kiểm chứng" ở mục "Pha 5".
  - `save_video()` (MP4 thật) chưa từng chạy thành công trên máy hiện tại
    (thiếu `vidgear` + ffmpeg thật) — mọi bằng chứng video hiện tại là GIF
    fallback, không phải MP4.
  - `BODY_UNITS_TO_PIXELS`/`VERTICAL_CENTER_OFFSET` (Pha 7, hiệu chỉnh lại
    ở Pha 9 sau khi cắt hông: 56,0→94,0 / -1,21→-0,22, rồi lại ở Pha 10 sau
    khi đổi mục tiêu sang chiều rộng vai: 94,0→69,8 / -0,22→0,53 — vế
    `VERTICAL_CENTER_OFFSET` của Pha 10 dựa trên hiệu chỉnh elbow SAI, đã
    trả lại -0,22 ở Pha 11 sau khi bất biến elbow được sửa; `BODY_UNITS_TO_PIXELS`
    giữ nguyên 69,8 vì không phụ thuộc pole direction) hiệu chỉnh trên ĐÚNG
    1 sign cụ thể — có thể cần đo lại nếu hình dạng nhân vật (tỉ lệ thân,
    tầm với cánh tay) thay đổi ở pha sau.
  - **Vị trí 6 điểm mắt (Pha 9)** là ước lượng riêng, KHÔNG có nguồn nhân
    trắc học trích dẫn được (khác các hằng số thân/tay khác đã có nguồn
    Drillis-Contini) — chỉ đảm bảo đúng thứ tự hình học, không đảm bảo tỉ
    lệ giải phẫu thật. `NOSE_FORWARD_OFFSET_MM`/`EAR_SIDE_OFFSET_MM`/
    `MOUTH_DROP_MM` (từ trước Pha 9) vẫn là mm phẳng, chưa neo theo
    `ASSUMED_STATURE_MM` như các hằng số mắt mới — điểm không nhất quán đã
    ghi nhận, chưa sửa (ngoài phạm vi Pha 9/10).
  - ~~Ảnh demo (Pha 9) lộ rõ hơn 1 artifact hình học~~ — Pha 10 sửa NHẦM
    (kết luận "bug ở hằng số pole" đúng một nửa, nhưng cách sửa — ép Y=0 —
    lại dựa trên 1 bất biến test sai, làm cánh tay phẳng ra thay vì đúng
    hình chữ V). **ĐÃ SỬA LẠI ĐÚNG ở Pha 11**: bất biến chỉ còn cận trên,
    `POLE_DIRECTION_RIGHT`/`_LEFT` trả về `(∓0,3, -1,0, 1,0)` (giá trị gốc
    Pha 9) — xem mục "Pha 11" phía trên. Bài học tự ghi nhận (2 lớp): (1)
    Pha 9 đánh giá sai mức độ nghiêm trọng ban đầu (coi "artifact nhỏ" thay
    vì "bug thật"); (2) Pha 10 sửa đúng HƯỚNG (nghi ngờ hằng số pole) nhưng
    tự thêm 1 bất biến SAI để xác nhận, rồi tin vào bất biến sai đó hơn là
    xác minh lại bằng tư thế giải phẫu thật — xem `ROADMAP.md`'s ghi chú
    bài học tương ứng cho cả 2 lớp này.
  - **Category 4 (Head & Face) chưa nối vào đầu người trong video** — đầu
    hiện chỉ có mũi/tai/miệng/mắt tĩnh (`body_geometry.py`), chưa dùng
    `FACE_LANDMARKS` thật (468 điểm MediaPipe) hay `FaceExpressionPose`
    (đã có ở Category 4, nhóm khác phụ trách) — việc map 468 điểm mesh mặt
    từ blend-shape sang toạ độ tĩnh là việc mới, không nhỏ, chưa bắt đầu.
  - ~~**Chỉ có 1 tay (phải), chưa có tay trái** — MVP-2~~ **ĐÃ XONG (Pha
    16):** `SignTimeline` dựng 1-2 track, chuyển động gán theo quy tắc
    arrowhead-fill cited. Coverage 6,2%→~20,9%. (Độ rõ render khi 2 tay gần
    nhau — như Pha 9-14 làm cho 1 tay — vẫn là việc render riêng.)
  - Vi phạm giới hạn giải phẫu vẫn CHƯA xử lý — số đo CHÍNH XÁC nhất hiện có
    là 224/261 (85,8%) từ Pha 6 (kiểm cả 8 khớp, không riêng PIP; xem lưu ý
    quan trọng về khả năng lệch định nghĩa CMC ngón cái ở mục "Pha 6"), thay
    cho số ước lượng cũ 52,1%/119-261 ở Pha 3 (chỉ riêng PIP).
- **Tầng đánh giá (Pha 6) đã đo, CHƯA sửa gì** (đúng phạm vi "task ĐO" của
  chính nó) — việc ưu tiên tiếp theo theo khuyến nghị của Pha 6 (xem mục
  "Pha 6" phía trên và `ROADMAP.md`):
  - Điều tra riêng ngón cái: đối chiếu định nghĩa `thumb.cmc` của
    3d-hands-benchmark với định nghĩa lâm sàng CMC flexion đã trích trong
    `anatomical_limits.py` — nghi vấn lệch định nghĩa, chưa xác minh.
  - Soát lại `export/bone_lengths.py`'s giả định hình học ngón cái
    (`_THUMB_BASE_OFFSET_MM`/`_THUMB_BASE_ROTATION`) — MPJPE ngón cái
    (80,29) cao hơn hẳn 4 ngón còn lại (38,92-47,76), khả năng cao là
    nguồn lỗi tái dựng, tách biệt với chất lượng góc khớp gốc.
  - Giả thuyết che khuất (C4) và tương quan giải phẫu-FK (C3) đều KHÔNG
    được số liệu xác nhận ở Pha 6 — không dùng 2 giả thuyết này để định
    hướng sửa lỗi tiếp theo.
  - `hyperextension` (góc âm) chưa có giới hạn thật trong
    `anatomical_limits.py` (đặt 0 cho mọi khớp) — có thể đếm thiếu vi phạm.
- **Category 2's `hand_side` trả `None`** (chưa chốt được quy tắc thật —
  `rotation` của Cat 1 không áp dụng được, `fill` có tín hiệu nhưng còn
  nhiễu ~27%) — cần đối chiếu Lessons in SignWriting chương 6 trước khi
  implement thành quy tắc cứng. Danh sách đầy đủ các giả định Category 2
  chưa kiểm chứng khác nằm ở mục "Pha 2 — Category 2" phía trên.
- Góc khớp lấy từ dữ liệu thật (MediaPipe trên `3d-hands-benchmark`) nhưng
  chưa tinh chỉnh theo rig/mesh 3D thật — vẫn là stick-figure debug.
- `abduction` (độ xoè ngón) cho toàn bộ 261 symbol vẫn là số đoán — chưa đo
  được từ dataset hiện có (cần định nghĩa mặt phẳng tham chiếu để tính góc
  chiếu ngang, phức tạp hơn flexion).
- Dấu của `abduction` có thể cần đảo chiều cho tay trái tuỳ convention rig —
  chưa xử lý (ghi chú trong code, chưa có rig thật để kiểm chứng).
- `data/hand_joint_poses.json` là JSON nội bộ (nguồn cho `HAND_POSE_TABLE`,
  không có wrist quaternion vì đó là hàm số của fill/rotation, tính lúc
  chạy) — vẫn CHƯA có API export JSON công khai cho 1 symbol cụ thể (pose +
  wrist quaternion đã tính) nếu render cuối cùng là web three.js thay vì
  Blender/Open3D.
- 2 category cuối của ISWA (Location, Punctuation — tổng 13 base symbol
  trong số 652 base symbol toàn ISWA) chưa bắt đầu — xem `ROADMAP.md` Pha 6.
  Hạ tầng chung (`base_hex` xuyên suốt, dispatch theo category, `PoseTable`
  generic, contract render tách theo category kể từ Pha 2) đã sẵn sàng; mỗi category
  vẫn cần kiểu dữ liệu pose riêng của nó (vd Head&Face cần blend-shape) và
  class symbol riêng, không tái dùng được `HandJointPose`/`HandSymbol`
  hay `MotionPath`/`MovementSymbol`.
- Môi trường dùng Python 3.10 (máy hiện có) thay vì 3.11+ như brief ban đầu
  yêu cầu — không ảnh hưởng vì không dùng feature riêng của 3.11.
- **`SignTimeline` (Pha 3) đã xong ở phạm vi MVP-1** (1 symbol tay + tối đa
  1 symbol chuyển động, 6,2% sign thật đo trên SignBank+) — gói mới
  `fsw_r/timeline/`, không sửa file nào trong `core/` (đã xác nhận bằng
  `git diff --stat`). Chi tiết đầy đủ ở mục "Pha 3 — `SignTimeline`
  (MVP-1)" phía trên. Việc còn để ngỏ riêng cho phần này:
  - **Tầng validate giải phẫu** (giới hạn góc khớp thật) — chưa có. Phát
    hiện độc lập kiểm chứng được: PIP flexion > 110° ở **119/261 (45,6%)**
    symbol Category 1 (`max=167°`, phân bố theo ngón `ring=95, pinky=93,
    middle=55, index=32` — khớp đúng số brief trích theo từng ngón và giá
    trị max, nhưng brief nêu tổng "136/261, 52,1%" — con số này KHÔNG tái
    lập được, nhiều khả năng là lỗi tính toán ở nguồn brief; đã chọn ghi số
    tự kiểm chứng được (119/261) thay vì chép lại số brief mà không kiểm
    chứng).
  - **MVP-2** (sign có nhiều symbol tay/chuyển động hơn, ~20,9% sign) — cần
    logic phân biệt/gán track cho nhiều tay/nhiều chuyển động, MVP-1 chưa
    viết (né có chủ đích, xem lý do chọn phạm vi ở mục "Pha 3" phía trên).
  - `DEFAULT_SIGN_DURATION` (0,8s) là hằng số giữ chỗ — chưa có nguồn dữ
    liệu thời gian thật; Category 3 (Dynamics) dự kiến bù việc này (xem
    `ROADMAP.md`).
  - `SIGNBOX_TO_BODY_SCALE` và phép ánh xạ toạ độ signbox → không gian cơ
    thể hiện là tuyến tính đơn giản, chưa hiệu chỉnh theo dữ liệu thật.
  - Renderer PNG-sequence (`fsw-r-viz/render_timeline.py`) vẫn là công cụ
    debug stick-figure, không phải renderer trình bày cuối cùng — cùng tình
    trạng với renderer Category 1/2 đã ghi ở trên.
  - Thứ tự đề xuất làm tiếp theo (đã cập nhật trong `ROADMAP.md`): (a) tầng
    validate giải phẫu, (b) Category 3 Dynamics (category DUY NHẤT mã hoá
    thời gian mà `SignTimeline` đang thiếu), (c) MVP-2, (d) Category 5 Body.
