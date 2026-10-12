"""
Stage 2e: TỰ GHÉP tên torrent -> phim IMDb, để lấy lại các torrent MagnetDB bỏ sót.

Vì sao: MagnetDB tách tên đúng nhưng tra IMDb sai rồi loại vì điểm thấp, vd.
"Deadpool.2016.1080p.BluRay" -> "Deadpool (feat. Deadpool)" (video ca nhạc, điểm 11).
Tập matchScore > 138 chỉ phủ ~1/10 torrent phim.

Cách làm (toàn bộ trong DuckDB, không cần guessit -> chạy trên hàng chục triệu tên):
  1. Lấy torrent trong cửa sổ 2019-04 -> 2024-09, tổng dung lượng >= 100MB.
  2. Bỏ tiền tố rác ("[UCCUSS]", "【...】", "www.site.com -"), đuôi file.
  3. Tách NĂM (1920-2029, không phải "1080p"/"1920x1080") và TÊN = phần đứng trước năm.
     Không có năm -> bỏ (giữ độ chính xác).
  4. Bỏ torrent phim bộ (S01E02, Season, Сезон, серия...).
  5. Các cách viết tên: đầy đủ; phần chữ Latin cuối ("Банды Нью-Йорка Gangs of New York"
     -> "Gangs of New York"); phần trước chữ Latin ("Парк Юрского периода"); bỏ số rác đầu.
  6. Tra CHÍNH XÁC trong chỉ mục tên IMDb (gồm akas), chỉ titleType = 'movie', năm ±1;
     nhiều phim trùng -> ưu tiên đúng năm, rồi nhiều vote nhất.

Đầu ra: data_clean/name_matches.parquet  (1 dòng = 1 torrent ghép được)

Chạy:  python src/04_match_torrent_names.py
"""

import datetime
import sys
import time
from pathlib import Path

import duckdb

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT     = Path(__file__).resolve().parent.parent
DB_PATH  = (ROOT / "data_raw/magnetdb/magnetdb_public.sqlite3").as_posix()
INDEX    = (ROOT / "data_clean/imdb_title_index.parquet").as_posix()
CATALOG  = (ROOT / "data_clean/imdb_catalog.parquet").as_posix()
OUT      = ROOT / "data_clean/name_matches.parquet"

WINDOW_START = "2019-04-01"
WINDOW_END   = "2024-09-30"
MIN_TOTAL_MB = 100

to_epoch = lambda d: int(
    datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).timestamp()
)
NORM = r"trim(regexp_replace(lower(strip_accents({c})), '[^\pL\pN]+', ' ', 'g'))"
YEAR = r"(19[2-9][0-9]|20[0-2][0-9])"
# tên = phần trước năm; năm không được dính "p" (1080p) hay "x" (1920x1080) hay chữ số
TITLE_YEAR = r"^(.+?)[\s._(\[-]+" + YEAR + r"(?:[^0-9px]|$)"
TV = r"(?i)(\bS\d{1,2}\s?E\d{1,3}\b|\bS\d{1,2}\b|season|сезон|серии|серия|episode|сериал)"

t0 = time.time()
con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite; SET sqlite_all_varchar = true;")
con.execute(f"ATTACH '{DB_PATH}' AS mdb (TYPE SQLITE, READ_ONLY);")

print("Reading torrents...")
con.execute(f"""
CREATE TABLE raw AS
SELECT CAST(id AS BIGINT) AS torrent_id, encode(name) AS name_raw,
       TRY_CAST(total_size AS BIGINT) AS total_size,
       TRY_CAST(discovered_on AS BIGINT) AS discovered_epoch
FROM mdb.torrents
WHERE TRY_CAST(discovered_on AS BIGINT) >= {to_epoch(WINDOW_START)}
  AND TRY_CAST(discovered_on AS BIGINT) <  {to_epoch(WINDOW_END)}
  AND TRY_CAST(total_size AS BIGINT) >= {MIN_TOTAL_MB} * 1e6
""")
n_raw = con.execute("SELECT count(*) FROM raw").fetchone()[0]
print(f"  {n_raw:,} torrents >= {MIN_TOTAL_MB}MB trong cửa sổ  ({time.time() - t0:.0f}s)")

# Tên không phải UTF-8: giải mã cp1251 bằng Python (ít, ~0.2%).
bad = con.execute("SELECT torrent_id, name_raw FROM raw WHERE TRY(decode(name_raw)) IS NULL").fetchall()
fixed = [(tid, bytes(raw).decode("cp1251", errors="replace")) for tid, raw in bad]
con.execute("CREATE TABLE fixed (torrent_id BIGINT, torrent_name VARCHAR)")
if fixed:
    con.executemany("INSERT INTO fixed VALUES (?, ?)", fixed)
print(f"  {len(fixed):,} tên giải mã lại bằng cp1251")

con.execute(rf"""
CREATE TABLE parsed AS
WITH named AS (
    SELECT r.torrent_id, coalesce(f.torrent_name, TRY(decode(r.name_raw))) AS torrent_name,
           r.total_size, r.discovered_epoch
    FROM raw r LEFT JOIN fixed f USING (torrent_id)
),
cleaned AS (
    SELECT *,
        regexp_replace(
            regexp_replace(torrent_name, '^(\s*(\[[^\]]*\]|【[^】]*】|www\.\S+\s*-?)\s*)+', ''),
            '\.(mkv|mp4|avi|ts|m4v|wmv|mov|mpg|iso)$', '', 'i') AS n
    FROM named
),
ty AS (
    SELECT *,
        regexp_replace(regexp_extract(n, '{TITLE_YEAR}', 1), '\[[^\]]*\]', ' ', 'g') AS name_title,
        TRY_CAST(regexp_extract(n, '{TITLE_YEAR}', 2) AS INTEGER) AS name_year
    FROM cleaned
    WHERE NOT regexp_matches(n, '{TV}')
)
SELECT * EXCLUDE (n) FROM ty WHERE name_year IS NOT NULL AND trim(name_title) <> ''
""")
n_parsed = con.execute("SELECT count(*) FROM parsed").fetchone()[0]
print(f"  {n_parsed:,} tên có dạng 'Tên ... Năm' (không phải phim bộ)  ({time.time() - t0:.0f}s)")

