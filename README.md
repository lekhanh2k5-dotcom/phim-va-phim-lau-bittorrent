# Phân tích phim và hệ sinh thái chia sẻ phim lậu trên BitTorrent

> Đồ án — môn **Tích hợp, Phân tích & Trực quan hóa Dữ liệu lớn**
> Nhóm/Sinh viên: _(điền tên)_ · Cập nhật: _(điền ngày)_

---

## Tóm tắt

Dự án tích hợp **3 nguồn dữ liệu** — **IMDb**, **TMDb** (gồm dữ liệu streaming do JustWatch cung cấp) và **MagnetDB**
(28,6 triệu torrent thu thập từ mạng BitTorrent DHT) — để (1) phân tích ngành điện ảnh như một dự án phân tích phim thông
thường, rồi (2) mở rộng sang một góc nhìn hiếm có: **phim lậu được chia sẻ thế nào, khi nào, bởi ai**.

Kết quả gồm **8 notebook, 54 biểu đồ** (≈ 30 loại hình khác nhau) trong `notebooks/`, ảnh PNG trong `plots/`.

Dự án chỉ dùng **metadata** (tên, dung lượng, thời gian), không tải nội dung có bản quyền.

## Cấu trúc phân tích

| Chương | Notebook | Biểu đồ | Nội dung |
|---|---|---|---|
| **1. Từng nguồn** | `01_imdb` | 8 | Ngành điện ảnh: số phim/năm, thể loại, điểm, thời lượng, sự chú ý (Lorenz), thể loại đi cùng nhau |
| | `02_tmdb` | 7 | Kinh doanh & phát hành: ngân sách vs doanh thu, ROI theo thể loại, mùa phát hành (polar), cửa sổ chiếu rạp, nước sản xuất (treemap), nhượng quyền, hãng |
| | `03_tmdb_streaming` | 6 | Streaming (JustWatch qua TMDb): bản đồ thế giới, độ phủ vs độ sâu nền tảng, hình thức xem, kho phim trùng nhau (UpSet), thể loại × nền tảng, Netflix theo nước |
| | `04_magnetdb` | 7 | Hệ sinh thái torrent: chia sẻ gì (sunburst), dung lượng "kinh điển" CD/DVD, độ phủ crawler, lịch nhiệt, giờ × thứ, hệ chữ (waffle), số file (CCDF) |
| **2. Kết hợp** | `05_combined` | 6 | Sơ đồ tích hợp; phim hay có ăn khách?; ngân sách vs điểm (raincloud); thể loại: số phim vs doanh thu (slope); chất lượng kho phim từng nền tảng; khả năng xem hợp pháp |
| **3. Phim lậu** | `06_integration` | 4 | Phương pháp ghép torrent → phim: phễu làm sạch, độ phủ theo nguồn, MagnetDB gốc vs tự ghép (dumbbell), độ đồng thuận |
| | `07_piracy_movies` | 8 | Top phim bị lậu; độ nổi tiếng vs bản lậu; thể loại, ngôn ngữ bị lậu vượt mức; phim cũ; bản lậu khi phim ra bản online; độ trễ bản WEB; chiến lược phát hành (hồi quy) |
| | `08_piracy_ecosystem` | 8 | Nhóm phát hành (bump chart); RARBG đóng cửa; codec; độ phân giải; nguồn rip streaming; lồng tiếng × ngôn ngữ gốc; trang lậu Nam Á; torrent giả |

Mỗi notebook: câu hỏi → code → biểu đồ → nhận xét, và bảng tóm tắt ở cuối. Phong cách biểu đồ thống nhất qua `src/viz_style.py`
(bảng màu đã kiểm tra an toàn cho người mù màu).

## Phát hiện chính

