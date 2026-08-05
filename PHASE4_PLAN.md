# Pha 4 — Head & Face (Category 4): kế hoạch thực thi chi tiết

> Đây là bản kế hoạch chi tiết (execution plan) cho Pha 4, cụ thể hoá phần
> "Pha 4" trong `ROADMAP.md`. Nguồn dữ liệu cấu trúc đã xác minh từ nguồn
> thật (không đoán) — xem mục "Nguồn đã xác minh" ở cuối.

## 0. Bối cảnh & 2 phát hiện quyết định thiết kế

Category 4 (`0x2ff–0x36c`, **110 base symbol, 5 group 22–26**) **không phải
một mô hình đồng nhất**. Phân tích trên `data/iswa_valid_combinations.json`:

| Group | Tên thật | Range | #Base | rotation>0 | Bản chất |
|---|---|---|---|---|---|
| 22 | Head | 0x2ff–0x309 | 11 | **11/11** (tới 15) | Xoay cứng đầu (rigid) |
| 23 | Brow, Eyes, Eyegaze | 0x30a–0x329 | 32 | 9/32 | Blend-shape (9 = eyegaze có hướng) |
| 24 | Cheeks, Ears, Nose, Breath | 0x32a–0x33a | 17 | 2/17 | Blend-shape |
| 25 | Mouth, Lips | 0x33b–0x358 | 30 | **0/30** | Blend-shape thuần (27/30 fill nhị phân) |
| 26 | Tongue, Teeth, Chin, Neck | 0x359–0x36c | 20 | 8/20 | Hỗn hợp |

**Phát hiện 1 — hai kiểu dữ liệu khác nhau trong cùng category:**
- **Group 22 (Head)** = biến đổi cứng của đầu (quaternion), cấu trúc
  fill/rotation giống tay (6 fill × tới 16 rotation) → **tái dùng được**
  công thức orientation của Category 1.
- **Group 23–26 (biểu cảm)** = **blend-shape** (nhiều Action Unit cùng lúc),
  `fill` ở đây là "variation/mức độ" chứ KHÔNG phải "Six Palm Facings";
  `rotation` phần lớn = 0 (khi có = hướng, vd eyegaze).

**Phát hiện 2 — Category 4 phá vỡ contract cốt lõi hiện tại.**
`FSWRenderableSymbol.get_joint_pose() -> HandJointPose`
([`core/renderable_symbol.py`](fsw-r/src/fsw_r/core/renderable_symbol.py)) là
hand-specific; `FSWBaseSymbol.get_wrist_orientation()` cũng vậy. Một
`FaceSymbol` không thể implement 2 method này. Đây là thay đổi core lớn nhất
kể từ Pha 1 — và **Pha 2 (Movement) sẽ đụng đúng chỗ này**, nên dọn 1 lần,
dùng cho cả hai.

**Phát hiện 3 — không có dataset đo sẵn cho mặt.** Với tay có
`3d-hands-benchmark` (đo góc thật từ ảnh). Với mặt, các dataset tìm được
(SignAvatars, FePh, Polish-SL/Action-Units) **không keyed theo symbol
ISWA** → không trích xuất trực tiếp được. Pose mặt phải **biên soạn tay**
từ ý nghĩa symbol (SignWriting Alphabet Manual 2010 + chart signwriting.org),
rồi ánh xạ sang chuẩn blend-shape. **Đây là dữ liệu diễn giải, không phải đo
đạc — độ tin cậy thấp hơn tay, phải ghi rõ trong `_meta` và field `source`
mỗi entry** (đúng như đã làm với `abduction`).

**Chuẩn blend-shape đích:** **ARKit 52 blendshapes** (cũng là output của
MediaPipe FaceLandmarker, render thẳng được trong three.js/Blender) — đóng
vai trò "target khách quan" như 21 keypoint MediaPipe của tay. *Cần chốt
trước khi bắt đầu Bước 2 (xem "Quyết định cần chốt").*

---

## Nguyên tắc giữ nguyên xuyên suốt (kế thừa từ Pha 1)

1. `core/` phải category-agnostic: thêm category = **thêm code, không sửa
   hạ tầng chung**. `registry.py` dispatch theo `_CATEGORY_SYMBOL`.
2. Data-driven ngay từ đầu (bảng JSON + class generic), **không** lặp lại
   pattern "1 class Python / base symbol" đã bị bỏ ở Category 1.
