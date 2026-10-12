"""
Trích dữ liệu MagnetDB cho phần tổng quan hệ sinh thái torrent (notebooks/04_magnetdb) —
MỌI loại nội dung, không riêng phim.

Đầu ra (data_clean/):
  mdb_torrents_all.parquet   mọi torrent: id, tên (giải mã UTF-8, lỗi thì cp1251), dung lượng,
                             thời điểm phát hiện (UTC)
  mdb_files_sample.parquet   mẫu ngẫu nhiên ~1% bảng files (950M dòng): lấy 19.000 đoạn 500 id
                             liên tiếp rải đều -> phần mở rộng file, dung lượng, isVideo
  mdb_files_per_torrent.parquet  số file của mỗi torrent (quét covering index readme_index)

Chạy:  python src/10_extract_magnetdb_overview.py      (~5–15 phút)
"""

import random
import sqlite3
import sys
import time
from pathlib import Path

import duckdb
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT    = Path(__file__).resolve().parent.parent
DB      = ROOT / "data_raw/magnetdb/magnetdb_public.sqlite3"
DC      = ROOT / "data_clean"
CHUNKS, CHUNK_LEN, SEED = 19_000, 500, 42
t0 = time.time()

# ---- 1. Mọi torrent ---------------------------------------------------------------------------
con = duckdb.connect()
con.execute("INSTALL sqlite; LOAD sqlite; SET sqlite_all_varchar = true;")
con.execute(f"ATTACH '{DB.as_posix()}' AS mdb (TYPE SQLITE, READ_ONLY);")
con.execute("""
CREATE TABLE t AS
SELECT CAST(id AS BIGINT) AS torrent_id, encode(name) AS name_raw,
       TRY_CAST(total_size AS BIGINT) AS total_size,
       TRY_CAST(discovered_on AS BIGINT) AS discovered_epoch
FROM mdb.torrents
""")
bad = con.execute("SELECT torrent_id, name_raw FROM t WHERE TRY(decode(name_raw)) IS NULL").fetchall()
con.execute("CREATE TABLE fixed (torrent_id BIGINT, name VARCHAR)")
if bad:
    con.executemany("INSERT INTO fixed VALUES (?, ?)",
                    [(i, bytes(r).decode("cp1251", errors="replace")) for i, r in bad])
con.execute(f"""
COPY (
    SELECT t.torrent_id, coalesce(f.name, TRY(decode(t.name_raw))) AS name, t.total_size,
           t.discovered_epoch, make_timestamp(t.discovered_epoch * 1000000) AS discovered_at_utc
    FROM t LEFT JOIN fixed f USING (torrent_id)
) TO '{(DC / "mdb_torrents_all.parquet").as_posix()}' (FORMAT PARQUET)
""")
n = con.execute("SELECT count(*) FROM t").fetchone()[0]
print(f"1. {n:,} torrent ({len(bad):,} tên giải mã cp1251)  {time.time() - t0:.0f}s", flush=True)

# ---- 2. Mẫu bảng files -----------------------------------------------------------------------------
sq = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
sq.text_factory = bytes                       # đường dẫn có thể không phải UTF-8
max_id = sq.execute("SELECT max(id) FROM files").fetchone()[0]
random.seed(SEED)
starts = sorted(random.sample(range(1, max_id - CHUNK_LEN), CHUNKS))
rows = []
for s in starts:
    rows += sq.execute("SELECT torrent_id, path, size, isVideo FROM files WHERE id BETWEEN ? AND ?",
                       (s, s + CHUNK_LEN - 1)).fetchall()
fs = pd.DataFrame(rows, columns=["torrent_id", "path", "size", "is_video"])
name = fs["path"].map(lambda b: b.decode("utf-8", errors="replace").rsplit("/", 1)[-1])
fs["ext"] = name.str.extract(r"\.([A-Za-z0-9]{1,6})$", expand=False).str.lower()
fs["size"] = pd.to_numeric(fs["size"], errors="coerce")
fs["is_video"] = pd.to_numeric(fs["is_video"], errors="coerce").fillna(0).astype("int8")
fs.drop(columns="path").to_parquet(DC / "mdb_files_sample.parquet", index=False)
print(f"2. {len(fs):,} file mẫu ({len(fs) / max_id:.2%} của {max_id:,})  {time.time() - t0:.0f}s", flush=True)

# ---- 3. Số file mỗi torrent (covering index, không đọc bảng) ----------------------------------------
cur = sq.execute("SELECT torrent_id, count(*) FROM files GROUP BY torrent_id")
parts = []
while batch := cur.fetchmany(2_000_000):
    parts.append(pd.DataFrame(batch, columns=["torrent_id", "n_files"]))
pd.concat(parts).to_parquet(DC / "mdb_files_per_torrent.parquet", index=False)
print(f"3. số file cho {sum(len(p) for p in parts):,} torrent  {time.time() - t0:.0f}s", flush=True)