**Phim (chương 1–2)**
- Số phim sản xuất/năm tăng ~8 lần trong 100 năm; phim tài liệu vượt chính kịch ở thập niên 2010.
- Sự chú ý cực kỳ tập trung: 1% phim chiếm 69% tổng số vote IMDb (Gini 0,96).
- Chỉ ~1/3 phim vượt ngưỡng hòa vốn ước tính; phim nhượng quyền ~25% số phim nhưng tới ~70% doanh thu.
- COVID rút "cửa sổ chiếu rạp" ở Mỹ từ ~76 xuống ~32 ngày và không quay lại.
- Phim hay chỉ ăn khách hơn một chút (ρ ≈ 0,20); nhiều tiền không làm phim được chấm cao hơn.
- ~96% phim chỉ có trên đúng một nền tảng streaming ở Mỹ — kho phim rất phân mảnh.

**Phim lậu (chương 3)**
- Mã IMDb có sẵn trong MagnetDB phủ rất thấp và có lỗi; **tự ghép tên torrent tăng dữ liệu ~14 lần**
  (đồng thuận 99,4% với mã MagnetDB đã làm sạch). Không có bước này, gần như mọi bom tấn "biến mất" khỏi dữ liệu.
- Bản lậu mới **tăng ~20 lần đúng tuần phim ra bản online hợp pháp** (bản online là nguồn rip); bản WEB lậu xuất hiện trung vị 0 ngày sau đó.
- Ra bản online sớm hay muộn chủ yếu đổi **thời điểm**, chưa thấy đổi rõ **tổng lượng** bản lậu năm đầu.
- Phim tiếng Nga, Trung, Ba Lan bị lậu gấp đôi mức nổi tiếng; ~1/3 bản lậu mới là phim trước 2010.
- RARBG đóng cửa (5/2023) để lại khoảng trống không nhóm nào lấp hết; Amazon và Netflix là nguồn của ~80% bản WEB có ghi nguồn.

## Nguồn dữ liệu (3 nguồn)

| Nguồn | Vai trò | Định dạng | Lấy ở đâu |
|---|---|---|---|
| **IMDb Datasets** | Danh mục phim chuẩn, **khóa trung tâm** `tconst` | TSV nén | `datasets.imdbws.com` |
| **TMDb API** | Ngân sách, doanh thu, ngày phát hành theo nước/loại; **watch providers do JustWatch cung cấp** | JSON qua API (~142k phim) | `themoviedb.org` (cần API key) |
| **MagnetDB** | Tín hiệu chia sẻ (torrent, file, thời điểm phát hiện) | SQLite 117 GB | OSF `osf.io/9eh47` (torrent `MagnetDB_2024.torrent`) |

Tính không đồng nhất (nội dung báo cáo): **cấu trúc** (SQLite / TSV / JSON), **định danh** (MagnetDB không có khóa
phim → ghép thực thể), **ngữ nghĩa thời gian** (năm sản xuất / ngày phát hành theo nước / thời điểm crawler phát hiện /
ảnh chụp hiện tại 2026), **chất lượng** (lỗi ghép, lỗi mã hóa tên, torrent giả, crawler ngừng 122 ngày).

## Chỉ muốn xem kết quả?

Không cần tải dữ liệu:
- **Dashboard + slide (online):** https://lekhanh2k5-dotcom.github.io/phim-va-phim-lau-bittorrent/
- **Quy trình xử lý từng bước** (dữ liệu thô → ghép → làm sạch, có bảng ví dụ trước/sau và số lượng còn lại sau mỗi bộ lọc):
  [`notebooks/00_quy_trinh_xu_ly.ipynb`](notebooks/00_quy_trinh_xu_ly.ipynb)
- **Slide thuyết trình:** https://lekhanh2k5-dotcom.github.io/phim-va-phim-lau-bittorrent/report/phim_15_phut/slides.html
- **Notebook phân tích đã chạy sẵn** (01–08, có đủ biểu đồ và nhận xét): mở các file trong `notebooks/` ngay trên GitHub.
- **Ảnh biểu đồ:** thư mục `plots/`.

