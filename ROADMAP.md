# fsw-r — Roadmap: cover toàn bộ ISWA/SignWriting, input là FSW

## Mục tiêu

Xây dựng framework nhận **FSW (Formal SignWriting ASCII) thật làm input**,
cover được **toàn bộ ISWA** (không chỉ Category 1 Hands như hiện tại) —
điểm khác biệt đã xác nhận qua khảo sát related work: chưa có hệ nào
(tuniSigner, các hệ dùng SWML 2012-2015, JASigning/HamNoSys...) làm cả 2 việc
này cùng lúc (xem `PROGRESS.md` phần related work).

Vì khối lượng rất lớn (~37,000 symbol ISWA), **chia theo category, làm từng
pha, mỗi pha ra được kết quả dùng được ngay** — không làm 1 lần hết toàn bộ.

## Các category ISWA (nguồn: `sutton-signwriting/core`, `src/fsw/fsw-structure.js`)

**Đã sửa lại bảng này** (trước đó liệt kê 8 dòng, tách riêng Trunk và
Limb — SAI, chưa đối chiếu nguồn thật lúc viết). Đối chiếu trực tiếp mảng
`category` thật trong `fsw-structure.js` (tải qua `npm pack`, không đoán):

```js
const category = [0x100, 0x205, 0x2f7, 0x2ff, 0x36d, 0x37f, 0x387];
// "hand, movement, dynamics, head, trunk & limb, location, and punctuation"
```

Mảng này có đúng **7 phần tử** — Trunk và Limb dùng CHUNG 1 ranh giới
category (`0x36d`), không phải 2 category riêng. `ranges` object trong cùng
file JS vẫn có 2 key `trunk`/`limb` tách riêng để tra cứu tiện, nhưng đó
KHÔNG phải là 2 category cấp cao nhất.

| Category | Range hex | Số symbol (ước tính theo range) | Bản chất dữ liệu |
|---|---|---|---|
| 1. Hands | `0x100–0x204` | 261 base symbol (10 group theo số đếm ASL 1-10) | Joint angle (góc gập khớp ngón) + wrist orientation (quaternion) |
| 2. Movement | `0x205–0x2f6` | 242 base symbol | Quỹ đạo chuyển động theo thời gian (đường thẳng/cong/vòng...) |
| 3. Dynamics | `0x2f7–0x2fe` | 8 base symbol | Tốc độ/nhịp/độ nhấn của chuyển động (đi kèm Movement) |
| 4. Head & Face | `0x2ff–0x36c` | ~110 base symbol | Biểu cảm mặt — blend-shape, KHÔNG phải joint-angle |
| 5. Trunk & Limb | `0x36d–0x37e` | 18 base symbol (Trunk `0x36d–0x375` 9 + Limb `0x376–0x37e` 9) | Chuyển động thân người + vị trí/chuyển động tay-chân (không phải bàn tay) |
| 6. Location | `0x37f–0x386` | 8 base symbol | Điểm chạm/vị trí trong không gian ký hiệu |
| 7. Punctuation | `0x387–0x38b` | 5 base symbol | Dấu câu trong văn bản SignWriting |

(Số symbol ở trên là **base symbol** — tổng cộng 7 category = 652 base
symbol, khớp với `ranges.all = [0x100, 0x38b]` trong `fsw-structure.js`, và
gần đúng với con số "hơn 639 base symbol" hay thấy trích dẫn ở tài liệu
SignWriting công khai. **Category 1 Hands chỉ có 261/652 base symbol** —
KHÔNG PHẢI là con số ~639/652 tổng, đây là lỗi đã lỡ ghi nhầm trong
`fsw-r/README.md` và `PROGRESS.md` trước đó, cần sửa lại. Mỗi base symbol
còn nhân thêm với số `fill × rotation` hợp lệ của riêng nó (Hands: tối đa
6×16=96 biến thể/base symbol) — đây là nguồn gốc con số ISWA tổng ~37,000
symbol hay được trích dẫn.)

Chi tiết đầy đủ (30 ranh giới group, hàm decode/encode, test biên) nằm ở
`fsw-r/src/fsw_r/core/iswa_data.py` — bảng ở đây chỉ để tham khảo nhanh.

## Lộ trình theo pha

