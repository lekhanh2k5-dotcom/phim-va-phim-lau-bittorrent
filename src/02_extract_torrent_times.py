"""
MagnetDB - Stage 0b: lấy thời gian (discovered_on) từ bảng torrents trong file .db
và ghép với matched_files.parquet (đầu ra của 01_matched_files_to_parquet.py).

Chỉ đọc bảng torrents (28.6M dòng), KHÔNG quét bảng files (950M dòng) vì phần
file + match đã có sẵn trong matchedVideos_sample.csv -> nhanh hơn rất nhiều.

Đầu ra:
  data_clean/torrents_matched.parquet        mọi torrent có file khớp IMDb (toàn thời gian)
  data_clean/magnetdb_matched_slice.parquet  file video x thời gian, trong cửa sổ phân tích

Chạy:
  python src/02_extract_torrent_times.py --test     # thử 100k dòng torrents trước
  python src/02_extract_torrent_times.py            # chạy thật
  python src/02_extract_torrent_times.py --verify   # + đếm lại trong bảng files để xác nhận
                                                    #   CSV đã đủ (quét 950M dòng, rất lâu)
"""

import argparse
import datetime
from pathlib import Path
import sys
import duckdb

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT        = Path(__file__).resolve().parent.parent
DB_DIR      = ROOT / "data_raw/magnetdb"
FILES_PQ    = ROOT / "data_clean/matched_files.parquet"
TORRENTS_PQ = ROOT / "data_clean/torrents_matched.parquet"
SLICE_PQ    = ROOT / "data_clean/magnetdb_matched_slice.parquet"

# ---- Config (tune these) ------------------------------------------------
MIN_MATCH_SCORE = 138          # ngưỡng tin cậy của MagnetDB (CSV đã lọc sẵn > 138)
WINDOW_START    = "2019-04-01" # bắt đầu SAU đợt "burn-in" đầu 2019 của crawler DHT
WINDOW_END      = "2024-09-30" # thu thập kết thúc 2024-09-29
# -------------------------------------------------------------------------

ap = argparse.ArgumentParser()
ap.add_argument("--test", action="store_true", help="chỉ đọc 100k dòng torrents đầu tiên")
ap.add_argument("--verify", action="store_true", help="đối chiếu số dòng CSV với bảng files")
ap.add_argument("--db", help="đường dẫn file SQLite (mặc định: tự dò trong data_raw/magnetdb)")
args = ap.parse_args()

# Tên file sau khi giải nén .tar.zst chưa chắc chắn -> tự dò.
candidates = [p for ext in ("*.db", "*.sqlite3", "*.sqlite") for p in DB_DIR.rglob(ext)]
if not args.db and not candidates:
    raise SystemExit(f"Không tìm thấy file SQLite trong {DB_DIR}. Đã giải nén .tar.zst chưa?")
DB_PATH = Path(args.db) if args.db else max(candidates, key=lambda p: p.stat().st_size)
if not FILES_PQ.exists():
    raise SystemExit("Chưa có matched_files.parquet -> chạy src/01_matched_files_to_parquet.py trước.")
print(f"DB: {DB_PATH}  ({DB_PATH.stat().st_size / 1e9:.1f} GB)")

to_epoch = lambda d: int(
    datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).timestamp()
)
start_epoch, end_epoch = to_epoch(WINDOW_START), to_epoch(WINDOW_END)

con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite;")
con.execute(f"ATTACH '{DB_PATH.as_posix()}' AS mdb (TYPE SQLITE, READ_ONLY);")
con.execute(f"CREATE TEMP TABLE ids AS SELECT DISTINCT torrent_id FROM read_parquet('{FILES_PQ.as_posix()}')")

limit = "LIMIT 100000" if args.test else ""
torrents_sql = f"""
    SELECT CAST(id AS BIGINT) AS torrent_id, encode(name) AS name_raw,  -- byte thô, giải mã sau
           TRY_CAST(total_size AS BIGINT) AS total_size,
           TRY_CAST(discovered_on AS BIGINT) AS discovered_epoch
    FROM (SELECT * FROM mdb.torrents {limit})
"""