3. Mỗi bước: `mypy --strict` sạch + `pytest` xanh + kiểm chứng
   hành vi/trực quan, **trước khi** sang bước sau. Commit riêng từng bước.
4. Domain knowledge (tên symbol, ý nghĩa fill/rotation) lấy từ nguồn thật,
   ghi rõ nguồn trong docstring/`_meta`. Không đoán.
5. Phân biệt rạch ròi dữ liệu **đo** (measured) và **biên soạn** (authored)
   trong `source` của mỗi entry.

---

## Bước 0 — Refactor contract (ĐIỀU KIỆN TIÊN QUYẾT, không thêm category)

**Mục tiêu:** gỡ tính hand-specific khỏi tầng chung để category phi-tay cắm
vào được. Bước này **không đổi hành vi** — Category 1 phải chạy y hệt.

### Trạng thái hiện tại
```
FSWBaseSymbol (ABC)
    base_hex/fill/rotation (+ validate theo iswa_data)
    category/group/base_symbol_number/symbol_id  (derived properties)
    hand_side: HandSide | None                   (abstract)
    _rotation_angle_degrees / _fill_facing_degrees / _fill_plane_degrees
    _default_wrist_orientation                    (công thức "Six Palm Facings")
    get_wrist_orientation()                        (abstract)   ← hand-specific
  └ FSWRenderableSymbol (ABC)
        get_joint_pose() -> HandJointPose          (abstract)   ← hand-specific
      └ HandSymbol
```

### Trạng thái đích
```
FSWBaseSymbol (ABC)                  ── chỉ giữ thứ MỌI category có
    base_hex/fill/rotation (+ validate)
    category/group/base_symbol_number/symbol_id  (derived)
    hand_side: HandSide | None                   (abstract, giữ nguyên)
    # BỎ get_wrist_orientation abstract; BỎ 4 helper fill/rotation→quaternion

WristOrientationMixin                ── MỚI (core/orientation.py)
    _rotation_angle_degrees / _fill_facing_degrees / _fill_plane_degrees
    _default_wrist_orientation()
    (chuyển nguyên văn từ FSWBaseSymbol, không đổi công thức)

FSWRenderableSymbol(FSWBaseSymbol, ABC)   ── marker rỗng: "symbol mà 1 renderer
                                              nào đó tiêu thụ được". KHÔNG khai
                                              báo pose method (pose là per-category).
  └ HandSymbol(FSWRenderableSymbol, WristOrientationMixin)
        get_joint_pose() -> HandJointPose
        get_wrist_orientation() -> Rotation   (dùng mixin)
        hand_side -> HandSide
        name
```

### Việc cụ thể
1. Tạo `core/orientation.py`: `class WristOrientationMixin` chứa 4 helper +
   `_default_wrist_orientation()` (copy nguyên từ `fsw_base_symbol.py`,
   giữ nguyên docstring giải thích gimbal-lock/thứ tự composition).
2. `core/fsw_base_symbol.py`: xoá 4 helper + `_default_wrist_orientation` +
   `get_wrist_orientation` abstract. Giữ lại `hand_side` abstract và mọi
   derived property. Cập nhật docstring module (bỏ phần "Six Palm Facings"
   mô tả — chuyển sang docstring của mixin/HandSymbol).
3. `core/renderable_symbol.py`: `FSWRenderableSymbol` bỏ `get_joint_pose`,
   thành marker ABC. Docstring: pose accessor là per-category.
4. `core/hand_symbol.py`: `HandSymbol(FSWRenderableSymbol, WristOrientationMixin)`;
   `get_wrist_orientation()` gọi `self._default_wrist_orientation()` (không đổi).
5. `core/renderer.py`: `HandMeshRenderer3D.render(symbol: HandSymbol)` —
   thu hẹp kiểu từ `FSWRenderableSymbol`. `hand_side` giờ là `HandSide`
   (không None) → nhánh guard None thành thừa; giữ lại 1 comment giải thích
   hoặc bỏ (tuỳ, không ảnh hưởng hành vi vì Category 1 không bao giờ None).
6. `fsw-r-viz/.../plot_hand.py`: đổi annotation `FSWRenderableSymbol` →
   `HandSymbol` (vì nó gọi `get_joint_pose()`). Import từ
   `fsw_r.core.hand_symbol`.

