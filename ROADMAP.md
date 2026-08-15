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

#### Chuỗi sửa nguồn dữ liệu Category 2 (4/4 — HOÀN TẤT): `symbol_id` →
`path_type` → `amplitude` → `plane`/`is_hit`

4 việc này BẮT BUỘC làm THEO ĐÚNG THỨ TỰ trên (không đổi chỗ, không làm song
song) — lý do ràng buộc thứ tự nêu ở mục `amplitude` bên dưới; `plane`/
`is_hit` được thêm vào cuối chuỗi sau khi phát hiện task 2 chưa sửa hết
(chính `_meta` của `movement_paths.json` tự khai còn sót).

- **1/4 — `symbol_id` dùng `symidArr` chuẩn: ĐÃ XONG** (`PROGRESS.md` mục
  "Pha 19"). `symbol_id_of()` giờ lấy từ thư viện tham chiếu ISWA thật
  (`@sutton-signwriting/core`'s `symidArr`, qua `data/iswa_symbol_ids.json`),
  không còn tự suy từ `GROUP_START` nội bộ nữa — sửa 328/652 base symbol có
  `symbol_id` hiển thị sai, thêm hẳn trường variation trước đó bị bỏ sót.
  `group_of()`/`GROUP_START` giữ nguyên KHÔNG đổi (việc này chỉ đổi trường
  hiển thị `symbol_id`, không đụng khoá tra cứu `base_hex` hay bảng
  `movement_paths`/`finger_articulations`).
- **2/4 — `path_type` suy SAI nguồn: ĐÃ XONG** (`PROGRESS.md` mục "Pha 20").
  `path_type` giờ suy từ **TÊN BASE SYMBOL thật** (signbank.org, qua
  `data/iswa_base_symbol_names.json`), không còn từ TÊN GROUP nữa — sửa
  134/242 (55,4%) base symbol có `path_type` sai (vd group "Straight Wall
  Plane" từng gán `path_type="straight"` cho cả 43 base, kể cả những base
  tên là Zigzag/Box/Check/Corner/Peaks). `PathType` mở rộng từ 5 lên 22 giá
  trị. `plane`/`is_hit` CÒN SÓT (vẫn suy từ tên GROUP) — task đó tự khai
  trong `_meta`, sửa nốt ở 4/4.
- **3/4 — `amplitude` cứng 10.0 cho toàn bộ 242 base: ĐÃ XONG**
  (`PROGRESS.md` mục "Pha 21"). Kiểm chứng trước (A1, không giả định):
  variation KHÔNG phải 1 thang kích thước thuần nhất/đơn điệu (chỉ 39/58
  base có >1 variation là có tín hiệu kích thước trong TÊN, và ngay cả khi
  có thì thứ tự variation không phải lúc nào cũng tăng theo kích thước) —
  nên bỏ hẳn việc parse tên, đo trực tiếp **kích thước glyph THẬT** từ font
  ISWA (`@sutton-signwriting/font-ttf`, cùng font `iswa_valid_combinations.json`
  đã dùng), chỉ so sánh TRONG cùng `(base_symbol_id, path_type)` — không
  bao giờ so giữa các base/dạng quỹ đạo khác nhau (đúng bẫy Phần 0). Mỗi
  nhóm anh em tự chuẩn hoá về trung bình 10.0 (giữ đúng thang cũ, không phá
  `SIGNBOX_TO_BODY_SCALE`) — trung bình toàn cục đo lại đúng 10,0000, lệch
  0% so ±20% cho phép.
- **4/4 — `plane`/`is_hit` suy SAI nguồn: ĐÃ XONG** (`PROGRESS.md` mục
  "Pha 22"). `plane` giờ ưu tiên tên BASE SYMBOL (`"floor plane"`/
  `"wall plane"`/`"diagonal"`), fallback tên GROUP chỉ khi tên base không
  nói gì (102/242) — sửa **11/242** base có `plane` sai (đo được, không
  phải 9 như brief nêu — 2 base thêm ở group 12 "Finger Movement", group
  brief coi là "không quy định plane" nhưng 2 base cụ thể đó lại có tên
  nói rõ plane). `is_hit` chuyển HẲN sang tên base, KHÔNG fallback nữa
  (từ khoá "Hit"/"Hits" luôn tường minh trong tên khi áp dụng) — sửa
  **13/242** base, đáng chú ý nhất là nguyên nhóm "Arm/Wrist/Finger
  Circle(s) Hits Wall" (group 20, Circles — group không có chữ "Hit" trong
  tên nên bị bỏ cờ hoàn toàn trước đây).

**Bài học chung rút ra sau cả 4 task (đúng yêu cầu ghi lại của task cuối,
Part D3):** kiểm tra xem MỘT nguồn có đang bị dùng để suy ra NHIỀU thứ khác
nhau không, trước khi tin nó. Ở đây: tên GROUP chỉ cho biết **mặt phẳng**
(Wall/Floor/Diagonal) và **có "hit" hay không** — nhưng chỉ đúng cho ĐA SỐ,
không phải MỌI base trong group (chính base bị ISWA đặt lệch group thường
lệ là nơi giả định "group nói đúng cho cả nhóm" sụp đổ); tên BASE SYMBOL
cho biết **dạng quỹ đạo** (Zigzag/Box/Corner/...) và, khi có, **plane
chính xác của riêng nó**; trường VARIATION cho biết **kích thước** (và đôi
khi hướng/số lần lặp). Framework ban đầu gộp tất cả vào MỘT nguồn (tên
group) rồi suy diễn — sai không phải vì tên group SAI, mà vì nó bị hỏi
những câu nó không trả lời được, VÀ vì "đa số đúng" bị lặng lẽ đối xử như
"luôn đúng". Thứ tự sửa 4 task theo đúng thứ tự "unlock" dữ liệu: task 1
mở khoá variation, task 2 dùng variation (gián tiếp, qua `base_symbol_id`)
+ tên base để tách `path_type` khỏi group, task 3 dùng cả `path_type` (đã
đúng) lẫn variation (đã có) để tách `amplitude` khỏi cả hai nguồn còn lại,
task 4 áp cùng nguyên tắc "ưu tiên tên base, group chỉ là fallback" cho 2
trường cuối cùng còn sót — đóng hoàn toàn chuỗi source-fidelity Category 2.

