# Kiểm chứng nguồn dữ liệu — hồ sơ bằng chứng (đã đóng)

> **TRẠNG THÁI: TẤT CẢ ĐÃ ĐÓNG (2026-08-15).** Tài liệu này giữ lại vì hai lý do:
> nó là **hồ sơ bằng chứng** cho phần source-fidelity của paper, và
> `scripts/check_symbol_id_provenance.py` giờ là **regression check** giữ cho
> các lỗi này không quay lại.
>
> | Lỗi | Trường | Trạng thái | Commit |
> |---|---|---|---|
> | #3 | `symbol_id` | ✅ đã sửa | `c253ecb` (1/4) |
> | #1 | `path_type` | ✅ đã sửa — 5 → 22 giá trị, theo tên per-symbol | `c69134d` (2/4) |
> | #2 | `amplitude` | ✅ đã sửa — 1 → 142 giá trị, mean 10.0 | `1be78d4` (3/4) |
> | #1 | `plane` / `is_hit` | ✅ đã sửa — 11 `plane` + 13 `is_hit` | `182449a` (4/4) |
>
> Chạy `python scripts/check_symbol_id_provenance.py` trên dữ liệu hiện tại:
> mục [1] tự đo và báo **"NOT collapsed … path_type is FIXED"**; mục [2] `plane`
> **0 mâu thuẫn**; mục [3] `is_hit` **0/242**; mục [4] **0 symbol**.
>
> Hai ghi chú để không ai hiểu nhầm khi trích vào paper:
>
> 1. Số **11** ca `plane` (không phải 9 như audit này nêu ban đầu) là đúng — bản
>    fix áp quy tắc cho cả group 12, bắt thêm `0x228`/`0x229`, vốn được audit này
>    xếp vào nhóm "tên nói rõ plane nhưng lưu null" thay vì "mâu thuẫn".
> 2. Còn **2 ca** `0x2ed`/`0x2ee` ("Wrist Circle **Front Wall**") vẫn lưu `null`
>    vì luật khớp `"wall plane"`, không khớp `"front wall"`. Render vẫn đúng
>    (fallback là WALL), nên đây là vết xước ở giá trị lưu, không phải lỗi giá trị.

Paper claim từ điển được dựng **"từ nguồn ISWA chuẩn"**. Đồng đội phát hiện một
**LỚP lỗi chung**: *dùng nguồn thô/gộp trong khi nguồn chính xác per-symbol nằm
ngay đó và đã là dependency sẵn có của project*.

Tài liệu này là **bằng chứng chạy được**, không phải bản fix. Script không sửa
một byte dữ liệu nào.

> **Đọc phần dưới ở thì quá khứ.** Mọi số đo từ đây trở xuống là **trạng thái
> TRƯỚC khi sửa** — đó chính là bằng chứng. Trạng thái hiện tại nằm ở bảng đầu
> trang: cả 4 đã đóng. Chạy lại script bất cứ lúc nào để xác nhận.

```
cd fsw-r
python scripts/check_symbol_id_provenance.py            # cả 3 lỗi
python scripts/check_symbol_id_provenance.py --bug 1    # từng lỗi
```

Cần mạng: `npm pack` (`@sutton-signwriting/core`, `@sutton-signwriting/font-ttf`)
+ signbank.org — đúng cơ chế nguồn tái lập được mà
`scripts/gen_valid_combinations.py` đã dùng.

| Lỗi | Trường | Nguồn đang dùng | Nguồn ĐÚNG (đã có sẵn) | Loại |
|---|---|---|---|---|
| #1 | `path_type` / `plane` / `is_hit` | tên **GROUP** | tên per-symbol + trường base/variation của Symbol ID (signbank ISWA 2010) | **dữ liệu SAI** |
| #2 | `amplitude` | hằng số `10.0` | kích thước glyph trong font Sutton | **dữ liệu SAI** |
| #3 | `symbol_id` | `GROUP_START` tự dựng lại | `symidArr` của `@sutton-signwriting/core` | quy ước hiển thị |

---

## Kiểm tra tính toàn vẹn (điều kiện tiên quyết)

Trước khi so sánh bất cứ thứ gì, script xác nhận tên lấy từ signbank khớp đúng
symbol nào:

```
signbank names fetched: 242  |  missing: 0  |  Symbol ID disagreements with symidArr: 0
```

**242/242 tên lấy được, 0 bất đồng** giữa Symbol ID của signbank và `symidArr`
canonical. Nên các so sánh bên dưới là so đúng tên với đúng symbol.

---

## Lỗi #1 — `path_type`/`plane`/`is_hit` lấy từ tên GROUP