### Pha 1 — Hands (Category 1) — ĐÃ XONG (261/261 base symbol)

**Lưu ý thuật ngữ (dễ nhầm, đã nhầm 1 lần):** "Category" và "Group" là 2
tầng khác nhau trong ISWA, không dùng lẫn:
- **Category** = 1 trong 8 nhóm lớn của toàn ISWA (Hands, Movement,
  Dynamics, Head&Face, Trunk, Limb, Location, Punctuation) — bảng ở trên.
- **Group** = tầng con BÊN TRONG Category 1 (Hands), chia theo số đếm ASL
  1-10. Vd **Group 1 "Index Finger" = 14 base symbol** (`0x100–0x10d`),
  Group 2 "Index & Middle" = số khác, v.v. **Category 1 (Hands) = tổng cả
  10 group cộng lại = 261 base symbol**, không phải 14.

**Trạng thái hiện tại:** parse FSW thật qua `sutton-signwriting`,
`rotation`/`fill` → quaternion 3D đã xác nhận đúng qua chart gốc + test (kể
cả bug gimbal-lock ở Floor Plane đã tìm ra và sửa). **Đủ 10/10 group Hands,
261/261 base symbol** (tên lấy từ ảnh/HTML thật signwriting.org, không
đoán):

**Kiến trúc đã đổi so với brief ban đầu:** 4 tầng class ban đầu
(`FSWBaseSymbol` → `FSWRenderableSymbol` → `SymbolGroupN` → `BaseSymbolX`,
1 class Python/base symbol) đã được refactor sang **data-driven**: 1 class
`HandSymbol` duy nhất cho cả 261 base symbol, tra góc khớp từ
`data/hand_joint_poses.json` (`core/pose_table.py`) thay vì hardcode trong
từng class — xem `PROGRESS.md` mục "Refactor tầng Group sang data-driven"
để biết lý do (261 class chỉ khác nhau ở 15 con số/class, tức là dữ liệu
giả dạng behavior) và chi tiết. `groups/` (10 file cũ) đã xoá.

| Group | Tên thật | Base symbol đã làm | Tổng base symbol group |
|---|---|---|---|
| 1 | Index Finger | 14/14 | 14 |
| 2 | Index & Middle Fingers | 16/16 | 16 |
| 3 | Index, Middle, Thumb | 38/38 | 38 |
| 4 | Four Fingers | 8/8 | 8 |
| 5 | Five Fingers | 58/58 | 58 |
| 6 | Baby Finger | 30/30 | 30 |
| 7 | Ring Finger | 22/22 | 22 |
| 8 | Middle Finger | 19/19 | 19 |
| 9 | Index & Thumb | 40/40 | 40 |
| 10 | Thumb | 16/16 | 16 |

Tổng: **261/261 base symbol — ĐÃ XONG HẾT** Category 1 (chi tiết cách làm
full, gồm 2 script tự động hoá `gen_group.py`/`gen_test.py`, xem
`PROGRESS.md` mục "Làm full toàn bộ 261 base symbol"). Lưu ý: với group 6-9, base
symbol số 1 KHÔNG phải là hình dạng đơn giản trùng tên group (vd group 6
"Baby Finger" nhưng base symbol 1 lại là "Index Middle Ring", không có
ngón út) — đã xác nhận bằng cách xem ảnh GIF thật của từng symbol trước khi
viết joint pose, không suy đoán từ tên group.

**Góc khớp của cả 261/261 base symbol giờ lấy từ dữ liệu thật** (không còn
đoán): `sign-language-processing/3d-hands-benchmark` — ảnh thật của 1 bàn
tay thật, 261 handshape × 6 góc, cộng pose 3D ước lượng sẵn bằng MediaPipe
(3 phiên bản, 48 lần chụp/symbol). Cách làm: map symbol_id ISWA → index
trong mảng `(48, 261, 6, 21, 3)` (thứ tự khớp `sorted(os.listdir(...))`
đúng bằng thứ tự group/base_symbol_number của mình — đã verify bằng cách
đọc script sinh dữ liệu gốc), lấy median qua 48 lần chụp, tính góc `flexion`
= góc giữa 2 vector xương liên tiếp (wrist→mcp, mcp→pip, pip→dip, dip→tip).
Đã cập nhật cả 10 file group + test tương ứng lúc đó (1358 test pass; sau
refactor data-driven, còn 596 test — xem `PROGRESS.md`). Lưu ý quan trọng: đây là
**ước lượng của MediaPipe trên ảnh thật, không phải motion-capture đã xác
thực** (chính benchmark cũng không claim vậy) — nhưng đáng tin hơn nhiều so
với số tự đoán. `abduction` (độ xoè ngón) KHÔNG đo được bằng cách này, vẫn
là số đoán giữ nguyên từ baseline cũ.