Dữ liệu thô và dữ liệu đã xử lý **không có trong repo** (MagnetDB ~117 GB, dữ liệu đã xử lý ~2,7 GB, và điều khoản IMDb
không cho phân phối lại). Để chạy lại toàn bộ, làm theo hai mục dưới đây.

## Tải và lưu dữ liệu

### Chuẩn bị

- **Dung lượng ổ đĩa trống: ≥ 160 GB** (MagnetDB nén 27,7 GB + giải nén 117 GB; xóa file nén sau khi giải nén để lấy lại
  ~28 GB). Nên dùng ổ SSD.
- **RAM:** không cần nhiều — DuckDB đọc SQLite theo luồng, không nạp cả 117 GB vào RAM.
- **Python 3.12** và các thư viện: `pip install -r requirements.txt`
- **Phần mềm torrent** để tải MagnetDB (vd. qBittorrent) và công cụ giải nén `.tar.zst`
  (Windows 10/11: lệnh `tar` có sẵn; macOS/Linux: `tar` + `zstd`).

### Cấu trúc thư mục dữ liệu cần tạo

Các script tìm dữ liệu theo **đúng đường dẫn** dưới đây (tính từ thư mục gốc của repo):

```
phim-va-phim-lau-bittorrent/
├── .env                                   ← khóa TMDb (bước 3)
└── data_raw/
    ├── magnetdb/
    │   ├── magnetdb_public.sqlite3        ← ~117 GB, giải nén từ .tar.zst (bước 1)
    │   └── matchedVideos_sample.csv       ← ~563 MB, đi kèm trong torrent (bước 1)
    ├── imdb/
    │   ├── title.basics.tsv.gz            ← bước 2 (giữ nguyên dạng .gz, KHÔNG cần giải nén)
    │   ├── title.ratings.tsv.gz
    │   └── title.akas.tsv.gz
    ├── tmdb_cache/                        ← tự tạo khi chạy src/06_fetch_tmdb.py (bước 3)
    └── geo/
        └── ne_110m_admin_0_countries.geojson   ← bước 4 (chỉ cho bản đồ)
```

`data_clean/` được các script tự tạo — không cần chuẩn bị.

### Bước 1 — MagnetDB (Seidenberger và cộng sự, 2025; CC-BY 4.0)

1. Vào trang OSF của bộ dữ liệu: **https://osf.io/9eh47/** → tải file **`MagnetDB_2024.torrent`**.
2. Mở file `.torrent` bằng qBittorrent, chọn thư mục lưu là **`data_raw/magnetdb/`**. Torrent gồm:
   - `magnetdb_public.sqlite3.tar.zst` (**27,67 GB**) — cơ sở dữ liệu chính, **bắt buộc**;
   - `matchedVideos_sample.csv` (563 MB) — **bắt buộc** (dùng ở `src/01`);
   - `README_MagnetDB_Metadata.pdf`, `files_sample.csv`, `torrents_sample.csv` — tài liệu và mẫu, không bắt buộc.

   qBittorrent có thể tạo thêm thư mục con `MagnetDB_2024/` — hãy chuyển các file ra thẳng `data_raw/magnetdb/`
   (hoặc giải nén vào đó ở bước sau).
3. Giải nén (mất ~10–30 phút):
   ```bash
   tar -xf data_raw/magnetdb/magnetdb_public.sqlite3.tar.zst -C data_raw/magnetdb
   ```
   Kết quả: `data_raw/magnetdb/magnetdb_public.sqlite3` (~117 GB). Sau đó có thể xóa file `.tar.zst`.

### Bước 2 — IMDb Non-Commercial Datasets

Tải 3 file từ **https://datasets.imdbws.com/** vào `data_raw/imdb/`:
`title.basics.tsv.gz` (~230 MB), `title.ratings.tsv.gz` (~9 MB), `title.akas.tsv.gz` (~520 MB).

```bash
mkdir -p data_raw/imdb && cd data_raw/imdb
curl -O https://datasets.imdbws.com/title.basics.tsv.gz
curl -O https://datasets.imdbws.com/title.ratings.tsv.gz
curl -O https://datasets.imdbws.com/title.akas.tsv.gz
```