### Kiểm chứng Bước 0 (bắt buộc trước khi qua Bước 1)
- `cd fsw-r && mypy --strict` sạch.
- `pytest` = **615/615** như cũ (không giảm — không đổi hành vi).
- `cd fsw-r-viz && mypy --strict` sạch + `pytest` 5/5.
- `python -m fsw_r_viz.demo` → 2 ảnh PNG **byte-for-byte giống hệt** trước
  refactor (so bằng `git diff --stat`/hash). Đây là bằng chứng công thức
  không đổi.

---

## Bước 1 — Group 22 (Head): beat "rigid transform", ít rủi ro nhất

**Vì sao làm trước:** chỉ 11 symbol; bản chất là xoay cứng → tái dùng nhiều
nhất từ Pha 1; chứng minh pipeline Category 4 chạy end-to-end (parse →
registry dispatch → render) trước khi đụng blend-shape.

### Thiết kế
- Kiểu pose: **`Rotation` (quaternion)** — không cần kiểu mới. Đầu nghiêng/
  quay là orientation thuần.
- `core/head_symbol.py`: `HeadSymbol(FSWRenderableSymbol, WristOrientationMixin)`
  - `get_head_orientation() -> Rotation`: **giả thuyết khởi đầu** =
    `self._default_wrist_orientation()` (công thức fill/rotation của tay).
    **PHẢI verify** trên chart Head thật (fill/rotation của đầu có thể mang
    nghĩa khác — vd fill = đầu nghiêng trước/sau thay vì Palm/Side/Back).
    Nếu khác → viết `_default_head_orientation()` riêng, khoá bằng test cụ
    thể (vd "rotation=4 → đầu chúc xuống").
  - `hand_side -> None` (đầu không phải tay; mirror trái/phải đã nằm trong
    orientation, không dùng `hand_side`).
- `core/registry.py`: thêm dispatch category 4 (xem "Registry dispatch" bên
  dưới) — nhánh group 22 → `HeadSymbol`.
- Dữ liệu: kiểm tra từng chart xem 11 symbol có cần bảng per-symbol không
  (vd "head" vs "forehead" vs "head tilting" là các glyph khác nhau). Nếu
  chỉ khác orientation → không cần JSON. Nếu khác semantic → `data/head_symbols.json`
  (11 entry: `base_hex → {name, ...}`), tên lấy từ chart (không đoán).

### Kiểm chứng Bước 1
- `symbol_from_fsw("<key Head thật>")` ra `HeadSymbol` đúng.
- `mypy --strict` sạch + test mới cho HeadSymbol (dựng object, orientation
  đổi theo rotation, hand_side=None).
- Render trực quan trong `fsw-r-viz` (renderer đầu tối giản — mesh/marker
  đầu áp orientation) so bằng mắt với chart Head.

---

## Bước 2 — `FaceExpressionPose` + `FaceSymbol` + Group 25 (Mouth) + viz mặt

**Vì sao Mouth trước:** đơn giản nhất — 0/30 rotation, 27/30 chỉ fill∈{0,1}
→ validate schema/renderer trên tập rõ nghĩa, ít biến.

### Kiểu dữ liệu mới (`core/types.py` hoặc `core/face_types.py`)
```python
@dataclass(frozen=True)
class FaceExpressionPose:
    # ARKit-52 blendshape name -> hệ số 0.0..1.0. Chỉ liệt kê blendshape
    # khác 0 (mặc định 0). Vd {"mouthSmileLeft": 0.8, "mouthSmileRight": 0.8}.
    blendshapes: Mapping[str, float]
```

### Điểm khác cấu trúc quan trọng so với tay
Ở tay, `fill` chỉ đổi wrist orientation (công thức), **joint pose độc lập
với fill**. Ở mặt, **`fill` đổi chính biểu cảm** (fill=0 vs fill=1 = 2
trạng thái miệng khác nhau). → pose phụ thuộc **(base_hex, fill)**, không
chỉ base_hex.

**Giải pháp giữ `PoseTable` generic:** value type của bảng mặt là
`Mapping[int, FaceExpressionPose]` (fill → pose). `FaceSymbol.get_expression()`
tra `TABLE[self.base_hex][self.fill]`. `PoseTable[Mapping[int, FaceExpressionPose]]`
— thân class `PoseTable` không đổi.