**Việc còn lại của Pha 1** (đã làm xong phần base symbol chính, còn 2 việc phụ):
- [x] Làm hết các base symbol còn lại trong mỗi group — **xong, 261/261**.
- [ ] Tính lại `abduction` (độ xoè ngón) từ dữ liệu thật (hiện chưa làm —
      cần thêm 1 bước tính góc chiếu ngang so với mặt phẳng lòng bàn tay,
      phức tạp hơn flexion vì cần định nghĩa mặt phẳng tham chiếu).
- [ ] Validate `rotation`/`fill` cho các group KHÁC group 1 — quy tắc
      `_rotation_angle_degrees()`/`_fill_facing_degrees()`/`_fill_plane_degrees()`
      hiện suy ra từ 1 group (Index) + 1 chart, cần kiểm tra xem có áp dụng
      y hệt cho toàn bộ 10 group hay có group nào khác quy tắc (ví dụ
      handshape đối xứng có thể có rotation/fill hoạt động khác — đã ghi
      chú rủi ro này trong `fsw-r/README.md`). Dataset benchmark cũng có đủ
      6 orientation/symbol — có thể dùng để validate luôn việc này.

### Pha 2 — Movement (Category 2) — ĐÃ XONG (242/242 base symbol)

**Vì sao làm ngay sau Hands:** đây là thứ biến pose tĩnh thành "động tác"
(motion) — đúng nhu cầu ra clip 3D đã bàn trước đó. Không có Movement thì
mãi mãi chỉ demo được ảnh tĩnh.

**Trạng thái:** xong — đủ 242/242 base symbol, `MovementSymbol` +
`data/movement_paths.json` (sinh bằng công thức từ bảng
`(path_type × plane)`, không đo). Chi tiết đầy đủ (bài kiểm tra khả năng mở
rộng cho Category 5, danh sách giả định chưa kiểm chứng, số liệu
`hand_side`) xem `PROGRESS.md` mục "Pha 2 — Category 2". Tóm tắt nhanh:
- `hand_side` trả `None` (chưa chốt quy tắc thật — xem số liệu bên dưới,
  vẫn giữ nguyên vì đây là phát hiện gốc, không phải việc còn phải làm).
- Nhiều tham số hình học (`curvature`/`amplitude`/`repeat`, `plane` của
  group 11/12/20, ngữ nghĩa `is_hit`) là giả định CHƯA kiểm chứng, ghi rõ
  trong `_meta` của `data/movement_paths.json` và trong
  `core/movement_paths.py`'s docstring.
- Renderer animation (interpolate theo thời gian, hiển thị `MotionPath`
  thành chuyển động thật) CHƯA làm — `sample_trajectory()` mới sinh được
  điểm 3D tĩnh (24 điểm mặc định), chưa có renderer riêng cho Category 2
  (khác `HandMeshRenderer3D`, vốn chỉ nhận `FSWHandRenderable`).

**Dùng ngay pattern data-driven (bảng dữ liệu + 1 class generic), KHÔNG lặp
lại pattern "1 class Python/base symbol" ban đầu của Category 1.** Category
1 tự nó đã đi qua đúng bài học này: bắt đầu bằng 261 class riêng
(`groups/`), rồi refactor sang 1 `HandSymbol` + bảng JSON vì 96% class chỉ
khác nhau ở vài con số, không phải hành vi (xem `PROGRESS.md`). Pha 2 nên
áp dụng data-driven pattern **ngay từ đầu**, không đợi tích luỹ 242 class
rồi mới refactor lại.

