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
làm ưu tiên tiếp theo.

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
- `fsw-r`: `mypy --strict` sạch (41 file `src/`; `src/`+`tests/` còn 1 lỗi
  cũ không liên quan ở `test_head_symbol.py`, xác nhận có từ trước Pha 4
  qua `git stash`), `pytest` **1.350/1.350 pass** (1.264
  trước Pha 4 + 67 test Pha 4 + 19 test mới Pha 5: `test_forward_
  kinematics.py`, `test_pose_export.py` — đúng 1 test cũ,
  `test_build_symbol_raises_for_unsupported_category`, buộc phải đổi
  target ở Pha 4 thay vì giữ nguyên, xem mục "Pha 4" để biết vì sao).
- `fsw-r-viz`: `mypy --strict` sạch (4 lỗi cũ không liên quan — 2
  `FuncAnimation` type stub, 1 `ndarray` generic, xác nhận có từ trước Pha
  4/5 qua `git stash`), `pytest` **27/27 pass** (tăng từ 5/5 khi
  `fsw-r-viz` còn chỉ có Category 1 — đã qua Pha 4 (Head&Face merge, nhóm
  khác) + Pha 5 (`test_render_pose_video.py`) từ lúc đó).
- Demo trực quan (`python -m fsw_r_viz.demo`) render đúng cả rotation lẫn
  fill: joint pose giống hệt nhau ở mọi rotation/fill/hand_side, chỉ hướng
  ngón (rotation) hoặc mặt bàn tay/mặt phẳng cánh tay (fill) thay đổi.
- `demo.py` của `fsw-r` giờ có 3 phần: rotation sweep, FSW sign string 2 tay
  (AST→FSWR), và fill sweep — đều dựng instance qua `symbol_from_fsw(...)`
  với key FSW thật, không còn gọi thẳng constructor với int tự đặt.

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
- **Tầng export `.pose`/video (Pha 5) mới xong bước 1-2 — chưa có IK cánh
  tay, chưa có thân tĩnh, chưa nối Category 3 vào duration** (bước 3-4, cố
  ý ngoài phạm vi, xem mục "Pha 5 — Tầng export" phía trên và
  `ROADMAP.md`). Cụ thể còn thiếu:
  - Two-bone IK cho cánh tay (vai→khuỷu→cổ tay) + tư thế thân tĩnh — hiện
    `POSE_LANDMARKS`/`POSE_WORLD_LANDMARKS` để confidence 0 toàn bộ, chỉ có
    2 bàn tay là có dữ liệu thật.
  - `DynamicsModifier.speed` chưa nối vào frame count/fps của video xuất ra
    — mọi video vẫn dùng `DEFAULT_SIGN_DURATION` cố định.
  - Độ dài xương (`export/bone_lengths.py`) chỉ có nguồn cho đốt ngón; độ
    dài xương bàn tay, khoảng cách khớp đốt bàn ngón, góc gắn ngón cái đều
    là ước lượng riêng — xem "giả định chưa kiểm chứng" ở mục "Pha 5".
  - `save_video()` (MP4 thật) chưa từng chạy thành công trên máy hiện tại
    (thiếu `vidgear` + ffmpeg thật) — mọi bằng chứng video hiện tại là GIF
    fallback, không phải MP4.
  - 52,1%/119-261 tư thế Category 1 vượt giới hạn giải phẫu (xem mục "Pha
    3") vẫn CHƯA xử lý — sẽ lộ rõ hơn khi có video thật thay vì chỉ đọc số.
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
