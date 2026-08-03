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

| Category | Range hex | Số symbol (ước tính theo range) | Bản chất dữ liệu |
|---|---|---|---|
| Hands | `0x100–0x204` | 261 base symbol (10 group theo số đếm ASL 1-10) | Joint angle (góc gập khớp ngón) + wrist orientation (quaternion) |
| Movement | `0x205–0x2f6` | 242 base symbol | Quỹ đạo chuyển động theo thời gian (đường thẳng/cong/vòng...) |
| Dynamics | `0x2f7–0x2fe` | 8 base symbol | Tốc độ/nhịp/độ nhấn của chuyển động (đi kèm Movement) |
| Head & Face | `0x2ff–0x36c` | ~110 base symbol | Biểu cảm mặt — blend-shape, KHÔNG phải joint-angle |
| Trunk | `0x36d–0x375` | 9 base symbol | Chuyển động thân người |
| Limb | `0x376–0x37e` | 9 base symbol | Vị trí/chuyển động tay-chân (không phải bàn tay) |
| Location | `0x37f–0x386` | 8 base symbol | Điểm chạm/vị trí trong không gian ký hiệu |
| Punctuation | `0x387–0x38b` | 5 base symbol | Dấu câu trong văn bản SignWriting |

(Số symbol ở trên là **base symbol** — tổng cộng 8 category = 652 base
symbol, khớp với `ranges.all = [0x100, 0x38b]` trong `fsw-structure.js`, và
gần đúng với con số "hơn 639 base symbol" hay thấy trích dẫn ở tài liệu
SignWriting công khai. **Category 1 Hands chỉ có 261/652 base symbol** —
KHÔNG PHẢI là con số ~639/652 tổng, đây là lỗi đã lỡ ghi nhầm trong
`fsw-r/README.md` và `PROGRESS.md` trước đó, cần sửa lại. Mỗi base symbol
còn nhân thêm với số `fill × rotation` hợp lệ của riêng nó (Hands: tối đa
6×16=96 biến thể/base symbol) — đây là nguồn gốc con số ISWA tổng ~37,000
symbol hay được trích dẫn.)

## Lộ trình theo pha

### Pha 1 — Hands (Category 1) — ĐANG LÀM

**Lưu ý thuật ngữ (dễ nhầm, đã nhầm 1 lần):** "Category" và "Group" là 2
tầng khác nhau trong ISWA, không dùng lẫn:
- **Category** = 1 trong 8 nhóm lớn của toàn ISWA (Hands, Movement,
  Dynamics, Head&Face, Trunk, Limb, Location, Punctuation) — bảng ở trên.
- **Group** = tầng con BÊN TRONG Category 1 (Hands), chia theo số đếm ASL
  1-10. Vd **Group 1 "Index Finger" = 14 base symbol** (`0x100–0x10d`),
  Group 2 "Index & Middle" = số khác, v.v. **Category 1 (Hands) = tổng cả
  10 group cộng lại = 261 base symbol**, không phải 14.

**Trạng thái hiện tại:** khung kiến trúc 4 tầng đã xong và test kỹ
(`FSWBaseSymbol` → `FSWRenderableSymbol` → `SymbolGroupN` → `BaseSymbolX`),
parse FSW thật qua `sutton-signwriting`, `rotation`/`fill` → quaternion 3D đã
xác nhận đúng qua chart gốc + test (kể cả bug gimbal-lock ở Floor Plane đã
tìm ra và sửa). **Cả 10/10 group Hands giờ đã có file code + ít nhất 1 base
symbol đăng ký thật** (tên lấy từ ảnh/HTML thật signwriting.org, không đoán):

| Group | Tên thật | Base symbol đã làm | Tổng base symbol group |
|---|---|---|---|
| 1 | Index Finger | 2/14 (Index, Index Bent) | 14 |
| 2 | Index & Middle Fingers | 1 (Index Middle) | 16 |
| 3 | Index, Middle, Thumb | 1 (Index Middle Thumb) | 38 |
| 4 | Four Fingers | 1 (Four Fingers) | 8 |
| 5 | Five Fingers | 1 (Five Fingers Spread) | 58 |
| 6 | Baby Finger | 1 (Index Middle Ring) | 30 |
| 7 | Ring Finger | 1 (Index Middle Baby) | 22 |
| 8 | Middle Finger | 1 (Index Ring Baby) | 19 |
| 9 | Index & Thumb | 1 (Middle Ring Baby) | 40 |
| 10 | Thumb | 1 (Thumb) | 16 |

Tổng: **11/261 base symbol** của Category 1. Lưu ý: với group 6-9, base
symbol số 1 KHÔNG phải là hình dạng đơn giản trùng tên group (vd group 6
"Baby Finger" nhưng base symbol 1 lại là "Index Middle Ring", không có
ngón út) — đã xác nhận bằng cách xem ảnh GIF thật của từng symbol trước khi
viết joint pose, không suy đoán từ tên group.

