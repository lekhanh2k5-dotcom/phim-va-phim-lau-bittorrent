"""Dựng notebooks/00_quy_trinh_xu_ly.ipynb: đi qua từng bước xử lý dữ liệu, có ví dụ trước/sau.
Chạy một lần trên máy có dữ liệu; kết quả được lưu trong notebook để người khác xem không cần dữ liệu."""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

OUT = Path(r"D:\dulieulon\notebooks\00_quy_trinh_xu_ly.ipynb")
md = nbformat.v4.new_markdown_cell
code = nbformat.v4.new_code_cell

cells = [
md("""# Phần 0 — Quy trình xử lý dữ liệu: từ dữ liệu thô đến dữ liệu sạch

Notebook này **đã được chạy sẵn**: mọi bảng ví dụ và con số bên dưới được lưu trong file, nên có thể xem trực tiếp trên
GitHub **mà không cần tải dữ liệu** (MagnetDB ~117 GB). Muốn chạy lại, làm theo mục *Tải và lưu dữ liệu* trong `README.md`.

Mỗi bước gồm: **đầu vào → việc làm → ví dụ dữ liệu → số lượng còn lại**. Mã nguồn đầy đủ của từng bước nằm trong `src/`.

```
 DỮ LIỆU THÔ                         TIỀN XỬ LÝ / TÍCH HỢP                               DỮ LIỆU SẠCH
 ───────────                         ─────────────────────                               ────────────
 MagnetDB (SQLite 117 GB) ──► 01–02  file video + thời điểm phát hiện ──┐
                          └─► 04     tự ghép TÊN torrent → phim IMDb ───┤
 IMDb (TSV)               ──► 03     danh mục phim + chỉ mục tên (akas) ┼──► 05 danh sách phim ──► 09 LÀM SẠCH ──► torrents_clean
 TMDb API (JSON)          ──► 06–07  ngày phát hành, tài chính, streaming┘                         (bộ lọc A–J)   movie_analysis
                              08     đánh giá chất lượng ghép
 MagnetDB (toàn bộ)       ──► 10     tổng quan hệ sinh thái (mọi loại nội dung) ──────────────────────────────► mdb_*
```"""),
code("""import sys, json
from pathlib import Path
import duckdb, pandas as pd
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "src" / "viz_style.py").exists())
DC = ROOT / "data_clean"
pd.set_option("display.max_colwidth", 90); pd.set_option("display.width", 200)
con = duckdb.connect(); con.sql("SET enable_progress_bar = false")
q = lambda sql: con.sql(sql.replace("@", (DC.as_posix() + "/"))).df()   # @x.parquet = data_clean/x.parquet
n = lambda sql: con.sql(sql.replace("@", (DC.as_posix() + "/"))).fetchone()[0]"""),

md("""## Bước 0 — Dữ liệu thô: ba nguồn, ba định dạng, không có khóa chung

| Nguồn | Định dạng | Quy mô | Khóa phim |
|---|---|---|---|
| **MagnetDB** | SQLite 117 GB: bảng `torrents` (28,6 triệu dòng), `files` (950 triệu dòng) | lớn nhất | **không có** — chỉ có tên torrent/tên file tự do |
| **IMDb** | 3 file TSV nén: `title.basics`, `title.ratings`, `title.akas` | ~760 nghìn phim | `tconst` (vd. `tt1630029`) |
| **TMDb** | API trả JSON, 1 file/phim | ~142 nghìn phim | `imdb_id` → nối thẳng với IMDb |

Ví dụ một dòng **torrent thô** của MagnetDB — tên là chuỗi tự do, phải tự tách ra phim nào:"""),
code("""q(\"\"\"SELECT torrent_id, name AS ten_torrent, round(total_size/1e9, 2) AS GB, discovered_at_utc AS thoi_diem_phat_hien
     FROM '@mdb_torrents_all.parquet'
     WHERE name ILIKE '%Avatar.The.Way.of.Water.2022%' OR name ILIKE '%Top.Gun.Maverick.2022%' OR name ILIKE '%Dune.2021.1080p%'
     ORDER BY torrent_id LIMIT 5\"\"\")"""),
md("Tổng quy mô bảng `torrents` (mọi loại nội dung: phim, nhạc, phần mềm, ảnh…):"),
code("""q("SELECT count(*) AS so_torrent, min(discovered_at_utc) AS tu, max(discovered_at_utc) AS den FROM '@mdb_torrents_all.parquet'")"""),

md("""## Bước 1–2 — Mã IMDb có sẵn trong MagnetDB (`src/01`, `src/02`)

**Đầu vào:** `matchedVideos_sample.csv` (MagnetDB đã tự ghép file video với IMDb, chỉ giữ điểm khớp `matchScore > 138`) +
bảng `torrents` trong SQLite (lấy thời điểm phát hiện).
**Việc làm:** chuyển CSV → Parquet, lấy `discovered_on` của từng torrent, giải mã lại ~1.300 tên torrent bị lỗi mã hóa
(Windows-1251, tiếng Nga).
**Vấn đề phát hiện:** mã ghép sẵn **có lỗi** và **phủ rất thấp**. Ví dụ các ca gán sai rõ ràng:"""),
code("""q(\"\"\"SELECT path AS ten_file, parsed_title AS ten_tach_duoc, match_title AS MagnetDB_gan_vao, round(match_score) AS diem
     FROM '@matched_files.parquet'
     WHERE path ILIKE '1. Introduction%' OR path ILIKE '%Girlfriend.Experience.S0%' OR path ILIKE 'Amarcord%'
     QUALIFY row_number() OVER (PARTITION BY match_title ORDER BY file_id) = 1 LIMIT 5\"\"\")"""),
code("""q(\"\"\"SELECT (SELECT count(*) FROM '@matched_files.parquet') AS so_file_video_da_ghep,
            (SELECT count(DISTINCT torrent_id) FROM '@matched_files.parquet') AS so_torrent,
            (SELECT count(DISTINCT imdb_id) FROM '@matched_files.parquet') AS so_ma_IMDb\"\"\")"""),

md("""## Bước 3 — Danh mục IMDb và chỉ mục tên (`src/03`)

**Việc làm:** giữ phim (`titleType = movie`), gắn điểm/số vote, và tạo **chỉ mục tên chuẩn hóa**: mỗi phim có nhiều tên
(tên gốc, tên tiếng Anh, tên ở từng nước trong `title.akas`), mọi tên được **bỏ dấu, viết thường, bỏ ký tự đặc biệt**.
Nhờ đó tên torrent tiếng Nga, Ý, Tây Ban Nha… vẫn tra được. Ví dụ các tên của *The Big Lebowski* trong chỉ mục:"""),
code("""q("SELECT norm AS ten_chuan_hoa, tconst, start_year, num_votes FROM '@imdb_title_index.parquet' WHERE tconst = 'tt0118715' LIMIT 12")"""),
code("""q(\"\"\"SELECT (SELECT count(*) FROM '@imdb_movies_all.parquet') AS moi_phim_IMDb,
            (SELECT count(*) FROM '@imdb_catalog.parquet') AS ung_vien_co_rating,
            (SELECT count(*) FROM '@imdb_title_index.parquet') AS so_ten_trong_chi_muc\"\"\")"""),

md("""## Bước 4 — Tự ghép tên torrent → phim (`src/04`, bước tích hợp quan trọng nhất)

**Vì sao:** MagnetDB tách tên đúng nhưng tra IMDb sai (vd. `Deadpool.2016.1080p.BluRay` → một video ca nhạc, điểm 11 nên bị loại),
nên bom tấn gần như vắng mặt trong dữ liệu gốc.
**Việc làm (toàn bộ bằng SQL trên 23,5 triệu torrent ≥ 100 MB, ~2 phút):**
1. Bỏ tiền tố rác (`[YTS.MX]`, `www.site.com -`), đuôi file.
2. Tách **NĂM** (1920–2029, không nhầm với `1080p`, `1920x1080`) và **TÊN** = phần trước năm.
3. Bỏ torrent phim bộ (`S01E02`, `Season`, `Сезон`…).
4. Tra **chính xác** tên chuẩn hóa trong chỉ mục IMDb, năm lệch ≤ 1, chỉ phim lẻ.
5. Đánh dấu **mơ hồ** khi trùng tên nhiều phim, hoặc tên quá chung chung của phim ít người biết ("New", "Cricket").

Ví dụ kết quả ghép:"""),
code("""q(\"\"\"SELECT n.torrent_name AS ten_torrent, n.name_title AS ten_tach, n.name_year AS nam, m.title AS phim_IMDb, m.start_year
     FROM '@name_matches.parquet' n JOIN '@movies.parquet' m USING (imdb_id)
     WHERE NOT n.ambiguous AND m.num_votes > 100000
       AND (n.torrent_name ILIKE '%Банды.Нью-Йорка%' OR n.torrent_name ILIKE '%I Guerrieri (1970)%'
            OR n.torrent_name ILIKE 'Parasite.2019.PL%' OR n.torrent_name ILIKE '%Scarface.1983.1080p.BluRay.10bit%'
            OR n.torrent_name ILIKE '%Drácula de Bram Stoker%')
     QUALIFY row_number() OVER (PARTITION BY m.imdb_id ORDER BY n.torrent_id) = 1\"\"\")"""),
code("""q(\"\"\"SELECT count(*) AS torrent_ghep_duoc, count(*) FILTER (WHERE ambiguous) AS ca_mo_ho_bi_bo,
            count(DISTINCT imdb_id) FILTER (WHERE NOT ambiguous) AS so_phim
     FROM '@name_matches.parquet'\"\"\")"""),

md("""## Bước 5–7 — Danh sách phim và dữ liệu TMDb (`src/05`, `src/06`, `src/07`)

**Việc làm:** hợp danh sách phim của hai cách ghép (bỏ mục không phải phim như sự kiện thể thao); gọi TMDb API cho từng phim
(và mọi phim IMDb ≥ 1.000 vote) → JSON được lưu đệm → chuyển thành 3 bảng: thông tin phim, ngày phát hành theo nước/loại,
nơi xem streaming theo nước. Ví dụ dòng đã chuẩn hóa:"""),
code("""q(\"\"\"SELECT imdb_id, tmdb_title, release_date::DATE AS ngay_phat_hanh, budget, revenue,
            first_theatrical::DATE AS ra_rap_som_nhat, first_digital::DATE AS ban_online_som_nhat, us_streaming_providers
     FROM '@tmdb_movies.parquet' WHERE imdb_id IN ('tt1630029','tt1745960','tt1160419')\"\"\")"""),
code("""q("SELECT imdb_id, country AS nuoc, type AS loai, release_date::DATE AS ngay FROM '@tmdb_release_dates.parquet' WHERE imdb_id = 'tt1745960' ORDER BY ngay LIMIT 8")"""),
md("Loại phát hành TMDb: 1 công chiếu, 2 rạp giới hạn, 3 rạp, **4 Digital (bản online)**, 5 đĩa, 6 TV."),

md("""## Bước 8 — Đánh giá chất lượng ghép (`src/08`)

Một pipeline độc lập thứ hai (thư viện `guessit` tách tên file + `rapidfuzz` so tên gần đúng) được chạy trên 20.000 tên file
và so với mã của MagnetDB — để biết các cách ghép đồng thuận đến đâu:"""),
code("""ev = q("SELECT * FROM '@match_eval.parquet'")
pred, ok = ev["pred"].notna(), ev["pred"] == ev["truth"]
pd.DataFrame({"so_ten_file": [len(ev)], "precision": [round(ok.sum() / pred.sum(), 3)], "recall": [round(ok.sum() / len(ev), 3)]})"""),

md("""## Bước 9 — Làm sạch và gộp hai nguồn (`src/09`, bộ lọc A–J)

Đây là bước biến dữ liệu "ghép được" thành dữ liệu **tin được**. Bảng dưới là nhật ký số lượng còn lại sau từng bộ lọc
(`data_clean/cleaning_log.csv`):"""),
code("""log = pd.read_csv(DC / "cleaning_log.csv")
log.rename(columns={"source": "nguon", "step": "buoc", "files": "so_file", "torrents": "so_torrent", "movies": "so_phim"})"""),
md("""Ý nghĩa từng bộ lọc và **ví dụ thật của dòng bị loại**:

| Bộ lọc | Loại bỏ cái gì |
|---|---|
| A | Không phải phim lẻ (phim bộ, video, chương trình TV) |
| B | Tập phim bộ bị gán nhầm vào phim lẻ cùng tên (`S01E05`) |
| C | Tệp < 100 MB: trailer, clip, sample |
| D | Năm trong tên file lệch > 1 năm so với năm phim |
| E / E2 | Tên file không giống bất kỳ tên nào của phim; sai phần phim (Part 2 ≠ Part 1) |
| F | Torrent xuất hiện sớm hơn 60 ngày trước lần ra mắt đầu tiên của phim |
| G | Hai nguồn ghép mâu thuẫn (torrent 1 phim, hai cách ghép ra hai phim khác nhau) |
| H, I | Tên torrent có từ khóa phim bộ; năm trên tên torrent lệch |
| J | **Torrent giả**: tự xưng bản WEB/BluRay khi phim chưa có bản đó |"""),
md("**Ví dụ bộ lọc B và D** — tập phim bộ và năm lệch bị MagnetDB gán vào phim lẻ:"),
code("""q(\"\"\"SELECT s.path AS ten_file, s.parsed_year AS nam_trong_ten, m.title AS bi_gan_vao, m.start_year AS nam_phim,
            CASE WHEN s.is_tv_hint THEN 'B: tập phim bộ' ELSE 'D: năm lệch' END AS bi_loai_vi
     FROM '@magnetdb_matched_slice.parquet' s JOIN '@movies.parquet' m USING (imdb_id)
     WHERE (s.is_tv_hint AND s.path ILIKE '%Series.of.Unfortunate.Events.S0%')
        OR (NOT s.is_tv_hint AND s.file_size >= 1e8 AND abs(s.parsed_year - m.start_year) > 1 AND m.title IN ('Gang of Roses', 'Independence Day'))
     QUALIFY row_number() OVER (PARTITION BY m.title ORDER BY s.file_id) <= 2\"\"\")"""),
md("**Ví dụ bộ lọc J** — torrent giả: bản \"BluRay\" của phim xuất hiện khi phim còn chưa ra rạp, cùng một dung lượng lặp lại:"),
code("""q(\"\"\"SELECT t.discovered_at_utc::DATE AS phat_hien, t.torrent_name AS ten_torrent, round(t.total_size/1e9, 2) AS GB,
            m.first_theatrical::DATE AS ra_rap, m.first_digital::DATE AS ban_online
     FROM '@torrents_clean.parquet' t JOIN '@movie_analysis.parquet' m USING (imdb_id)
     WHERE t.implausible AND m.title = 'Ant-Man and the Wasp: Quantumania'
     ORDER BY phat_hien LIMIT 6\"\"\")"""),

md("""## Kết quả: hai bảng sạch dùng cho mọi phân tích

**`torrents_clean`** — 1 dòng = 1 cặp (torrent, phim), kèm nguồn ghép, chất lượng bản phát hành, cờ gói nhiều phim, cờ torrent giả:"""),
code("""q(\"\"\"SELECT t.torrent_name, m.title AS phim, t.source AS nguon_ghep, t.quality_tier AS chat_luong, t.is_pack, t.implausible,
            t.discovered_at_utc::DATE AS phat_hien
     FROM '@torrents_clean.parquet' t JOIN '@movies.parquet' m USING (imdb_id)
     WHERE m.title IN ('Dune', 'Top Gun: Maverick') AND m.start_year IN (2021, 2022) AND t.in_stable_window AND NOT t.implausible AND t.quality_tier IN ('web', 'disc') AND regexp_matches(t.torrent_name, '^[A-Za-z0-9.:]+$')
     QUALIFY row_number() OVER (PARTITION BY m.title, t.source, t.quality_tier ORDER BY t.torrent_id) = 1\"\"\")"""),
md("**`movie_analysis`** — 1 dòng = 1 phim: IMDb + TMDb + thống kê torrent trong giai đoạn crawler ổn định (04/2021 – 09/2024):"),
code("""q(\"\"\"SELECT title, start_year, num_votes, avg_rating, revenue, first_digital::DATE AS ban_online,
            n_torrents_stable AS so_torrent_on_dinh, n_torrents_stable_magnetdb AS chi_tinh_ma_MagnetDB
     FROM '@movie_analysis.parquet' ORDER BY n_torrents_stable DESC LIMIT 8\"\"\")"""),
code("""q(\"\"\"SELECT count(*) AS cap_torrent_phim_sach, count(DISTINCT torrent_id) AS so_torrent, count(DISTINCT imdb_id) AS so_phim,
            count(*) FILTER (WHERE in_stable_window) AS trong_giai_doan_on_dinh
     FROM '@torrents_clean.parquet' WHERE NOT implausible\"\"\")"""),
md("""## Tóm tắt quy trình

| Giai đoạn | Script | Đầu ra chính | Ý nghĩa |
|---|---|---|---|
| Trích xuất | 01–02, 10 | `matched_files`, `magnetdb_matched_slice`, `mdb_*` | Lấy phần cần dùng từ SQLite 117 GB |
| Chuẩn hóa | 03 | `imdb_title_index` | Mọi tên phim ở mọi ngôn ngữ về một dạng |
| Tích hợp | 04, 05, 06–07 | `name_matches`, `movies`, `tmdb_*` | Ghép torrent ↔ IMDb ↔ TMDb |
| Đánh giá | 08 | `match_eval` | Đo mức đồng thuận của phép ghép |
| Làm sạch | 09 | `torrents_clean`, `movie_analysis` | 10 bộ lọc A–J, loại lỗi ghép và torrent giả |

Các notebook 01–08 dùng hai bảng sạch này để phân tích và vẽ biểu đồ."""),
]

nb = nbformat.v4.new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
NotebookClient(nb, timeout=1800, kernel_name="python3", resources={"metadata": {"path": str(OUT.parent)}}).execute()
nbformat.write(nb, OUT)
errs = sum(o.get("output_type") == "error" for c in nb.cells if c.cell_type == "code" for o in c.outputs)
print("wrote", OUT, "errors:", errs)