`scripts/gen_movement_paths.py` có bảng `_GROUP_TABLE` đúng **10 dòng**, mỗi
group 1 dòng, rồi gán y hệt cho **mọi** base symbol trong group đó
([gen_movement_paths.py:50-61](fsw-r/scripts/gen_movement_paths.py#L50-L61)).

### [1] Mức độ gộp — thuần cấu trúc, không cần đọc tên

Lấy thẳng từ trường base của Symbol ID (`CC-GG-BBB-VV`), không diễn giải gì:

```
ISWA phân biệt 129 SYMBOL riêng biệt trên 242 base hex,
nhưng path_type chỉ có 5 giá trị, mỗi group 1 giá trị.

 group  #bases   #ISWA symbols    stored path_type
     1      17              17             contact
     2      20              13              finger
     3      43              20            straight
     4      16               4            straight
     5      35              19            straight
     6      30              11              curved
     7      17              15              curved
     8      30              14              curved
     9      14               8              curved
    10      20               8              circle
```

Group 3 (tên "Straight Wall Plane") gộp **20 symbol ISWA khác nhau** thành 1
`path_type=straight`.

### [2] `plane` — bị chính TÊN của symbol phủ định

**9 symbol mâu thuẫn thẳng** (tên nói plane này, dữ liệu ghi plane kia):

| base | tên ISWA thật | tên nói | đang lưu |
|---|---|---|---|
| `0x24e` | Travel Rotation, Single **Floor Plane** | floor | `wall` |
| `0x24f` | Travel Rotation, Double **Floor Plane** | floor | `wall` |
| `0x250` | Travel Rotation, Alternating **Floor Plane** | floor | `wall` |
| `0x284` | Travel Rotation Single **Wall Plane** | wall | `floor` |
| `0x285` | Travel Rotation Double **Wall Plane** | wall | `floor` |
| `0x286` | Travel Rotation Alternating **Wall Plane** | wall | `floor` |
| `0x2b4-0x2b6` | Wave **Diagonal** Path Small/Medium/Large | diagonal | `wall` |

Thêm **4 symbol** tên nói rõ plane nhưng đang lưu `null` — chính là 4 trong số
những chỗ `core/movement_paths.py` phải fallback về WALL: `0x228`/`0x229`
("Finger Contact Movement, **Wall/Floor Plane**"), `0x2ed`/`0x2ee` ("Wrist
Circle **Front Wall** Single/Double").

> Đây là điểm **mở rộng** so với cách đồng đội mô tả lỗi (chỉ nói `path_type`):
> `plane` và `is_hit` dính đúng cùng một lỗi, và **chứng minh được mà không cần
> diễn giải hình học nào** — chỉ so chữ trong tên chính thức của symbol.

### [3] `is_hit` — sai 13/242, sai cả hai chiều

- **10 symbol tên có "Hits" nhưng lưu `is_hit=False`** — toàn bộ nằm ở group 10
  ("Circles", bảng gán `False` cho cả group): `Arm Circle **Hits** Wall`
  (6 symbol), `Wrist Circle **Hits** Wall` (2), `Finger Circles **Hits** Wall` (2).
- **3 symbol lưu `is_hit=True` nhưng tên không hề có "Hits"** — `Wave Diagonal
  Path Small/Medium/Large`, chỉ vì chúng nằm trong group 7 ("Curves Hit Wall
  Plane").

### [4] `path_type` — 15 symbol "straight" mà tên nói hình phi thẳng

*(Mục này ILLUSTRATIVE: nó đọc từ chỉ hình dạng nên là một diễn giải, khác [2]
và [3].)* Ví dụ: `Zigzag, Wall Plane Small/Medium/Large`, `Peaks, Wall Plane
Small/Medium/Large`, `Travel Arm Spiral, Wall Plane Single/Double/Triple`,
`Zigzag, Floor Plane ...` — tất cả đang là `path_type='straight'`.

Đây đúng là ví dụ "Zigzag = straight" mà đồng đội nêu, nay có base hex cụ thể.

---

## Lỗi #2 — `amplitude` là 1 hằng số; font ISWA có kích thước thật

`_DEFAULT_AMPLITUDE = 10.0`
([gen_movement_paths.py:64](fsw-r/scripts/gen_movement_paths.py#L64)).
`amplitude` không phải trường trang trí — nó chính là **độ dài quỹ đạo** trong
`core/movement_paths.py::_canonical_shape()`, nên hằng số này = *mọi chuyển
động trong Category 2 đi cùng một quãng đường*.

```
[1] STORED amplitude: 10.0 -- 242 symbols (100%)

[2] MEASURED glyph size (SuttonSignWritingLine.ttf, Version 1.1.0):
      bases measured: 242/242
      distinct sizes: 210
      min     84.9 font units -- 0x21c 'Flick Small Single'
      max    658.7 font units -- 0x2b6 'Wave Diagonal Path Large'
      spread: 7.76x
```

**ISWA viết độ lớn chuyển động THẲNG VÀO glyph** — "... Small / Medium / Large
/ Largest" là 4 base symbol riêng biệt được vẽ ở 4 kích thước. Toàn bộ dải
7,76× đó đang bị xoá bằng 1 hằng số.

### Chéo kiểm: 2 nguồn độc lập khớp nhau 50/50

Với mỗi nhóm symbol có tên ISWA **giống hệt nhau trừ đúng chữ chỉ cỡ**, glyph
trong font có to dần đúng theo thứ tự tên nói không?

```
comparable series: 50
strictly increasing with the name's size word: 50
violations: 0
```

Ví dụ (cả 4 hiện đều là `amplitude=10.0`):

| base | glyph (font units) | tên ISWA |
|---|---|---|
| `0x22a` | 186.8 | Single Straight Movement, Wall Plane **Small** |
| `0x22b` | 335.2 | Single Straight Movement, Wall Plane **Medium** |
| `0x22c` | 445.6 | Single Straight Movement, Wall Plane **Large** |
| `0x22d` | 519.0 | Single Straight Movement, Wall Plane **Largest** |

Hình học font và cách đặt tên ISWA là **hai nguồn độc lập**, và chúng khớp
100%. Đó là điều làm "kích thước glyph" thành nguồn amplitude bảo vệ được
trước phản biện, chứ không phải một phép đo ngẫu nhiên.

**Caveat đã ghi trong output, không giấu:** metric là trung vị đường chéo
bounding box qua mọi `(fill, rotation)` hợp lệ của base đó. Xoay một mũi tên
không vuông thì bbox đổi, nên mỗi base còn dao động nội bộ — trung vị **8,2%**,
lớn nhất **39,5%**.

Font này **đã là dependency sẵn có**: `gen_valid_combinations.py` tải đúng file
này để dựng `iswa_valid_combinations.json`.

---

## Lỗi #3 — `symbol_id` dựng từ `GROUP_START`

Đã audit từ trước, số liệu **tái lập nguyên vẹn** sau khi mở rộng script:

```
[1] GROUP BOUNDARIES (30 groups): ALL MATCH -- GROUP_START là bản dựng lại hoàn hảo
[2] CATEGORY assignment: ALL CORRECT (0 misfiled)
[3] symbol_id STRING vs canonical:  group# lệch 391 / base# lệch 328 / tổng 652
```

**Khác hẳn #1 và #2:** dữ liệu bên dưới ĐÚNG (category + cả 30 ranh giới group
khớp canonical), chỉ **chuỗi ID hiển thị** không chuẩn — nên nó là lỗi *quy
ước*, không phải lỗi *giá trị* như #1/#2. Bản fix thực tế (`c253ecb`) giữ
nguyên `group_of()`/`GROUP_START` đánh số toàn cục và chỉ đổi `symbol_id_of`,
vì `movement_paths`/`finger_articulations` khoá bảng theo cách đánh số đó.

---

## Audit này KHÔNG khẳng định điều gì

Ghi rõ để không ai trích dẫn quá tay trong paper:

- **Không** nói `path_type` đúng của từng symbol trong 242 symbol là gì. Quyết
  định đó là phần *fix*, cần chọn hình học per-symbol — không phải việc của
  audit.
- **Không** chốt hệ số quy đổi font-unit → `amplitude`, cũng chưa chốt nên dùng
  đường chéo bbox, chiều cao, hay độ dài cung của quỹ đạo.
- Mục [4] của lỗi #1 (`path_type` "straight") là **diễn giải theo từ khoá hình
  dạng**; chỉ [2] và [3] (`plane`, `is_hit`) là so sánh nguyên văn với chữ mà
  tên ISWA nói thẳng ra.

## Việc còn mở sau khi chuỗi này đóng

1. `curvature` và `repeat` vẫn là hằng số theo `path_type`, **chưa** lấy từ các
   qualifier Single/Double/Triple/Alternating trong chính tên symbol — đã được
   khai báo trung thực ở `movement_paths.json`'s `unverified_assumptions[3]`.
   Cùng LỚP lỗi với 4 lỗi trên, và giờ vá rẻ vì `iswa_base_symbol_names.json`
   đã có sẵn 242 tên.
2. Vùng **body (Category 5)** và **head & face (Category 4)** đã audit riêng:
   lành mạnh về nguồn — tên per-symbol lấy từ signbank, giá trị chưa đo được
   gắn nhãn `authored` trung thực chứ không claim là đo đạc. Câu hỏi `fill` của
   Category 4 đã được giải bằng `scripts/check_face_fill_semantics.py`.