con.execute(rf"""
CREATE TABLE variants AS
SELECT DISTINCT torrent_id, name_year, v AS norm, k AS variant
FROM (
    SELECT torrent_id, name_year, name_title AS v, 1 AS k FROM parsed
    -- Biến thể 2 và 3 CHỈ dùng khi tên có chữ không phải Latin (tên song ngữ). Với tên thuần
    -- Latin, "phần Latin cuối" của "Teen ... (NEW 2015" là "NEW" -> ghép nhầm phim tên "New".
    UNION ALL  -- phần chữ Latin cuối: "Банды.Нью-Йорка.Gangs.of.New.York" -> "Gangs.of.New.York"
    SELECT torrent_id, name_year, regexp_extract(name_title, '([A-Za-z0-9][A-Za-z0-9 .,''&:!_-]*)$', 1), 2 FROM parsed
    WHERE regexp_matches(name_title, '[^\x00-\x7F]')
    UNION ALL  -- phần trước chữ Latin đầu tiên: "Парк Юрского периода"
    SELECT torrent_id, name_year, regexp_extract(name_title, '^([^A-Za-z]+)', 1), 3 FROM parsed
    WHERE regexp_matches(name_title, '[^\x00-\x7F]')
    UNION ALL  -- bỏ số rác đầu tên: "101209.Alpha.Dog" -> "Alpha.Dog"
    SELECT torrent_id, name_year, regexp_replace(name_title, '^\d{{5,}}[\s._-]+', ''), 4 FROM parsed
) x(torrent_id, name_year, v, k)
""")
con.execute(f"UPDATE variants SET norm = {NORM.format(c='norm')}")
con.execute("DELETE FROM variants WHERE norm = '' OR length(norm) < 2")

# Trùng tên trong khoảng ±1 năm -> "mơ hồ": vẫn ghi lựa chọn (đúng năm, nhiều vote nhất)
# nhưng gắn cờ để 05/09 loại ra. (Thử ưu tiên "đúng năm" chỉ khớp MagnetDB 43% -> không đủ tin.)
con.execute(f"""
CREATE TABLE hits AS
WITH cand AS (
    SELECT DISTINCT v.torrent_id, v.variant, v.norm, i.tconst AS imdb_id, i.num_votes,
           abs(i.start_year - v.name_year) AS year_diff
    FROM variants v
    JOIN read_parquet('{INDEX}') i ON i.norm = v.norm AND abs(i.start_year - v.name_year) <= 1
    SEMI JOIN (SELECT tconst FROM read_parquet('{CATALOG}') WHERE titleType = 'movie') c
         ON c.tconst = i.tconst
),
best_variant AS (
    SELECT * FROM cand
    QUALIFY variant = min(variant) OVER (PARTITION BY torrent_id)
),
scored AS (
    SELECT *,
           count(DISTINCT imdb_id) FILTER (WHERE year_diff = 0) OVER (PARTITION BY torrent_id) AS n_exact_year,
           count(DISTINCT imdb_id) OVER (PARTITION BY torrent_id) AS n_candidates
    FROM best_variant
)
SELECT torrent_id, imdb_id, variant, year_diff, num_votes, n_candidates,
       -- mơ hồ: trùng tên nhiều phim, HOẶC tên quá ngắn/chỉ là số ("New", "Web", "18", "100")
       -- của một phim ít người biết -> dễ là chữ thường gặp trong tên torrent, không phải tên phim
       n_candidates > 1
       OR ((length(norm) <= 3 OR regexp_matches(norm, '^[0-9 ]+$')) AND num_votes < 1000)
       -- tên một từ của phim gần như không ai biết ("Cricket", "Panorama"): thường là chữ chung
       OR (num_votes < 100 AND NOT contains(norm, ' ')) AS ambiguous
FROM scored
QUALIFY row_number() OVER (PARTITION BY torrent_id ORDER BY year_diff, num_votes DESC) = 1
""")

con.execute(f"""
COPY (
    SELECT p.torrent_id, h.imdb_id, p.torrent_name, p.name_title, p.name_year,
           p.total_size, p.discovered_epoch,
           make_timestamp(p.discovered_epoch * 1000000) AS discovered_at_utc,
           h.variant AS match_variant, h.year_diff, h.n_candidates, h.ambiguous
    FROM parsed p JOIN hits h USING (torrent_id)
) TO '{OUT.as_posix()}' (FORMAT PARQUET)
""")

n, n_movies = con.execute(f"SELECT count(*), count(DISTINCT imdb_id) FROM read_parquet('{OUT.as_posix()}')").fetchone()
print(f"\nWrote {OUT.relative_to(ROOT)}: {n:,} torrent ghép được -> {n_movies:,} phim  ({time.time() - t0:.0f}s)")
print(con.sql(f"""SELECT match_variant, count(*) n FROM read_parquet('{OUT.as_posix()}') GROUP BY 1 ORDER BY 1"""))