**Góc khớp của 11 base symbol đã làm giờ lấy từ dữ liệu thật** (không còn
đoán): `sign-language-processing/3d-hands-benchmark` — ảnh thật của 1 bàn
tay thật, 261 handshape × 6 góc, cộng pose 3D ước lượng sẵn bằng MediaPipe
(3 phiên bản, 48 lần chụp/symbol). Cách làm: map symbol_id ISWA → index
trong mảng `(48, 261, 6, 21, 3)` (thứ tự khớp `sorted(os.listdir(...))`
đúng bằng thứ tự group/base_symbol_number của mình — đã verify bằng cách
đọc script sinh dữ liệu gốc), lấy median qua 48 lần chụp, tính góc `flexion`
= góc giữa 2 vector xương liên tiếp (wrist→mcp, mcp→pip, pip→dip, dip→tip).
Đã cập nhật cả 11 file group + test tương ứng. Lưu ý quan trọng: đây là
**ước lượng của MediaPipe trên ảnh thật, không phải motion-capture đã xác
thực** (chính benchmark cũng không claim vậy) — nhưng đáng tin hơn nhiều so
với số tự đoán. `abduction` (độ xoè ngón) KHÔNG đo được bằng cách này, vẫn
là số đoán giữ nguyên từ baseline cũ.

**Việc còn lại của Pha 1:**
- [ ] Làm hết các base symbol còn lại trong mỗi group (vd Group 1 còn
      12/14, Group 5 còn 57/58...) — cùng pattern đã có, mỗi symbol giờ có
      thể lấy góc khớp thật ngay từ dataset trên (không cần đoán nữa), chỉ
      cần map đúng symbol_index rồi chạy lại cách tính đã có.
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

### Pha 2 — Movement (Category 2)

**Vì sao làm ngay sau Hands:** đây là thứ biến pose tĩnh thành "động tác"
(motion) — đúng nhu cầu ra clip 3D đã bàn trước đó. Không có Movement thì
mãi mãi chỉ demo được ảnh tĩnh.

**Thay đổi kiến trúc cần có:**
- `core/fsw_symbol_key.py` hiện **chỉ chấp nhận range Hands**
  (`0x100–0x204`, raise `ValueError` cho mọi range khác) — cần tổng quát
  hoá để nhận diện category từ base hex (dùng đủ bảng range ở trên), không
  chỉ validate riêng Hands.
- `core/registry.py` hiện map `(group, base_symbol_number) → class` với giả
  định ngầm là "Hands" — cần thêm `category` vào key của registry để không
  đụng độ với base_symbol_number của category khác.
- Cần kiểu dữ liệu MỚI hoàn toàn (không tái dùng `HandJointPose`): 1
  "motion path" — chuỗi điểm/keyframe theo thời gian, có hướng
  (thẳng/cong/vòng), tốc độ. Đây là điểm khác biệt lớn nhất so với Pha 1,
  vì Pha 1 chỉ có 1 pose tĩnh, Pha 2 bắt buộc phải có trục thời gian.
- Renderer (`HandMeshRenderer3D`) hiện chỉ gọi `apply_wrist_orientation` +
  `apply_joint_pose` 1 lần — cần renderer animation mới (interpolate giữa
  các keyframe theo thời gian), khác hẳn renderer tĩnh hiện tại.

### Pha 3 — Dynamics (Category 3)

Nhỏ (8 base symbol), đi kèm chặt với Movement (tốc độ/nhịp) — làm cùng lúc
hoặc ngay sau Pha 2, tái dùng phần lớn hạ tầng "motion path" của Pha 2.

### Pha 4 — Head & Face (Category 4)

**Khác biệt lớn:** không phải joint-angle (khớp xương) mà là **blend-shape**
(biểu cảm mặt: nhướng mày, chu miệng...). Cần thiết kế 1 hệ kiểu dữ liệu
hoàn toàn mới (`FaceExpressionPose` hay tương tự), không tái dùng được
`HandJointPose`/`FingerPose`. Renderer cũng cần thêm khả năng áp blend-shape
lên mesh mặt (không phải rig xương).

### Pha 5 — Trunk & Limb (Category 5-6)

Nhỏ (9+9 base symbol), mở rộng khung xương ra ngoài bàn tay (vai, thân,
chân/tay không phải bàn tay). Có thể tái dùng phần lớn kiểu tư duy
"joint-angle" của Pha 1 (vì đây cũng là khớp xương), chỉ khác bộ khớp.

### Pha 6 — Location & Punctuation (Category 7-8)

Nhỏ nhất (8+5 base symbol), mang tính bổ trợ:
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