**Bảng ISWA valid combinations (`core/iswa_data.py`) là BẮT BUỘC cho
Category 2, không phải tuỳ chọn như đã cân nhắc lúc đầu cho Category 1:**
242 base symbol của Movement có **17 mẫu (fills, rotations) khác nhau**
(nhiều base chỉ có 8 rotation hoặc 2-4 fill, xem số liệu tham khảo ở bảng
category phía trên) — biến thiên nhiều hơn hẳn Category 1 (chỉ 2 mẫu: đủ
6×16, hoặc 1 trong 8 ngoại lệ). `iswa_data.py` đã tổng quát hoá đủ để đọc
range Category 2 (`0x205–0x2f6`) mà không cần sửa gì thêm — chỉ cần dùng.

**Đã làm xong (xem `PROGRESS.md` mục "Pha 2 — Category 2" để biết chi tiết
đầy đủ):** phát hiện + sửa contract trừu tượng ở `core/renderable_symbol.py`
CHƯA generic (`FSWRenderableSymbol` cũ khai `get_joint_pose() -> HandJointPose`
làm abstract cứng, `MovementSymbol` không kế thừa nổi — tách lại thành
marker chung + `FSWHandRenderable`/`FSWMotionRenderable`, làm TRƯỚC khi
viết `MovementSymbol`, đúng như phải làm); `parse_fsw_symbol_key("S22b03")`
parse thành công; `_CATEGORY_SYMBOL = {1: HandSymbol, 2: MovementSymbol}`
(đúng 1 dòng mới trong `registry.py`, cộng các file `core/` khác chỉ bị
THÊM MỚI thuần tuý — không sửa logic cũ, xem bài kiểm tra khả năng mở rộng
ở `PROGRESS.md`); `MotionPath`/`PathType`/`MovementPlane` (kiểu dữ liệu
mới, không tái dùng `HandJointPose`); `data/movement_paths.json` (242 entry,
sinh bằng công thức từ bảng `(path_type × plane)`, không đo).

**Việc còn lại của Pha 2 (chưa làm, không phải đã làm sai):**
- Renderer animation (interpolate theo thời gian, biến `MotionPath` /
  `sample_trajectory()` thành chuyển động thật) — `HandMeshRenderer3D` chỉ
  render 1 pose tĩnh, chưa có renderer riêng cho Category 2.
- `HandSide` cần thêm giá trị `BOTH` (xem phát hiện `fill` bên dưới) —
  chưa thêm, vì `hand_side` của Category 2 hiện trả `None` chứ chưa gán
  `BOTH` cho trường hợp nào.
- Nhiều tham số hình học (`curvature`/`amplitude`/`repeat` theo từng symbol
  cụ thể, `plane` của group 11/12/20, ngữ nghĩa `is_hit`) vẫn là giả định
  chưa kiểm chứng — danh sách đầy đủ ở `PROGRESS.md`.

**Phát hiện quan trọng (đo trên corpus thật, CHƯA đối chiếu tài liệu chính
thức — chỉ là số liệu, không phải quy tắc đã chốt để implement):** quy tắc
`rotation >= 8 → LEFT` của Category 1 **không áp dụng cho Category 2**.
Kiểm chứng trên `sign-language-processing/signbank-plus` (`data/raw.csv`,
257.800 sign, 3,4 triệu symbol token) — lọc các sign chỉ có **đúng 1 symbol
tay** (nên biết chắc symbol Category 2 trong sign đó thuộc tay nào), rồi
đối chiếu với `rotation`/`fill` của symbol Category 2 xuất hiện trong sign:

| Tay (suy từ symbol tay Cat 1 duy nhất trong sign) | Cat 2 rotation 0-7 | Cat 2 rotation 8-15 |
|---|---|---|
| RIGHT | 62,2% | 37,8% |
| LEFT | 58,5% | 41,5% |

Nếu `rotation >= 8 → LEFT` đúng cho Cat 2 thì hàng LEFT phải gần 100% —
2 hàng gần như giống hệt nhau, tức **rotation không dự đoán được tay** ở
Category 2.

| Tay (suy từ Cat 1) | Cat 2 fill=0 | Cat 2 fill=1 |
|---|---|---|
| RIGHT | 97,4% | 0,5% |
| LEFT | 72,0% | 26,7% |

