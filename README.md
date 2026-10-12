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

## Cách chạy

```bash
pip install duckdb pyarrow pandas numpy matplotlib squarify geopandas statsmodels \
            guessit rapidfuzz python-dotenv requests nbformat nbclient ipykernel

# Dữ liệu thô: giải nén MagnetDB (tar của Windows 11 hỗ trợ zstd) vào data_raw/magnetdb/;
# IMDb .tsv.gz vào data_raw/imdb/; TMDb key trong .env (TMDB_API_KEY)
tar -xf magnetdb_public.sqlite3.tar.zst -C data_raw/magnetdb
```

**Lớp 1 — xử lý dữ liệu (`src/`, chạy một lần, theo thứ tự):**

| Script | Việc | Đầu ra (`data_clean/`) |
|---|---|---|
| `01_matched_files_to_parquet` | CSV file-khớp-IMDb của MagnetDB → Parquet | `matched_files` |
| `02_extract_torrent_times` | Thời điểm phát hiện + tên torrent từ SQLite | `magnetdb_matched_slice` |
| `03_imdb_catalog` | Danh mục IMDb, chỉ mục tên (gồm akas), mọi phim | `imdb_catalog`, `imdb_title_index`, `imdb_movies_all` |
| `04_match_torrent_names` | **Tự ghép** tên torrent → phim (tên + năm, SQL) | `name_matches` |
| `05_build_movie_list` | Danh sách phim từ hai nguồn ghép | `movies` |
| `06_fetch_tmdb` | Gọi TMDb (`--catalog-min-votes 1000` để lấy cả phim không có trên torrent) | `data_raw/tmdb_cache/*.json` |
| `07_tmdb_to_table` | JSON → bảng | `tmdb_movies`, `tmdb_release_dates`, `tmdb_watch_providers` |
| `08_match_eval` | Pipeline guessit + rapidfuzz, đánh giá vs MagnetDB | `match_eval` |
| `09_build_tables` | Làm sạch (A–J) + gộp hai nguồn | `torrents_clean`, `movie_analysis`, `cleaning_log.csv` |
| `10_extract_magnetdb_overview` | Mọi torrent + mẫu 1% bảng files (cho chương 1.4) | `mdb_torrents_all`, `mdb_files_sample`, `mdb_files_per_torrent` |

**Lớp 2 — phân tích & trực quan (`notebooks/`)**: mở và chạy bất kỳ notebook nào (chỉ đọc Parquet, ~vài chục giây/notebook).
Notebook được dựng từ mã nguồn trong `notebooks/_src/` (`python notebooks/_src/make_0X.py` dựng lại và chạy notebook X);
nếu sửa trực tiếp trong `.ipynb` thì không chạy lại `make_0X` để tránh ghi đè.

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
dulieulon/
├── README.md
├── .env                 # TMDb key — KHÔNG chia sẻ/commit
├── data_raw/            # magnetdb/ (SQLite 117 GB), imdb/, tmdb_cache/, geo/
├── data_clean/          # Parquet trung gian + bảng phân tích, cleaning_log.csv
├── src/                 # 01–10: xử lý dữ liệu; viz_style.py: phong cách biểu đồ dùng chung
├── notebooks/           # 01–08: phân tích & trực quan; _src/: mã nguồn dựng notebook
├── plots/               # 1_imdb … 8_piracy_ecosystem (54 PNG)
└── report/              # báo cáo
```