IMDb cập nhật các file này hằng ngày, nên số liệu khi chạy lại có thể lệch nhẹ so với kết quả trong repo
(bản dùng trong dự án: tải ngày 05/10/2026). Dữ liệu IMDb chỉ dùng cho mục đích cá nhân, phi thương mại.

### Bước 3 — Khóa TMDb API

1. Tạo tài khoản miễn phí tại https://www.themoviedb.org/ → **Settings → API** → đăng ký API (loại *Developer*,
   mục đích học tập) → sao chép **API Key**.
2. Sao chép `.env.example` thành `.env` ở thư mục gốc repo và điền khóa: `TMDB_API_KEY=...`.
   File `.env` đã nằm trong `.gitignore` — **không bao giờ commit khóa lên GitHub**.
3. Dữ liệu TMDb được tải tự động khi chạy `src/06_fetch_tmdb.py` (lưu từng phim thành một file JSON trong
   `data_raw/tmdb_cache/`). ~142 nghìn phim × 2 lượt gọi API, **mất ~4–5 giờ**; dừng giữa chừng thì chạy lại sẽ tiếp tục
   từ chỗ dừng. Ở một số nhà mạng Việt Nam, DNS chặn `api.themoviedb.org` — script tự chuyển sang DNS-over-HTTPS
   (1.1.1.1); nếu vẫn lỗi, đổi DNS máy sang 1.1.1.1 hoặc 8.8.8.8.

### Bước 4 — Ranh giới quốc gia (chỉ để vẽ bản đồ, notebook 03)

```bash
mkdir -p data_raw/geo
curl -L -o data_raw/geo/ne_110m_admin_0_countries.geojson \
  https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson
```

## Chạy lại toàn bộ

**Lớp 1 — xử lý dữ liệu (`src/`, chạy một lần, theo thứ tự).** Chạy từ thư mục gốc repo, vd. `python src/01_matched_files_to_parquet.py`.

| Script | Việc | Đầu ra (`data_clean/`) | Thời gian* |
|---|---|---|---|
| `01_matched_files_to_parquet` | CSV file-khớp-IMDb của MagnetDB → Parquet | `matched_files` | ~5 giây |
| `02_extract_torrent_times` | Thời điểm phát hiện + tên torrent từ SQLite (`--test` để thử trước) | `magnetdb_matched_slice` | ~1 phút |
| `03_imdb_catalog` | Danh mục IMDb, chỉ mục tên (gồm akas), mọi phim | `imdb_catalog`, `imdb_title_index`, `imdb_movies_all` | ~20 giây |
| `04_match_torrent_names` | **Tự ghép** tên torrent → phim (tên + năm, SQL) | `name_matches` | ~2 phút |
| `05_build_movie_list` | Danh sách phim từ hai nguồn ghép | `movies` | vài giây |
| `06_fetch_tmdb --catalog-min-votes 1000` | Gọi TMDb (cả phim IMDb ≥ 1.000 vote không có trên torrent) | `data_raw/tmdb_cache/*.json` | ~4–5 giờ |
| `07_tmdb_to_table` | JSON → bảng | `tmdb_movies`, `tmdb_release_dates`, `tmdb_watch_providers` | ~1 phút |
| `08_match_eval` | Pipeline guessit + rapidfuzz, đánh giá vs MagnetDB (cho notebook 06) | `match_eval` | ~3 phút |
| `09_build_tables` | Làm sạch (A–J) + gộp hai nguồn | `torrents_clean`, `movie_analysis`, `cleaning_log.csv` | ~1 phút |
| `10_extract_magnetdb_overview` | Mọi torrent + mẫu 1% bảng files (cho notebook 04) | `mdb_torrents_all`, `mdb_files_sample`, `mdb_files_per_torrent` | ~7 phút |