`fill` có tín hiệu RÕ hơn nhiều (fill=1 xuất hiện nhiều hơn ~53 lần khi tay
là trái — khớp hướng với quy ước SignWriting: fill code 0/1/2 = ISWA fill
1/2/3 = phải/trái/cả hai), nhưng vẫn còn nhiễu đáng kể (LEFT vẫn ra fill=0
tới 72%). **Chưa đủ tin cậy để implement thành quy tắc cứng** — cần đối
chiếu thêm Lessons in SignWriting chương 6 trước khi chốt. Đây là lý do
`HandSide` cần thêm `BOTH` (giá trị ISWA fill code 2 ám chỉ) thay vì chỉ
RIGHT/LEFT nhị phân.

### SignTimeline (MVP-1) — ĐÃ XONG

**Lưu ý đánh số:** đây KHÔNG phải "Pha 3" theo đánh số category ở file này
(mục dưới, "Dynamics", vẫn giữ số Pha 3 như cũ) — trong `PROGRESS.md`, việc
này được gọi là "Pha 3" theo nghĩa thứ tự thời gian làm việc (Pha 1 = Hands,
Pha 2 = Movement, Pha 3 = SignTimeline), khác trục đánh số với category. Ghi
chú ở đây để tránh nhầm giữa 2 cách đánh số Pha khác nhau trong 2 file.

**Việc đã làm:** gói mới `fsw_r/timeline/` (KHÔNG sửa file nào trong
`core/` — xác nhận bằng `git diff --stat`), dịch layout 2D tĩnh của FSW
(toạ độ signbox `x`/`y`) sang chuỗi pose theo thời gian (`SignTimeline` →
`PoseFrame`). Phạm vi cố ý giới hạn ở **MVP-1**: sign có đúng 1 symbol tay
(Category 1), tối đa 1 symbol chuyển động (Category 2), không có category
nào khác — đo trên SignBank+ (257.800 sign) thì phạm vi này cover 6,2% sign
thật (~16.000 sign). Chi tiết đầy đủ (kiến trúc 5 tầng D1-D5, bảng độ tin
cậy theo tầng, các phát hiện kỹ thuật, danh sách giả định chưa kiểm chứng,
phát hiện về giới hạn giải phẫu khớp PIP) xem `PROGRESS.md` mục "Pha 3 —
`SignTimeline` (MVP-1)".

**Vì sao giới hạn đúng phạm vi này:** MVP-1 né mọi bước phải "đoán" (gán
chuyển động cho tay nào khi có 2 tay, phân biệt 2 tay đồng thời hay 1 tay 2
thời điểm, dùng `y` làm proxy thời gian...) — mọi tầng xử lý đều xác định
(deterministic), nên nếu output sai thì chắc chắn lỗi nằm ở toán anchor/nội
suy, không phải ở logic phân biệt còn chưa viết.

**Việc còn lại (không phải làm sai, mà là ngoài phạm vi MVP-1 có chủ đích):**
- Tầng validate giải phẫu (giới hạn góc khớp thật) — chưa có, xem phát hiện
  PIP flexion > 110° ở 119/261 (45,6%) symbol trong `PROGRESS.md`.
- MVP-2 (sign có nhiều symbol tay/chuyển động hơn, ~20,9% sign) — cần logic
  phân biệt/gán track chưa viết ở MVP-1.
- `DEFAULT_SIGN_DURATION` (0,8s) là hằng số giữ chỗ, chưa có nguồn dữ liệu
  thời gian thật (Category 3 Dynamics dự kiến bù việc này).
- `SIGNBOX_TO_BODY_SCALE` và phép ánh xạ toạ độ signbox → không gian cơ thể
  hiện là tuyến tính đơn giản, chưa hiệu chỉnh theo dữ liệu thật.

### Pha 3 — Dynamics (Category 3) — ĐÃ XONG tầng ký hiệu (8/8 base symbol)

**Trạng thái:** xong ở tầng ký hiệu — `DynamicsSymbol` + `FSWModifierSymbol`
(contract riêng, KHÔNG nằm trong cây `FSWRenderableSymbol` vì Dynamics không
render gì) + `data/dynamics_modifiers.json` (8 entry, AUTHORED từ tên thật
tra trên signbank.org). Chi tiết đầy đủ (bảng tên/biến thiên fill-hay-
rotation, giả định chưa kiểm chứng) ở `PROGRESS.md` mục "Pha 4 — Category 3
& 5". **CHƯA nối vào `SignTimeline`** — đó vẫn là việc còn lại, cố ý ngoài
phạm vi task làm tầng ký hiệu.

