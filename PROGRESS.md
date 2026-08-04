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
  rồi dựng lại) — `registry.py` dispatch theo category
  (`_CATEGORY_SYMBOL`), sẵn sàng thêm Category 2 chỉ bằng 1 dòng code mới
  + code hoàn toàn mới cho riêng Category 2 (xem mục ngay phía trên).
- `fsw-r`: `mypy --strict` sạch (26 file), `pytest` **615/615 pass**
  (`test_iswa_structure.py`, `test_pose_table.py`, `test_hand_symbol.py`,
  `test_wrist_orientation.py`, `test_hand_side.py`, `test_iswa_data.py`,
  `test_fsw_symbol_key.py`, `test_fsw_ast.py`, `test_registry.py`,
  `test_fswr_converter.py`).
- `fsw-r-viz`: `mypy --strict` sạch (6 file), `pytest` 5/5 pass
  (`test_hand_geometry.py`, `test_plot_hand.py`).
- Demo trực quan (`python -m fsw_r_viz.demo`) render đúng cả rotation lẫn
  fill: joint pose giống hệt nhau ở mọi rotation/fill/hand_side, chỉ hướng
  ngón (rotation) hoặc mặt bàn tay/mặt phẳng cánh tay (fill) thay đổi.
- `demo.py` của `fsw-r` giờ có 3 phần: rotation sweep, FSW sign string 2 tay
  (AST→FSWR), và fill sweep — đều dựng instance qua `symbol_from_fsw(...)`
  với key FSW thật, không còn gọi thẳng constructor với int tự đặt.

## Việc còn để ngỏ / chưa làm

- **Category 1 (Hands) đã xong: đủ 261/261 base symbol, cả 10/10 group** —
  mục còn lại dưới đây là thứ CHƯA làm trong phạm vi Category 1, cộng 6
  category khác của ISWA (Trunk và Limb là 1 category chung, không phải 2
  — xem `ROADMAP.md` mục "Các category ISWA" — nên tổng là 7 category, 6
  category còn lại ngoài Hands; xem `ROADMAP.md` Pha 2 trở đi).
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
- 6 category khác của ISWA (Movement, Dynamics, Head & Face, Trunk & Limb,
  Location, Punctuation — tổng ~391 base symbol còn lại trong số 652 base
  symbol toàn ISWA) chưa bắt đầu — xem `ROADMAP.md` Pha 2 trở đi. Hạ tầng
  chung (`base_hex` xuyên suốt, dispatch theo category, `PoseTable`
  generic) đã sẵn sàng; mỗi category vẫn cần kiểu dữ liệu pose riêng của nó
  (vd Movement cần "motion path", Head&Face cần blend-shape) và class
  symbol riêng, không tái dùng được `HandJointPose`/`HandSymbol`.
- Môi trường dùng Python 3.10 (máy hiện có) thay vì 3.11+ như brief ban đầu
  yêu cầu — không ảnh hưởng vì không dùng feature riêng của 3.11.