# SQLite không ép kiểu: một ô text trong cột INTEGER làm DuckDB báo lỗi mismatch.
# Gặp lỗi đó thì đọc mọi cột dạng VARCHAR rồi TRY_CAST (đã có ở trên).
print("Reading torrents table" + (" (TEST: 100k rows)" if args.test else " (28.6M rows)") + "...")
try:
    con.execute(f"CREATE TEMP TABLE t AS {torrents_sql}")
except duckdb.Error as e:
    print(f"  type error ({e.__class__.__name__}) -> retry with sqlite_all_varchar")
    con.execute("SET sqlite_all_varchar = true;")
    con.execute(f"CREATE TEMP TABLE t AS {torrents_sql}")

tor = con.execute("""
    SELECT t.*, make_timestamp(t.discovered_epoch * 1000000) AS discovered_at_utc  -- UTC, không múi giờ
    FROM t SEMI JOIN ids USING (torrent_id)
""").df()


# Một số tên torrent không phải UTF-8 mà là Windows-1251 (tiếng Nga), vd.
# b"\xC1\xF0\xE0\xF2\xF1\xF2\xE2\xEE" = "Братство". Thử UTF-8 trước, hỏng thì cp1251.
def decode_name(raw):
    if raw is None:
        return None, None
    raw = bytes(raw)
    try:
        return raw.decode("utf-8"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("cp1251", errors="replace"), "cp1251"


tor[["torrent_name", "name_encoding"]] = [decode_name(r) for r in tor.pop("name_raw")]
tor.to_parquet(TORRENTS_PQ, index=False)
print(f"  tên torrent không phải UTF-8 (đã giải mã cp1251): {(tor['name_encoding'] == 'cp1251').sum():,}")

con.execute(f"""
COPY (
    SELECT f.*, t.torrent_name, t.total_size, t.discovered_epoch, t.discovered_at_utc
    FROM read_parquet('{FILES_PQ.as_posix()}') f
    JOIN read_parquet('{TORRENTS_PQ.as_posix()}') t USING (torrent_id)
    WHERE f.match_score > {MIN_MATCH_SCORE}
      AND t.discovered_epoch >= {start_epoch}
      AND t.discovered_epoch <  {end_epoch}
) TO '{SLICE_PQ.as_posix()}' (FORMAT PARQUET);
""")

# ---- Verify -------------------------------------------------------------
n_ids = con.execute("SELECT count(*) FROM ids").fetchone()[0]
n_t, n_null, tmin, tmax = con.execute(f"""
    SELECT count(*), count(*) - count(discovered_epoch), min(discovered_at_utc), max(discovered_at_utc)
    FROM read_parquet('{TORRENTS_PQ.as_posix()}')
""").fetchone()
n_rows, n_tor, n_titles, dmin, dmax = con.execute(f"""
    SELECT count(*), count(DISTINCT torrent_id), count(DISTINCT imdb_id),
           min(discovered_at_utc), max(discovered_at_utc)
    FROM read_parquet('{SLICE_PQ.as_posix()}')
""").fetchone()

print(f"\nWrote {TORRENTS_PQ.relative_to(ROOT)}")
print(f"  torrents found:       {n_t:,} / {n_ids:,} torrent_id trong CSV"
      + ("" if args.test else f"  ({n_ids - n_t:,} không tìm thấy)"))
print(f"  thiếu discovered_on:  {n_null:,}")
print(f"  discovery range:      {tmin}  ->  {tmax}")
print(f"\nWrote {SLICE_PQ.relative_to(ROOT)}  (cửa sổ {WINDOW_START} -> {WINDOW_END})")
print(f"  file rows:            {n_rows:,}")
print(f"  distinct torrents:    {n_tor:,}")
print(f"  distinct IMDb titles: {n_titles:,}")
print(f"  discovery range:      {dmin}  ->  {dmax}")

if args.verify:
    print("\nVerifying CSV completeness against files table (scans 950M rows, slow)...")
    n_db = con.execute(f"""
        SELECT count(*) FROM mdb.files
        WHERE isVideo = 1 AND matchScore > {MIN_MATCH_SCORE}
    """).fetchone()[0]
    print(f"  files table: {n_db:,}  vs  CSV: 1,562,572  -> {'KHỚP' if n_db == 1562572 else 'LỆCH'}")

print("\nNext: join imdb_id -> IMDb title.basics (titleType='movie') + ratings.")