**Đáng chú ý sau khi có `SignTimeline`:** đây là category DUY NHẤT mã hoá
thông tin thời gian (tốc độ/nhịp/độ nhấn) mà `SignTimeline` hiện đang thiếu
(`DEFAULT_SIGN_DURATION` chỉ là hằng số giữ chỗ) — nối `DynamicsModifier`
vào đó sẽ trực tiếp thay được giả định đó bằng dữ liệu thật (dù vẫn là
AUTHORED, không đo), không chỉ là "+8 base symbol, +14,2 điểm độ phủ" về
số lượng.

### Pha 4 — Head & Face (Category 4)

**Ngoài phạm vi của phần việc này — thành viên khác trong nhóm phụ trách
Category 4.** Giữ mục này lại chỉ để tham khảo cấu trúc chung, không phải
việc cần làm tiếp theo ở đây.

**Khác biệt lớn:** không phải joint-angle (khớp xương) mà là **blend-shape**
(biểu cảm mặt: nhướng mày, chu miệng...). Cần thiết kế 1 hệ kiểu dữ liệu
hoàn toàn mới (`FaceExpressionPose` hay tương tự), không tái dùng được
`HandJointPose`/`FingerPose`. Renderer cũng cần thêm khả năng áp blend-shape
lên mesh mặt (không phải rig xương).

### Pha 5 — Trunk & Limb / "Body" (Category 5) — ĐÃ XONG tầng ký hiệu (18/18 base symbol)

**Trạng thái:** xong ở tầng ký hiệu — `BodySymbol` + `FSWBodyRenderable`
(contract mới, thêm vào cây `FSWRenderableSymbol`, không sửa 4 nhánh cũ) +
`data/body_poses.json` (18 entry, AUTHORED từ tên thật tra trên
signbank.org — bao gồm việc xác nhận `0x36d` = "Shoulder Hip Spine", ký
hiệu mốc/tham chiếu tổng hợp của Trunk, đúng giả thuyết đặt ra trước khi
thiết kế `BodyPose`). Group 28 (Limb) hoá ra là các khối dựng hình một chi
sơ đồ hoá ("Limb Length 1".."7" + Combinations + Fingers), KHÔNG phải 9
khớp giải phẫu riêng biệt như tên category gợi ý — `BodyPose` phản ánh đúng
cấu trúc thật này. Chi tiết đầy đủ ở `PROGRESS.md` mục "Pha 4 — Category 3
& 5". **CHƯA nối vào `SignTimeline`** (`timeline/anchor.py` vẫn dùng toạ độ
signbox tuyến tính đơn giản, chưa dùng `BodyPose` làm khung tham chiếu) —
cố ý ngoài phạm vi task làm tầng ký hiệu.