\*Đo trên máy chạy dự án (Windows, ổ SSD); máy khác có thể nhanh/chậm hơn.

**Lớp 2 — phân tích & trực quan (`notebooks/`).** Mở và chạy bất kỳ notebook nào (chỉ đọc Parquet trong `data_clean/`,
~vài chục giây/notebook). Notebook được dựng từ mã nguồn trong `notebooks/_src/`
(`python notebooks/_src/make_0X.py` dựng lại và chạy notebook X); nếu sửa trực tiếp trong `.ipynb` thì không chạy lại
`make_0X` để tránh ghi đè.

**Dashboard & slide:** `python report/phim_15_phut/build.py` tạo lại `report/phim_15_phut/dashboard.html` và `slides.html`
từ các Parquet (xem `report/phim_15_phut/README.md`).

## Lưu ý phương pháp & giới hạn

- **Độ phủ crawler không đều**: burn-in 9/2019–3/2020, gần như ngừng 7/2020–3/2021 (trống 122 ngày), trống ~1 tháng 6/2024.
  Mọi phân tích theo thời gian chỉ dùng **04/2021 – 09/2024**.
- **Thước đo phim lậu là nguồn cung** (số torrent được đăng), không phải số người tải (MagnetDB không có seeder/leecher).
- `discovered_on` là lúc crawler **thấy** torrent, không phải lúc tạo torrent.
- **Ghép tự động không hoàn hảo**: tự ghép cần năm trong tên torrent; phim trùng tên (±1 năm) hoặc tên quá chung chung của phim ít
  người biết bị bỏ (vd. *Pinocchio* 2022 bị đếm thiếu). Mục IMDb chỉ là sự kiện thể thao/chương trình bị loại.
- **Không phân tích sâu bản quay lén CAM/TS/TC**: nhãn ngắn, dễ nhận nhầm.
- **Dữ liệu tham chiếu là ảnh chụp 2026** (vote, doanh thu, streaming); ngày phát hành TMDb có lịch sử nhưng có thể thiếu nước/loại.
- TMDb ghi ngân sách/doanh thu = 0 khi không rõ (chỉ ~9.300 phim có đủ); tiền USD danh nghĩa.
- **Tương quan ≠ nhân quả.** Dữ liệu IMDb/TMDb nghiêng về phim và khán giả phương Tây.

## Trích dẫn & giấy phép

- **MagnetDB** (CC-BY 4.0): Seidenberger, S., Pursell, N., & Maiti, A. (2025). *MagnetDB: A Longitudinal Torrent Discovery
  Dataset with IMDb-Matched Movies and TV Shows.* ICWSM 19(1), 2575–2586. DOI: 10.17605/OSF.IO/9EH47 · arXiv:2501.09275
- **IMDb**: dữ liệu thuộc IMDb.com, Inc., dùng cho mục đích cá nhân/phi thương mại.
- **TMDb**: "This product uses the TMDB API but is not endorsed or certified by TMDB."
- **JustWatch**: dữ liệu watch providers trong TMDb do JustWatch cung cấp — bắt buộc ghi nguồn.
- **Natural Earth**: ranh giới quốc gia cho bản đồ (public domain).

## Cấu trúc thư mục

```
phim-va-phim-lau-bittorrent/
├── README.md
├── .env                 # khóa TMDb của bạn — KHÔNG commit (đã gitignore)
├── data_raw/            # KHÔNG có trong repo — tải theo mục "Tải và lưu dữ liệu"
├── data_clean/          # KHÔNG có trong repo — các script src/ tự tạo
├── requirements.txt     # thư viện Python
├── .env.example         # mẫu file khóa TMDb
├── src/                 # 01–10: xử lý dữ liệu; viz_style.py: phong cách biểu đồ dùng chung
├── notebooks/           # 01–08: phân tích & trực quan; _src/: mã nguồn dựng notebook
├── plots/               # 1_imdb … 8_piracy_ecosystem (54 PNG)
└── report/              # báo cáo
```