### Class & bảng
- `FaceSymbol(FSWRenderableSymbol)`:
  - `get_expression() -> FaceExpressionPose` = `FACE_POSE_TABLE[self.base_hex][self.fill]`.
  - `hand_side -> None`.
  - (rotation cho mặt: Mouth luôn 0; group 23 eyegaze dùng rotation làm
    hướng — để Bước 3, thiết kế `get_expression` không phụ thuộc rotation ở
    Bước 2.)
- `core/face_pose_table.py`: `FACE_POSE_TABLE = PoseTable[...]("face_expression_poses.json", parse, expected_count=...)`.
- `data/face_expression_poses.json`: khoá top-level `base_hex` (hex string);
  mỗi entry `{name, symbol_id, source, fills: {"0": {blendshapes...}, "1": {...}}}`.

### Registry
- Nhánh category 4, group ≠ 22 → `FaceSymbol`.

### Renderer mặt (fsw-r-viz) — làm CÙNG Bước 2 để verify được
- `fsw-r-viz`: renderer mặt tối giản — vẽ 52 (hoặc tập con) landmark/mesh
  mặt neutral rồi dịch chuyển theo blendshape, hoặc bảng "blendshape → mô tả
  điểm" đơn giản. Mục tiêu: **sanity-check bằng mắt** so với chart, tương
  đương stick-figure của tay. Không cần mesh đẹp.
- Dispatch render: thêm `render(symbol)` cấp cao ở `fsw-r-viz` phân nhánh
  `isinstance(symbol, HandSymbol|HeadSymbol|FaceSymbol)` → renderer tương
  ứng. `core/` không đổi.

### Kiểm chứng Bước 2
- Dựng `FaceSymbol` cho vài mouth symbol, `get_expression()` ra đúng
  blendshape đã author; đổi fill → đổi biểu cảm.
- `mypy --strict` sạch + test (bảng đủ entry, blendshape trong [0,1],
  round-trip `symbol_from_fsw`).
- Render vài mouth (fill 0 vs 1) so bằng mắt với chart signwriting.org.

---

## Bước 3 — Group 23, 24, 26 (biên soạn hàng loạt)

- **Script bán tự động** (kiểu `scripts/gen_group.py` của tay) để lấy **tên
  thật** từng symbol từ chart (regex `<title>`/nguồn thật, không đoán) và
  sinh khung entry JSON. **Khác tay:** giá trị blendshape **phải author
  tay** từ Manual/chart — không có nguồn tự động như `.npy` của tay. Script
  chỉ sinh khung + tên, người điền hệ số blendshape.
- **Group 23 (Brow/Eyes/Eyegaze):** 9 symbol có rotation → rotation = hướng
  nhìn (eyegaze). Mở rộng `FaceSymbol.get_expression()` để với các base này,
  rotation ánh xạ sang blendshape hướng mắt (`eyeLookIn/Out/Up/Down...`).
  Khoá bằng test ("rotation=X → mắt nhìn hướng Y").
- **Group 24, 26:** author như Group 25; Group 26 có 8/20 rotation (chin/neck
  nghiêng) — cân nhắc phần "neck tilt" gần với rigid của Head (có thể tách
  nhánh nhỏ), xem "Rủi ro".
- Làm từ group nhỏ → lớn (24: 17 → 26: 20 → 23: 32) để lộ lỗi sớm; mỗi
  group xong: `mypy` sạch + test group xanh trước khi sang group kế.

---

## Registry dispatch cho Category 4 (precise)

Category 4 map tới **2 class** (HeadSymbol/FaceSymbol) tuỳ group → dùng 1
factory, vẫn là **đúng 1 entry** trong `_CATEGORY_SYMBOL`:

```python
# core/registry.py
from fsw_r.core.iswa_data import group_of
from fsw_r.core.head_symbol import HeadSymbol
from fsw_r.core.face_symbol import FaceSymbol

def _make_category4(base_hex: int, fill: int, rotation: int) -> FSWRenderableSymbol:
    if group_of(base_hex) == 22:                 # Head = rigid orientation
        return HeadSymbol(base_hex=base_hex, fill=fill, rotation=rotation)
    return FaceSymbol(base_hex=base_hex, fill=fill, rotation=rotation)  # 23-26 = blend-shape

_CATEGORY_SYMBOL: dict[int, _Constructor] = {1: HandSymbol, 4: _make_category4}
```

Không sửa gì khác trong `registry.py`. `fsw_symbol_key.py` đã parse được
range Category 4 sẵn (chấp nhận `0x100–0x38b`) — không cần đụng.