**Việc tiếp theo cho Category 2** (không còn trong chuỗi 4 task này, nêu ở
task cuối's brief Part D4): đo độ phủ THẬT bằng cách chạy toàn bộ corpus
qua pipeline (thay vì chỉ trích số brief), và làm nốt Category 6 (Location,
8 base)/7 (Punctuation, 5 base) để chốt 652/652 base symbol toàn ISWA (xem
mục "Các category ISWA" phía trên). `curvature`/`repeat` (tên base thật
nêu rõ Single/Double/Triple/Alternating nhưng chưa task nào dùng tới) vẫn
là cơ hội còn để ngỏ nếu có task sau muốn nhận.

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
- ✅ **MVP-2 (sign 2 tay, ~20,9%) — ĐÃ XONG (PROGRESS.md Pha 16).**
  `SignTimeline` dựng 1-2 track; chuyển động gán cho tay theo quy tắc
  arrowhead-fill CITED (`fill%3` = phải/trái/cả-hai — Lessons in SignWriting
  + SignWriter Studio Arrow Chooser, cài ở `timeline/classify.
  tracks_for_movement`). Còn ngoài phạm vi: 2 tư thế cùng-tay, >1 chuyển
  động/tay.
- ✅ **"2 tay đè nhau" — ĐÃ XONG cả 2 lớp.** Lớp 1 (Pha 17): `anchor()` ánh
  xạ signbox tới nửa-rộng-vai thay vì ±1 → 2 tay tách đúng vị trí. Lớp 2
  (Pha 18): `two_hand_closeup_pose` — close-up **2 tay cạnh nhau** (mỗi tay
  1 nửa khung, neo tâm bao-hình, 3/4 view) → thấy rõ từng handshape, hết
  nhoè. GIF `demo/mvp2_two_hand_closeup.gif`. Còn để ngỏ (nhỏ): chuyển động
  ngón đồng thời 2 tay trong close-up, và các tinh chỉnh thẩm mỹ khác.
- `DEFAULT_SIGN_DURATION` (0,8s) là hằng số giữ chỗ, chưa có nguồn dữ liệu
  thời gian thật (Category 3 Dynamics dự kiến bù việc này).
- `SIGNBOX_TO_BODY_SCALE` và phép ánh xạ toạ độ signbox → không gian cơ thể
  hiện là tuyến tính đơn giản, chưa hiệu chỉnh theo dữ liệu thật.

### Export sang `.pose` + video (bước 1-2) — ĐÃ XONG

**Lưu ý đánh số:** giống "SignTimeline (MVP-1)" ở trên, đây không có số Pha
riêng ở file này (không phải category-based) — trong `PROGRESS.md` việc này
là "Pha 5" theo trục thời gian làm việc (Pha 4 = Category 3 & 5).

**Việc đã làm:** gói mới `fsw_r/export/` + `fsw-r-viz/render_pose_video.py`
(KHÔNG sửa `core/` hay `timeline/` — xác nhận bằng `git diff --stat`), biến
`tuple[PoseFrame, ...]` thành video/GIF thật qua thư viện `pose-format`
(`==0.14.1`, pin chính xác) thay vì tự viết renderer — 3 lý do (topology
MediaPipe khớp sẵn với `hand_joint_poses.json`, không phải tự làm mesh/
skinning/camera, `.pose` là định dạng chung để so sánh với pose trích từ
video thật sau này) và độ dài đốt xương có trích nguồn thật (không phải số
đoán) đều ghi ở `PROGRESS.md` mục "Pha 5 — Tầng export". `demo/mvp1_sign.gif`
đã commit — video/GIF thật đầu tiên của dự án (trước đó chỉ có PNG sequence).

**Việc còn lại lúc đó (bước 3-4)** -- bước 3 (two-bone IK + thân tĩnh) ĐÃ
XONG, xem mục "Video ra hình người ký hiệu" ngay dưới "Tầng đánh giá". Bước
4 (nối Category 3) vẫn còn:
- Nối Category 3 (`DynamicsModifier.speed`) vào duration/frame count của
  video xuất ra — hiện mọi video vẫn dùng `DEFAULT_SIGN_DURATION` cố định
  (kế thừa từ MVP-1, chưa đổi).
- `save_video()` (MP4 thật, cần gói `vidgear` + ffmpeg) chưa từng chạy
  thành công trên máy hiện tại — mọi bằng chứng video hiện tại là GIF
  fallback (`save_gif()`, chỉ cần Pillow).

### Tầng đánh giá (FK accuracy + ràng buộc giải phẫu) — ĐÃ XONG

**Lưu ý đánh số:** cùng kiểu với "SignTimeline (MVP-1)"/"Export sang .pose"
ở trên — trong `PROGRESS.md` việc này là "Pha 6" theo trục thời gian làm
việc, không phải category-based.

**Vì sao làm trước khi làm IK/thân người:** framework chạy end-to-end từ
"Export .pose + video" nhưng chưa có con số đánh giá nào — task này đo
2 câu hỏi quyết định hướng đi: (1) vòng khứ hồi góc-khớp→FK mất mát bao
nhiêu, (2) vi phạm giới hạn giải phẫu ảnh hưởng thật đến đâu. Task ĐO,
không sửa `core/`/`timeline/`/`export/`.

**Kết quả (đầy đủ, kèm số liệu, xem `PROGRESS.md` mục "Pha 6"):**
- **MPJPE = 48,72** (thang chuẩn hoá size=150) — 261 tham số góc khớp
  thắng rõ 2 baseline bắt buộc (1 pose trung bình: 64,84; 1 pose/group:
  60,44) → kiến trúc góc khớp per-symbol có giá trị thật, nhưng sai số
  tuyệt đối không nhỏ.
- **Ngón cái là nguồn lỗi lớn nhất, rõ rệt** (MPJPE=80,29 so với 38,92-47,76
  của 4 ngón còn lại).
- Giả thuyết che khuất (C4: kỳ vọng ring>pinky>middle>index) — **không khớp**
  (đo được pinky>ring>index>middle).
- Tương quan vi phạm giải phẫu ↔ sai số FK (C3) — **gần như 0** (Pearson
  r=0,014) — 2 vấn đề KHÔNG cùng 1 nguồn gốc rõ ràng như giả thuyết ban đầu.
- Vi phạm giải phẫu: **224/261 (85,8%)**, đa số do ngón cái CMC — nghi vấn
  lệch định nghĩa khớp (xem `PROGRESS.md`), chưa xác minh.
- Sửa 1 bug thật trong `pose_format.utils.normalization_3d.PoseNormalizer`
  (pháp tuyến mặt phẳng có dấu mơ hồ, không idempotent) — nếu không tìm ra
  thì mọi số MPJPE ở trên vô nghĩa. Xem `PROGRESS.md` để biết chi tiết.

**Khuyến nghị (không tự đổi kiến trúc trong task này):** giữ kiến trúc góc
khớp; ưu tiên điều tra riêng ngón cái (định nghĩa `thumb.cmc` +
`export/bone_lengths.py`'s giả định hình học ngón cái) trước khi đầu tư IK
cánh tay — tránh khuếch đại lỗi có sẵn. **Cập nhật:** phần "làm IK cánh
tay" đã LÀM RỒI ngay sau task đo này (xem mục dưới đây).

**✅ Hiệu chỉnh hình học ngón cái — ĐÃ XONG (Pha 15).** Hai hằng số ngón cái
không nguồn (`_THUMB_BASE_OFFSET_MM`, `_THUMB_BASE_ROTATION`) đã được **fit
vào ground truth** trên tập held-out 70/30 phân tầng (seed 42) — origin mới
`FITTED`. Kết quả held-out (test): MPJPE **48,14 → 45,07 (6,4%, không
overfit)**; thumb per-finger **80,29 → 63,93**. **Không** đụng
`hand_joint_poses.json` hay góc khớp. Chi tiết + 4 số + baseline ở
`PROGRESS.md` mục "Pha 15", báo cáo `reports/fk_calibration.md` +
`reports/calibration_split.json`. **Hướng tiếp theo (theo brief, vì cải
thiện ≥5%): sang MVP-2 (2 tay) — ĐÃ LÀM (Pha 16).** Phần CÒN LẠI
của điều tra ngón cái (đối chiếu định nghĩa `thumb.cmc` của dataset với định
nghĩa lâm sàng CMC — nguồn nghi ngờ của 224/261 vi phạm giải phẫu) vẫn nằm
ở tầng GÓC KHỚP, tách biệt với hình học tái dựng vừa fit, và vẫn để ngỏ.

### Video ra hình người ký hiệu (scale + thân tĩnh + two-bone IK) — ĐÃ XONG

**Lưu ý đánh số:** cùng kiểu với các mục "ĐÃ XONG" không đánh category ở
trên — trong `PROGRESS.md` việc này là "Pha 7".

**Việc đã làm:** video trước đây chỉ có bàn tay (21/576 điểm, bàn tay
chiếm ~36% khung) — giờ có **thân + cánh tay two-bone IK nối vào bàn tay**
(21→35 điểm cho 1 sign MVP-1 thật). 2 phần, mỗi phần 1 commit riêng đúng
brief yêu cầu:
- **Phần A** (làm trước, rẻ nhất): hiệu chỉnh `BODY_UNITS_TO_PIXELS` (đo
  trực tiếp, không đoán) để bàn tay chiếm ~75% khung thay vì ~36%.
- **Phần B**: `export/body_geometry.py` (thân tĩnh, 4 tỉ lệ có trích nguồn
  thật — Drillis & Contini 1966 qua Winter's textbook Hình 4.1) +
  `export/arm_ik.py` (two-bone IK **nghiệm đóng lượng giác**, không dùng
  solver lặp/`scipy.optimize` — có test parse AST xác nhận).

**Phát hiện thật đáng chú ý (kiểm chứng bằng cách render+xem, không phải
đoán):** hiệu chỉnh `BODY_UNITS_TO_PIXELS` của Phần A (riêng cho bàn tay)
KHÔNG đủ cho cả người — bounding box thân+tay tràn khỏi khung 512px hơn 3
lần. Phải đo lại và thêm hằng số mới (`VERTICAL_CENTER_OFFSET`) để căn
giữa cả hình, không chỉ scale. Xem `PROGRESS.md` mục "Pha 7" để biết chi
tiết đầy đủ.

**Việc còn lại:**
- **Điều tra ngón cái** (đã nêu ở mục "Tầng đánh giá" phía trên) — vẫn
  chưa làm, vẫn là ưu tiên số 1.
- Nối `Category 5 BodyPose` vào tư thế thân (đang tĩnh, dùng hằng số riêng
  của `body_geometry.py`) — chờ `body_poses.json` có dữ liệu thật (hiện là
  placeholder).
- Nối Category 3 vào duration (bước 4 của "Export sang .pose + video", vẫn
  chưa làm — xem mục đó ở trên).
- `BODY_UNITS_TO_PIXELS`/`VERTICAL_CENTER_OFFSET` hiệu chỉnh trên đúng 1
  sign cụ thể — có thể cần đo lại nếu tỉ lệ nhân vật thay đổi (vd sau khi
  điều tra ngón cái, hoặc khi nối `BodyPose` thật).

### Thống nhất scale bàn tay ↔ thân người — ĐÃ XONG

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 8" (tiếp Pha 7).

**Việc đã làm:** bàn tay ở Pha 7 nhỏ bất tương xứng với thân vì
`bone_lengths.py` dùng số mm KHÔNG neo vào chiều cao nào, còn
`body_geometry.py` suy từ `ASSUMED_STATURE_MM`. Giờ **cả hai neo vào MỘT
chiều cao** qua module lá mới `export/anthropometry.py` (phá vòng import).
Bàn tay to lên đúng tỉ lệ nhân trắc (palm/shoulder 0,149 → 0,200) bằng cách
nhân ĐỒNG NHẤT 1 hệ số scale (giữ nguyên tỉ lệ tương đối giữa các đốt/ngón).
5 test bất biến mới (`test_hand_body_scale.py`), GIF thứ 4 đã commit.

**⚠️ Điểm mấu chốt — đây chỉ đổi scale TỔNG THỂ bàn tay, MPJPE KHÔNG được
đổi:** `validation/` chuẩn hoá mọi landmark qua `PoseNormalizer(size=150)`
TRƯỚC khi so sánh, tức khử scale tổng thể — nên scale đồng đều KHÔNG đổi
MPJPE (vẫn 48,72). Nếu MPJPE đổi thì nghĩa là hình dạng TƯƠNG ĐỐI trong bàn
tay đã bị đổi ngoài ý muốn: đúng như vậy đã xảy ra 1 lần khi
`_THUMB_BASE_OFFSET_MM` (điểm gắn ngón cái, hardcode trong
`forward_kinematics.py`) chưa được nhân hệ số scale — MPJPE lệch
48,72→48,74, đã bắt bằng cách chạy lại `eval_fk_accuracy.py` và sửa (nhân
`HAND_SCALE` cho offset). Bất kỳ thay đổi scale bàn tay nào sau này PHẢI
chạy lại eval để xác nhận `reports/fk_accuracy.md` không đổi.

**Việc còn lại:** như phần rederive metacarpal ngón cái đã nêu — palm của
bàn tay này ~0,43 chiều dài (không phải ~0,50 nhân trắc), nên `HAND_LENGTH_
TO_STATURE=0,1197` phải khít 3 bất biến; sửa triệt để cần rederive metacarpal
(sẽ đổi hình dạng tương đối ⇒ đổi MPJPE), nằm cùng nhóm với "điều tra ngón
cái" ở trên.

### Khung hình demo dễ đọc hơn (cắt ngang hông + thêm mắt) — ĐÃ XONG

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 9" (tiếp Pha 8).
Task nhỏ, thuần thẩm mỹ cho ảnh báo cáo — không đổi dữ liệu/tham số 3D,
không ảnh hưởng MPJPE.

**Việc đã làm:** `PoseVisualizer` vẽ thân (vai↔vai↔hông↔hông) thành 1 hình
thang đặc chiếm phần lớn khung hình (đúng topology `BODY_LIMBS` thật, không
phải bug) — che mất bàn tay là trọng tâm. Đã (1) ngừng xuất `LEFT_HIP`/
`RIGHT_HIP` (giữ nguyên `hip_position()`/`TORSO_LENGTH_MM` trong
`body_geometry.py`, chỉ không export ra `.pose`; xác nhận bằng cách đọc
thật source `PoseVisualizer._draw_frame()` rằng cạnh chỉ vẽ khi CẢ 2 đầu
có confidence > 0, rồi render lại để xác nhận bằng mắt), (2) hiệu chỉnh lại
`BODY_UNITS_TO_PIXELS` (56,0→94,0) và `VERTICAL_CENTER_OFFSET`
(-1,21→-0,22) theo bounding box đo thật sau khi cắt hông, (3) thêm 6 điểm
mắt (`static_eye_landmarks()`) neo theo `ASSUMED_STATURE_MM` (khác các
hằng số mũi/tai/miệng có sẵn, vẫn là mm phẳng chưa neo — điểm không nhất
quán đã ghi nhận, chưa sửa). Số điểm confidence > 0: 35→39. GIF thứ 5
(`mvp1_sign_5_readable_frame.gif`) đã render, xem lại bằng mắt, và commit.
Chi tiết đầy đủ ở `PROGRESS.md` mục "Pha 9".

**Quan sát trung thực (lúc đó không sửa, đánh giá "ngoài phạm vi task"):**
phóng to tỉ lệ + bỏ hình thang hông làm lộ rõ hơn 1 chỗ khuỷu tay phải
chúc xuống dưới đường vai-cổ tay — nguồn là hằng số pole-vector có sẵn
trong `arm_ik.py` (`POLE_DIRECTION_RIGHT`/`_LEFT`). **ĐÃ SỬA ở task tiếp
theo ("Sửa bug hướng xoay IK + chỉnh khung hình demo" ở dưới)** — hoá ra
đây không chỉ là hình học cũ bị phóng to như đánh giá ban đầu, mà là 1 bug
thật (hằng số pole sai tỉ lệ) từng bị hình thang hông che khuất trước đó.
Xem mục ngay dưới đây để biết chi tiết + bài học rút ra.

**Việc còn lại — 2 hạng mục ảnh chưa làm ở task này, cố ý ghi TODO (không
làm luôn vì mỗi việc không nhỏ):**
- **Thêm `FACE_LANDMARKS` thật (468 điểm MediaPipe)** — đầu hiện chỉ có
  mũi/tai/miệng/mắt tĩnh (`body_geometry.py`, không phải mesh mặt thật).
  Cần thiết kế cách map từ `FaceExpressionPose` (Category 4, đã có, nhóm
  khác phụ trách — blend-shape) sang 468 toạ độ tĩnh mà `PoseVisualizer`
  hiểu được — việc mới, không nhỏ, ngoài phạm vi task cắt-hông/thêm-mắt.
- **Mở rộng sang 2 tay** (MVP-2, ~20,9% sign thật cần ≥2 track — xem mục
  "MVP-2" ở trên) — video hiện chỉ có 1 tay (phải); cần logic phân biệt/
  gán track cho tay trái mà `SignTimeline` MVP-1 chưa viết.

### Sửa bug hướng xoay IK + chỉnh khung hình demo — ĐÃ XONG (phần elbow SAU ĐÓ PHÁT HIỆN SAI)

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 10" (tiếp Pha 9).
Task nhỏ, chỉ trong `export/` — không đổi dữ liệu, không ảnh hưởng MPJPE.

**⚠️ Cập nhật quan trọng:** phần hiệu chỉnh `POLE_DIRECTION_*` (Y=0) mô tả
dưới đây **ĐÃ ĐƯỢC PHÁT HIỆN LÀ SAI và ĐÃ REVERT** ở task tiếp theo ("Sửa
lại bất biến IK sai", mục ngay dưới) — nguyên nhân gốc không phải hằng số
pole tự nó sai, mà là bất biến TEST mà task này tự thêm (`test_c1`) có cận
dưới sai giải phẫu, khiến việc "sửa" pole theo hướng đó cũng sai theo. Phần
chỉnh khung hình (chiều rộng vai 81%→60%) vẫn ĐÚNG, không bị revert. Giữ
nguyên mục này làm bản ghi lịch sử trung thực (không xoá/viết lại) — xem
mục "Sửa lại bất biến IK sai" để biết chi tiết đầy đủ.

**Việc đã làm:** khuỷu tay phải (elbow) từng chúc xuống ~160px dưới CẢ vai
lẫn cổ tay ("tam giác nhọn chĩa xuống", về giải phẫu là cánh tay gập
ngược), và vai chiếm 81% chiều rộng khung. Đã điều tra chẩn đoán ban đầu
của brief (nghi ngờ bug DẤU trong bước xoay `Rotation.from_rotvec`) bằng
đại số (công thức Rodrigues) + kiểm chứng bằng số TRƯỚC KHI sửa bất cứ
gì — **xác nhận KHÔNG có bug dấu**, code cũ đã cho ra đúng kết quả. Nguyên
nhân thật: hằng số `POLE_DIRECTION_RIGHT`/`LEFT` có thành phần "xuống"
(Y) áp đảo, kết hợp với hình học đặc thù của project (cổ tay thường vươn
gần giữa thân trong khi vai nằm xa ở bên hông → góc gập lớn) khiến khuỷu
tay bị kéo xuống rất sâu. Đã hiệu chỉnh lại bằng đo đạc trên toàn bộ frame
thật của sign demo + 4 cấu hình biên (không đoán): Y=0 chính xác. Đồng
thời hiệu chỉnh lại `BODY_UNITS_TO_PIXELS` (94,0→69,8) theo chiều RỘNG VAI
(60%, trong khoảng 55-65%/50-70% brief yêu cầu) thay vì chiều cao như Pha
9. 6 test bất biến cấu hình cánh tay mới (`test_arm_configuration.py`, 29
case tham số hoá qua 4 cấu hình × 2 bên). GIF thứ 6
(`mvp1_sign_6_arm_ik_fix.gif`) đã render, xem lại bằng mắt (so sánh trực
tiếp với GIF trước-sửa), và commit. Chi tiết đầy đủ ở `PROGRESS.md` mục
"Pha 10".

**Bài học rút ra, ghi rõ theo đúng yêu cầu của task này:** toàn bộ 1.412
test đã có trước task này (bao gồm cả `test_arm_ik.py`'s C1/C2 riêng cho
`arm_ik.py`) đều PASS với khuỷu tay gập ngược — vì không test nào kiểm
tra CẤU HÌNH HỢP LÝ của kết quả IK, chỉ kiểm tra độ dài xương (bất biến
đúng ĐỘ LỚN) và tính đối xứng (bất biến đúng TƯƠNG QUAN 2 bên), cả 2 đều
giữ nguyên dù khuỷu tay ở bất kỳ đâu trên "vòng tròn" các vị trí hợp lệ về
mặt độ dài xương. **Độ dài xương + đối xứng là điều kiện CẦN nhưng không
ĐỦ để bắt lỗi cấu hình hình học** — cần thêm lớp test riêng kiểm tra vị
trí THỰC TẾ của điểm hình học mới (nằm trong khoảng hợp lý so với các điểm
lân cận, nghiêng đúng hướng mong đợi...), không chỉ các bất biến "nội tại"
(độ dài, đối xứng) không phụ thuộc vị trí tuyệt đối. Áp dụng cho mọi thành
phần hình học thêm mới sau này (vd nếu có Category 5 `BodyPose` thật thay
thân tĩnh, hay mở rộng 2 tay ở MVP-2): viết test bất biến CẤU HÌNH (vị trí
tương đối so với điểm neo, hướng nghiêng...) NGAY TỪ ĐẦU, không chờ tới
khi phát hiện bằng mắt sau khi đã commit.

### Sửa lại bất biến IK sai (hồi quy từ Pha 10) — ĐÃ XONG

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 11" (tiếp Pha 10).
Task rất nhỏ, chỉ đụng `export/arm_ik.py` + `tests/test_arm_configuration.py`
(cộng 2 file phụ thuộc dây chuyền do bounding box đổi lại).

**Việc đã làm:** Pha 10 tự thêm test `test_c1_elbow_stays_within_the_
shoulder_wrist_vertical_span`, ép khuỷu tay nằm trong khoảng dọc giữa vai
và cổ tay — CẢ cận trên lẫn cận dưới. Cận dưới sai về giải phẫu: khuỷu tay
buông thõng xuống dưới cả vai lẫn cổ tay khi giơ tay lên ngang vai là tư
thế TỰ NHIÊN đúng (hình chữ V), không phải lỗi. Để thoả cận dưới sai đó,
Pha 10 hiệu chỉnh `POLE_DIRECTION_RIGHT/LEFT` về `(∓0,15, 0,0, 1,0)`
(thành phần xuống = 0), vô tình làm phẳng cánh tay thành gần như 1 đường
ngang. Đã sửa: (1) bỏ cận dưới của `test_c1` (đổi tên thành
`test_c1_elbow_never_rises_above_both_shoulder_and_wrist`, chỉ còn cận
trên — khuỷu không được cao hơn CẢ vai lẫn cổ tay cùng lúc), (2) trả
`POLE_DIRECTION_RIGHT/LEFT` về giá trị gốc của Pha 9 (`(∓0,3, -1,0, 1,0)`)
— đã kiểm chứng lại (không giả định) với bất biến ĐÚNG trên cả 4 cấu hình
× 2 bên tay. Giữ nguyên công thức `cos(angle)*aim + sin(angle)*bend_direction`
của Pha 10 (không liên quan tới bug này) và `BODY_UNITS_TO_PIXELS=69,8`
(chiều rộng vai, không phụ thuộc pole direction). `VERTICAL_CENTER_OFFSET`
đo lại lần 3: 0,53 → -0,22 (quay gần về giá trị Pha 9, vì bounding box
body-space giờ gần như y hệt — chỉ pole đổi, hình học thân/đầu không đổi).
GIF thứ 7 (`mvp1_sign_7_elbow_invariant_fix.gif`) đã render, xem lại bằng
mắt (so sánh với cả GIF Pha 9 và Pha 10), và commit. Chi tiết đầy đủ ở
`PROGRESS.md` mục "Pha 11".

**Bài học rút ra (2 lớp, cả 2 đều đáng ghi):**
1. **Một test có thể khoá hành vi SAI, không chỉ "thiếu test" mới nguy
   hiểm.** Pha 10 nghĩ mình đang "thêm test bất biến hình học còn thiếu"
   (đúng tinh thần bài học của chính Pha 10 rút ra từ Pha 9) — nhưng bất
   biến TỰ NÓ sai (suy luận hình học trừu tượng "khuỷu nằm giữa 2 điểm neo"
   nghe hợp lý nhưng không khớp tư thế giải phẫu thật khi tay giơ cao). Một
   khi bất biến sai đã có test khoá lại, nó còn NGUY HIỂM HƠN không có test
   nào — tạo cảm giác an toàn giả (29 test pass!) và chủ động kéo việc hiệu
   chỉnh tiếp theo (`POLE_DIRECTION_*`) đi theo hướng sai, thay vì chỉ đơn
   giản là bỏ sót.
2. **Bất biến hình học phải kiểm chứng với TƯ THẾ THẬT trước khi đưa vào
   test**, không chỉ suy luận trừu tượng. Cách kiểm chứng đúng (đã áp dụng
   ở Pha 11): tự hỏi "người thật làm gì trong tư thế này" (giơ tay ký hiệu
   → khuỷu thõng xuống là bình thường) TRƯỚC khi viết assert, thay vì suy
   diễn thuần hình học rồi tin ngay. Áp dụng cho mọi thành phần hình học
   thêm mới sau này (Category 5 `BodyPose`, MVP-2 hai tay...).

### Video cận cảnh bàn tay (thấy rõ khớp ngón) — ĐÃ XONG

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 12" (tiếp Pha 11).
Task nhỏ, chỉ trong `fsw-r-viz/` — 0 file `fsw-r/src/fsw_r/` bị sửa.

**Việc đã làm:** video toàn thân không đọc được handshape (MCP cách nhau
8,4px, dưới độ dày nét 3px của `PoseVisualizer` ở khung 512×512 — công
thức độ dày tỉ lệ thuận với khung nên tăng độ phân giải không giúp gì).
Thêm video THỨ HAI (`render_hand_closeup.py`, file mới) thay vì sửa video
toàn thân (vẫn đang làm đúng việc show tư thế/quỹ đạo). Đo cả 2 chiến lược
phóng trước khi chọn: (a) fit bbox toàn quỹ đạo cổ tay (2,3×, MCP→19px) so
với (b) neo cổ tay + phóng theo kích thước RIÊNG của bàn tay (3,6×,
MCP→30px) — chọn (b) vì mục đích là đọc handshape, không phải xem quỹ đạo.
`HAND_CLOSEUP_TARGET_FRACTION=0,8` (hằng số có tên, không hardcode hệ số
phóng) tái tạo đúng hệ số 3,6× đo độc lập. `HAND_CLOSEUP_THICKNESS=2` chọn
sau khi so bằng mắt với mặc định 3px. Neo dọc tự tính từ khoảng trải thật
của bàn tay (không phải 1 hằng số phần trăm khung đoán thêm) — tự động đặt
cổ tay thấp hơn tâm khi ngón vươn 1 phía, đúng yêu cầu brief. 6 test bất
biến mới (`test_render_hand_closeup.py`). GIF thứ 8
(`mvp1_sign_8_hand_closeup.gif`) đã render, xem lại bằng mắt (index duỗi
thẳng tách biệt rõ 3 ngón nắm lại, đúng tiêu chí), và commit — video toàn
thân (`mvp1_sign_7_elbow_invariant_fix.gif`) xác nhận không đổi. Chi tiết
đầy đủ ở `PROGRESS.md` mục "Pha 12".

**Phát hiện phụ, ghi nhận trung thực (không sửa, ngoài phạm vi task):**
chỗ "gập" của 3 ngón cong lại (PIP→DIP→TIP) chủ yếu xảy ra theo trục Z
(chiều sâu), nên trong hình chiếu 2D (chỉ x,y, giống cách `PoseVisualizer`
luôn chiếu) không hiện rõ thành 1 góc khuỷu nhìn thấy được — chỉ hiện ra
là đoạn ngắn hơn ngón duỗi. Muốn thấy rõ GÓC GẬP theo đúng nghĩa đen cần
đổi góc camera của renderer — việc mới, không nhỏ, ngoài phạm vi task này
(xem "Việc còn lại" bên dưới).

**Việc còn lại — 2 hạng mục ảnh chưa làm, VẪN CHƯA LÀM ở task này (nhắc
lại từ mục "Khung hình demo dễ đọc hơn" phía trên, chưa có tiến triển
mới):**
- **Thêm `FACE_LANDMARKS` thật (468 điểm MediaPipe)** — đầu hiện chỉ có
  mũi/tai/miệng/mắt tĩnh (`body_geometry.py`, không phải mesh mặt thật).
  Cần thiết kế cách map từ `FaceExpressionPose` (Category 4, đã có, nhóm
  khác phụ trách — blend-shape) sang 468 toạ độ tĩnh mà `PoseVisualizer`
  hiểu được — việc mới, không nhỏ.
- **Mở rộng sang 2 tay** (MVP-2, ~20,9% sign thật cần ≥2 track — xem mục
  "MVP-2" ở trên) — video hiện chỉ có 1 tay (phải); cần logic phân biệt/
  gán track cho tay trái mà `SignTimeline` MVP-1 chưa viết. Ảnh hưởng cả
  video toàn thân LẪN video cận cảnh mới (cận cảnh hiện chỉ nhận 1 tham số
  `hand`, gọi 2 lần cho 2 tay là đủ về mặt code, nhưng chưa có sign thật 2
  tay nào để render thử).

### Chuyển động khớp ngón tay (Group 12 — Finger Movement) — ĐÃ XONG

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 13" (tiếp Pha 12).
**Khác các task gần đây: task này ĐƯỢC PHÉP sửa `core/` và `timeline/`**
— tính năng thật, không phải sửa lỗi tầng ngoài.

**Việc đã làm:** trước task này, `joint_pose` giống hệt nhau ở MỌI
keyframe của bất kỳ sign chuyển động nào — bàn tay là hình cứng bị kéo
dọc quỹ đạo, khớp ngón hoàn toàn đứng yên (đúng thiết kế MVP-1, không
phải bug, nhưng là giới hạn). Đồng thời phát hiện + sửa 1 bug ngữ nghĩa
có sẵn: `core/movement_paths.py` mô hình ISWA Group 12 ("Finger Movement")
thành CẢ BÀN TAY lắc qua lại trong không gian — sai; Group 12 nghĩa là
CÁC KHỚP NGÓN cử động, cổ tay đứng yên. Đã tra tên thật 5/20 base dẫn đầu
(76,1% token Group 12, corpus SignBank+) trên signbank.org TRƯỚC khi thiết
kế bảng dữ liệu (0x221 Hinge Up Down Large 38,2%, 0x225 Hinge Alternating
Large 16,0%, 0x216 Squeeze Large Single 8,9%, 0x21b Flick Large Single
7,9%, 0x222 Hinge Up Down Small 5,1%) — số valid fills/rotations mỗi
trang khớp chính xác bảng đo sẵn của brief, xác nhận đúng symbol.

Kiểu mới `FingerArticulation` (`core/types.py`, cạnh `MotionPath`) +
`data/finger_articulations.json` (20 entry, AUTHORED — không có dataset
nào ánh xạ tên ISWA finger-movement sang góc khớp số, giống
`dynamics_modifiers.json`/`body_poses.json`) + `core/finger_articulation.py`'s
`articulate_joint_pose()` (công thức `amplitude_deg·sin(2π·cycles·t+phase)`,
clamp bằng `JOINT_LIMITS` — IMPORT từ `validation/anatomical_limits.py`,
không sửa file đó). `FSWMotionRenderable` thêm
`get_finger_articulation() -> FingerArticulation | None` (bắt buộc mọi
Category 2 symbol, `None` cho 4/5 path_type còn lại — không tạo contract
riêng). `core/movement_paths.py`'s `PathType.FINGER` giờ trả 1 điểm cố
định (giống CONTACT) thay vì công thức lắc cũ. `timeline/build.py`: khi
có `FingerArticulation`, mỗi keyframe tính lại `joint_pose` theo đúng
`time` của nó — thay đổi DUY NHẤT; `sample.py` không cần sửa gì (nội suy
tuyến tính có sẵn giữa keyframe dày đặc tự biến chuỗi dao động thành
chuyển động mượt). 34 test mới (`test_finger_articulation.py`, D1-D6).
GIF thứ 9 (`mvp1_sign_9_finger_movement.gif`, Index + 0x221, qua pipeline
cận cảnh Pha 12) đã render, xem lại bằng mắt (sau khi tự bắt lỗi 1 lần
chọn nhầm frame preview bị "phách" trùng pha — xác nhận lại bằng số trước
khi kết luận), và commit. Chi tiết đầy đủ ở `PROGRESS.md` mục "Pha 13".

**Việc còn lại — nguồn chuyển động thứ hai cho khớp ngón, thuộc MVP-2,
CHƯA làm ở task này:** **nội suy handshape giữa hai ký hiệu tay cùng bên**
trong 1 sign — khi 1 sign có ≥2 symbol Category 1 (Hand) trên cùng 1 tay
(~12,8% sign thật theo số liệu corpus đã có sẵn — chưa tự đo lại độc lập
trong task này, chỉ ghi nhận làm việc tiếp theo), handshape đổi
theo thời gian (vd từ nắm sang duỗi) chính là 1 dạng chuyển động khớp
ngón THẬT SỰ — khác hẳn Group 12 (dao động quanh 1 handshape neo, biên độ
nhỏ) ở chỗ đây là chuyển tiếp HẲN giữa 2 tư thế tay khác nhau, biên độ
lớn hơn nhiều và không tuần hoàn. `SignTimeline` MVP-1 hiện chỉ hỗ trợ
đúng 1 symbol tay/sign (xem `timeline/build.py`'s `UnsupportedSignError`)
nên chưa thể làm — cần logic MVP-2 (gán/phân biệt nhiều symbol tay trên
cùng track) làm nền trước.
- **Hiệu chỉnh hằng số hình học bàn tay bằng ground truth** — MPJPE hiện
  tại (48,72, xem "Tầng đánh giá" ở trên) đo trên hằng số xương/khớp AUTHORED
  (ước lượng riêng, không phải đo trực tiếp — xem `export/bone_lengths.py`).
  Chưa có task nào quay lại HIỆU CHỈNH các hằng số đó bằng chính dữ liệu
  ground truth (3d-hands-benchmark) để giảm MPJPE xuống — Pha 6 chỉ ĐO,
  chưa SỬA (khuyến nghị ưu tiên số 1 vẫn là điều tra ngón cái, xem mục
  "Tầng đánh giá").

### Góc nhìn 3/4 cho video cận cảnh bàn tay — ĐÃ XONG

**Lưu ý đánh số:** trong `PROGRESS.md` việc này là "Pha 14" (tiếp Pha 13).
Task nhỏ, thuần tầng viz — **0 file `fsw-r/src/fsw_r/` bị sửa**.

**Việc đã làm:** GIF cận cảnh của Pha 13 cho thấy khớp ngón "co ngắn" thay
vì "gập" — `PoseVisualizer` chiếu trực giao lên mặt phẳng XY, trong khi đo
trực tiếp cho thấy chuyển động MCP thật (Group 12) nằm phần lớn ở Y VÀ Z
(đầu ngón giữa dịch X=0,000 Y=-0,458 Z=-0,207 body-space units giữa frame
7/13 của sign chuẩn) — Z bị bỏ hoàn toàn khi chiếu, cung tròn bị bẹp thành
đường thẳng. Đã thêm tham số `view_angle_deg` cho
`render_hand_closeup.py`, xoay landmark quanh trục Y TRƯỚC bước neo cổ
tay/phóng to có sẵn từ Pha 12 (đúng thứ tự yêu cầu — xoay trước rồi mới đo
bounding box để tính hệ số phóng). Đo đánh đổi thật bằng chính
implementation (không suy diễn từ bảng cho sẵn): góc tăng → biên độ gập
thấy được tăng, khoảng cách MCP tối thiểu giảm — chọn **60°**
(`HAND_CLOSEUP_VIEW_ANGLE_DEG`, MCP tối thiểu đo được 17,3px, còn margin
so với ngưỡng 15px; 90° tụt xuống 8,2px, dưới ngưỡng). GIF thứ 10
(`mvp1_sign_10_closeup_front.gif` 0°, `mvp1_sign_10_closeup_3q.gif` 60°)
đã render, xem lại bằng mắt — 60° cho thấy ngón trỏ ĐỔI HƯỚNG rõ ràng
(thẳng đứng → chéo lên-phải) giữa 2 frame cực trị, đúng là cung gập; 0°
chỉ cho thấy ngón NGẮN LẠI. Hai GIF khác nhau rõ rệt. Chi tiết đầy đủ ở
`PROGRESS.md` mục "Pha 14".

**Sự cố tự bắt được khi triển khai:** brief gợi ý đặt mặc định tham số
`view_angle_deg` = `HAND_CLOSEUP_VIEW_ANGLE_DEG` (60°) luôn — làm đúng vậy
thì HỎNG 3 test cũ của Pha 12 (lời gọi cũ không truyền góc ngầm nhận 60°
thay vì 0°, phá ngưỡng 20px cũ). Phát hiện qua chạy `pytest`, không phải
đoán trước — sửa lại: mặc định cả 3 hàm về `0.0` (khác gợi ý brief), giữ
hằng số 60° dùng tường minh đúng 1 chỗ gọi mới. Kết quả: mọi lời gọi cũ
(kể cả test Pha 12, kể cả `demo.py`'s 2 hàm render cũ) giữ nguyên hành vi
byte-for-byte — đúng yêu cầu "không đổi video cận cảnh 0° hiện có".

**Điểm đáng chú ý cho báo cáo:** `.pose` xuất ra giữ đủ 3 chiều không
gian thật, nhưng `PoseVisualizer` (renderer chuẩn của cộng đồng
`pose-format`) chỉ chiếu 2 chiều lên ảnh — dữ liệu 3D của project này
giàu hơn thứ công cụ hiển thị tiêu chuẩn khai thác được. Góc nhìn 3/4 là
cách làm lộ ra sự thật đó, không tính toán gì mới, chỉ "mượn" lại phần dữ
liệu Z vốn đã có sẵn.

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

**Thứ tự đề xuất tiếp theo** (cập nhật sau khi `SignTimeline` MVP-1, Category
3/5's tầng ký hiệu, tầng export bước 1-2, tầng đánh giá, VÀ video ra hình
người (thân tĩnh + two-bone IK) đều đã xong — xem mục "Video ra hình người
ký hiệu" ở trên). **Lưu ý:** thứ tự THỰC TẾ đã làm khác đề xuất trước đó — IK
cánh tay (mục 2 cũ) đã làm TRƯỚC khi điều tra ngón cái (mục 1 cũ), dùng thân
TĨNH (hằng số ước lượng riêng, không phải `BodyPose`) làm điểm neo tạm thời,
không phải vì đề xuất cũ sai mà vì đó là task được giao tiếp theo — ghi nhận
đúng thực tế, không sửa lại lịch sử:
1. **Điều tra riêng ngón cái** (KHÔNG phải "tầng validate giải phẫu" nói
   chung nữa — việc đó đã có `validation/anatomical_limits.py` + số đo thật
   từ Pha đánh giá) — MPJPE ngón cái (80,29) cao hơn hẳn 4 ngón còn lại
   (38,92-47,76), và 201/261 symbol vi phạm CMC (nghi lệch định nghĩa,
   chưa xác minh). Đối chiếu định nghĩa `thumb.cmc` của 3d-hands-benchmark
   với định nghĩa lâm sàng đã trích trong `anatomical_limits.py`, VÀ soát
   lại `export/bone_lengths.py`'s giả định hình học ngón cái
   (`_THUMB_BASE_OFFSET_MM`/`_THUMB_BASE_ROTATION`) — vẫn CHƯA làm, vẫn là
   ưu tiên hàng đầu (giờ còn thêm lý do: sai số ngón cái giờ sẽ khuếch đại
   qua cả cánh tay IK, vì elbow đã neo vào cổ tay — sửa ngón cái sau khi có
   IK vẫn tốt hơn không sửa, nhưng sửa CÀNG SỚM CÀNG RẺ vẫn đúng nguyên tắc
   cũ).
2. **Nối Category 3/5 vào `SignTimeline` VÀ export bước 4 (Category 3 vào
   duration)** — `DynamicsModifier.speed` thay `DEFAULT_SIGN_DURATION`'s
   hằng số giữ chỗ; `BodyPose` làm khung tham chiếu không gian thật cho
   `timeline/anchor.py` VÀ thay thế tư thế thân TĨNH hiện tại của
   `export/body_geometry.py` (hằng số ước lượng riêng, đo trên 1 sign cụ
   thể) bằng dữ liệu thật theo từng symbol Category 5 — cùng 1 dữ liệu
   (`BodyPose`) phục vụ cả 2 việc, nên làm chung 1 đợt hợp lý hơn tách
   riêng.
3. **MVP-2** (nới phạm vi `SignTimeline` lên sign có nhiều symbol tay/
   chuyển động hơn, ~20,9% sign đo trên SignBank+) — cần logic phân biệt/
   gán track chưa viết ở MVP-1, nên làm sau khi nền tảng (ngón cái +
   Dynamics/Body) đã vững.
4. **Category 6-7 (Location, Punctuation)** — xem Pha 6 dưới đây; category
   ISWA cuối cùng còn lại sau Pha 1-5.
5. **`save_video()` MP4 thật** (cài `vidgear` + ffmpeg thật vào môi trường
   chạy) — hiện mọi bằng chứng video là GIF fallback; việc phụ, không chặn
   gì (đã có bằng chứng động, chỉ là định dạng file).

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