**Thứ tự đề xuất tiếp theo** (cập nhật sau khi cả `SignTimeline` MVP-1 VÀ
Category 3/5's tầng ký hiệu đã xong):
1. **Tầng validate giải phẫu** (giới hạn góc khớp thật, vd PIP flexion) —
   làm trước vì rẻ (không cần category mới), và mọi pose đã sinh ra từ Pha
   1-3 đều có thể sai theo hướng này mà chưa có cách tự phát hiện.
2. **Nối Category 3/5 vào `SignTimeline`** — `DynamicsModifier.speed` thay
   `DEFAULT_SIGN_DURATION`'s hằng số giữ chỗ; `BodyPose` làm khung tham
   chiếu không gian thật cho `timeline/anchor.py` thay vì toạ độ signbox
   tuyến tính đơn giản hiện tại. Làm ngay sau tầng validate giải phẫu để dữ
   liệu thời gian/không gian mới cũng được validate cùng lúc.
3. **MVP-2** (nới phạm vi `SignTimeline` lên sign có nhiều symbol tay/
   chuyển động hơn, ~20,9% sign đo trên SignBank+) — cần logic phân biệt/
   gán track chưa viết ở MVP-1, nên làm sau khi nền tảng (giải phẫu +
   Dynamics/Body) đã vững.
4. **Category 6-7 (Location, Punctuation)** — xem Pha 6 dưới đây; category
   ISWA cuối cùng còn lại sau Pha 1-5.

### Pha 6 — Location & Punctuation (Category 6-7)

Category ISWA cuối cùng chưa làm (Pha 1, 2, 3, 5 đều đã xong tầng ký hiệu;
Pha 4 do thành viên khác phụ trách, cũng đã xong). Nhỏ nhất (8+5 base
symbol), mang tính bổ trợ:
- Location: điểm chạm/vị trí trong không gian ký hiệu (ảnh hưởng vị trí đặt
  tay trong scene, không phải pose của tay).
- Punctuation: dấu câu trong văn bản SignWriting, không ảnh hưởng animation
  3D trực tiếp — có thể chỉ cần parse qua để không lỗi, không cần render.

## Ràng buộc kiến trúc cần giữ xuyên suốt mọi pha

- **Nguyên tắc "base symbol + fill + rotation = đủ", nhưng công thức không
  dùng chung giữa các category.** Cấu trúc key FSW (`base + fill +
  rotation`) đảm bảo: code đúng 1 lần cách 1 base symbol phản ứng với
  fill/rotation của chính nó → mọi biến thể fill×rotation của base symbol
  đó tự động được cover, không cần định nghĩa riêng từng biến thể. Đây LÀ
  nguyên tắc đúng và đã áp dụng thành công ở Category 1 (Hands, xem
  `_default_wrist_orientation()`). NHƯNG: công thức cụ thể (fill/rotation
  → pose 3D) **khác nhau giữa các category**, và trong Movement thậm chí
  khác nhau giữa các NHÓM base symbol trong cùng 1 category (xem bằng
  chứng: `signwriting/utils/mirror/mirror.py` có hàng chục bảng công thức
  riêng theo nhóm base — `_XOR_PAIRED_BASES`, `_CEILING_HITS_BASES`...).
  Nên với Pha 2 trở đi, KHÔNG giả định tái dùng được công thức của Hands —
  cần tìm công thức riêng cho từng category (có thể theo từng nhóm base
  trong category đó, giống cách `mirror.py` đã nhóm), rồi mới áp dụng lại
  đúng nguyên tắc "code 1 lần, cover hết biến thể" cho nhóm đó.
- Mỗi category/group là 1 module riêng, **không group nào biết về group
  khác** — renderer và core (`registry.py`, `fsw_ast.py`, `fswr_converter.py`)
  luôn phải category-agnostic, đúng nguyên tắc đã áp dụng từ Pha 1.
- Parse FSW luôn qua thư viện thật `signwriting`/`sutton-signwriting`,
  không tự chế regex mô phỏng lại phần thư viện đã có sẵn.
- Mỗi base symbol mới thêm vào phải có test khoá hành vi cụ thể (như
  `test_wrist_orientation_points_finger_down_at_180_degrees` đã làm) —
  tránh lặp lại việc sửa qua sửa lại 1 quy tắc nhiều lần vì hiểu nhầm domain.
- Domain knowledge (range hex, tên symbol, ý nghĩa fill/rotation...) luôn
  phải trích từ nguồn thật (source code `sutton-signwriting/core`, chart/
  lesson trên `signwriting.org`) — không đoán, ghi rõ nguồn trong docstring.

## Rủi ro / điều chưa chắc chắn

- Quy tắc `rotation`/`fill` → 3D hiện chỉ verify trên Group 1 (Index) qua 1
  chart — CHƯA chắc mọi group Hands khác đều theo đúng công thức này 1:1
  (đặc biệt handshape đối xứng, xem README `fsw-r`).
- Category Movement/Head&Face đòi hỏi kiểu dữ liệu và renderer khác hẳn Pha
  1 — không thể chỉ "copy pattern group cũ", cần thiết kế lại 1 phần kiến
  trúc core khi bắt đầu Pha 2 và Pha 4.
- Chưa có rig/mesh 3D thật nào — mọi thứ vẫn là stick-figure debug
  (`fsw-r-viz`). Nếu mục tiêu cuối là clip 3D chất lượng trình bày được,
  cần tích hợp Blender/three.js ở 1 giai đoạn nào đó (chưa xếp vào pha nào
  cụ thể ở trên, cần bàn thêm).