---

## Schema JSON đề xuất (`data/face_expression_poses.json`)

```json
{
  "_meta": {
    "source": "SignWriting Alphabet Manual 2010 + per-symbol charts (signwriting.org)",
    "method": "AUTHORED, not measured — each blendshape vector is a human interpretation of the symbol's documented meaning, mapped to ARKit-52 blendshapes. Unlike hand_joint_poses.json (MediaPipe-measured), there is no source dataset keyed to ISWA face symbols.",
    "blendshape_standard": "ARKit 52",
    "total_entries": 0
  },
  "33b": {
    "symbol_id": "04-25-001",
    "name": "<tên thật từ chart>",
    "source": "authored from Manual 2010 chart 04-25-001",
    "fills": {
      "0": {"mouthClose": 0.0, "...": 0.0},
      "1": {"jawOpen": 0.4, "...": 0.0}
    }
  }
}
```

---

## Thứ tự & phụ thuộc

```
Bước 0 (refactor contract)  ── tiên quyết cho tất cả
   ├─► Bước 1 (Head, group 22)         [rigid, ít rủi ro, chứng minh pipeline]
   └─► Bước 2 (FaceExpressionPose +
               FaceSymbol + Mouth + viz mặt)   [blend-shape type + renderer]
                 └─► Bước 3 (group 23/24/26 biên soạn hàng loạt)
```

Bước 1 và Bước 2 độc lập nhau (đều chỉ cần Bước 0) — có thể làm song song
hoặc Head trước cho thắng nhanh.

---

## Quyết định cần chốt TRƯỚC khi code (cần domain/bạn)

1. **Chuẩn blend-shape:** ARKit 52 (đề xuất, render thẳng three.js/Blender)
   hay FACS Action Units? → quyết định kiểu `FaceExpressionPose`.
2. **Group 22 (Head) — orientation-only hay cần bảng per-symbol?** Phụ thuộc
   vào 11 chart: các glyph có khác nhau về semantic không, hay chỉ khác
   orientation. → đọc 11 chart trước khi code Bước 1.
3. **Ý nghĩa `fill` cho từng nhóm mặt** (nhất là fill nhị phân của Mouth):
   phải đối chiếu **SignWriting Alphabet Manual 2010** trước khi author —
   ROADMAP đã cảnh báo "công thức fill/rotation khác nhau giữa các category,
   thậm chí giữa các nhóm base".

## Rủi ro / điều chưa chắc

- **Không có ground-truth đo được cho mặt** → không "verify bằng dataset"
  như tay. Cách kiểm chứng duy nhất: render blend-shape rồi **so bằng mắt
  với chart thật** từng symbol (giống cách bắt bug gimbal-lock ở Category 1).
  Chấp nhận độ tin cậy thấp hơn, ghi rõ trong `_meta`.
- **Group 22 (Head) vs Pha 5 (Trunk/Neck) có thể chồng lấn** — "neck tilt"
  (group 26) và "head tilt" (group 22) đều là xoay quanh cổ. Khi làm Pha 5
  cần rà lại để không mô hình 2 lần.
- **`fill` mặt đổi chính biểu cảm** (khác tay) → bảng khoá theo (base_hex,
  fill); nếu sau này phát hiện rotation cũng đổi biểu cảm ở vài base (ngoài
  eyegaze) thì phải mở rộng khoá — đã dự phòng bằng cách để `get_expression`
  đọc cả `self.fill`/`self.rotation` từ đầu.
- **Head orientation formula** giả định tái dùng công thức tay — chưa verify;
  có thể phải viết riêng.

## Nguồn đã xác minh

- Cấu trúc category/group: `@sutton-signwriting/core` `fsw-structure.js`
  (`category`/`group` array) — đã có trong `core/iswa_data.py`.
- Tên group 22–26: các trang `signwriting.org/lessons/iswa/group22..26/`.
- Số fill/rotation hợp lệ: `data/iswa_valid_combinations.json` (font TTF thật).
- Ý nghĩa symbol (để author blend-shape): SignWriting Alphabet Manual 2010
  (`signwriting.org/archive/docs7/sw0636_...pdf`) + chart từng symbol.
- Chuẩn blend-shape đích: ARKit 52 / MediaPipe FaceLandmarker.
- Khảo sát dataset mặt (kết luận: không có bản keyed theo ISWA): SignAvatars,
  FePh, Polish-SL Action Units.
```
