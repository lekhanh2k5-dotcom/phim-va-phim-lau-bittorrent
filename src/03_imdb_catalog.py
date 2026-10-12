"""
Stage 2a: danh mục IMDb + chỉ mục tên (chỉ phụ thuộc IMDb, không phụ thuộc MagnetDB).

Đầu vào:  data_raw/imdb/title.basics | ratings | akas .tsv.gz
Đầu ra:
  data_clean/imdb_catalog.parquet      movie/tvMovie/video CÓ rating (~467k) — tập ứng viên
  data_clean/imdb_title_index.parquet  (tên chuẩn hóa, tconst, năm, vote): primaryTitle +
                                       originalTitle + mọi tên trong title.akas
  data_clean/imdb_movies_all.parquet   MỌI phim (titleType='movie', kể cả chưa có rating) —
                                       cho phần phân tích ngành điện ảnh (20_viz_imdb.py)

Chuẩn hóa tên (NORM) dùng chung cho mọi bước ghép: bỏ dấu, lowercase, ký tự không phải
chữ/số -> khoảng trắng.

Chạy:  python src/03_imdb_catalog.py
"""

from pathlib import Path
import sys
import time
import duckdb

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT     = Path(__file__).resolve().parent.parent
BASICS   = (ROOT / "data_raw/imdb/title.basics.tsv.gz").as_posix()
RATINGS  = (ROOT / "data_raw/imdb/title.ratings.tsv.gz").as_posix()
AKAS     = (ROOT / "data_raw/imdb/title.akas.tsv.gz").as_posix()
CATALOG  = ROOT / "data_clean/imdb_catalog.parquet"
INDEX    = ROOT / "data_clean/imdb_title_index.parquet"
ALL      = ROOT / "data_clean/imdb_movies_all.parquet"

# IMDb TSV: không có dấu nháy, null = \N
TSV  = "delim = '\t', quote = '', nullstr = '\\N', all_varchar = true, header = true"
NORM = r"trim(regexp_replace(lower(strip_accents({col})), '[^\pL\pN]+', ' ', 'g'))"

t0 = time.time()
con = duckdb.connect()
con.execute(f"""
COPY (
    SELECT b.tconst, b.titleType, b.primaryTitle, b.originalTitle,
           b.isAdult = '1' AS is_adult,
           TRY_CAST(b.startYear AS INTEGER) AS start_year,
           TRY_CAST(b.runtimeMinutes AS INTEGER) AS runtime_min,
           b.genres,
           CAST(r.averageRating AS DOUBLE) AS avg_rating,
           CAST(r.numVotes AS INTEGER) AS num_votes
    FROM read_csv('{BASICS}', {TSV}) b
    JOIN read_csv('{RATINGS}', {TSV}) r USING (tconst)
    WHERE b.titleType IN ('movie', 'tvMovie', 'video')
) TO '{CATALOG.as_posix()}' (FORMAT PARQUET);
""")
n_cat = con.execute(f"SELECT count(*) FROM read_parquet('{CATALOG.as_posix()}')").fetchone()[0]
print(f"Wrote {CATALOG.relative_to(ROOT)}  ({n_cat:,} titles, {time.time() - t0:.0f}s)")

con.execute(f"""
COPY (
    WITH cat AS (SELECT tconst, start_year, num_votes, primaryTitle, originalTitle
                 FROM read_parquet('{CATALOG.as_posix()}')),
    names AS (
        SELECT tconst, primaryTitle AS t FROM cat
        UNION ALL SELECT tconst, originalTitle FROM cat
        UNION ALL
        SELECT a.titleId, a.title
        FROM read_csv('{AKAS}', {TSV}) a
        SEMI JOIN cat ON a.titleId = cat.tconst
    )
    SELECT DISTINCT {NORM.format(col='n.t')} AS norm, n.tconst, c.start_year, c.num_votes
    FROM names n JOIN cat c USING (tconst)
    WHERE n.t IS NOT NULL
) TO '{INDEX.as_posix()}' (FORMAT PARQUET);
""")
n_idx, n_t = con.execute(f"SELECT count(*), count(DISTINCT tconst) FROM read_parquet('{INDEX.as_posix()}')").fetchone()
print(f"Wrote {INDEX.relative_to(ROOT)}  ({n_idx:,} tên cho {n_t:,} titles, {time.time() - t0:.0f}s)")

con.execute(f"""
COPY (
    SELECT b.tconst, b.primaryTitle AS title, b.originalTitle AS original_title,
           b.isAdult = '1' AS is_adult,
           TRY_CAST(b.startYear AS INTEGER) AS start_year,
           TRY_CAST(b.runtimeMinutes AS INTEGER) AS runtime_min,
           b.genres,
           CAST(r.averageRating AS DOUBLE) AS avg_rating,
           CAST(r.numVotes AS INTEGER) AS num_votes
    FROM read_csv('{BASICS}', {TSV}) b
    LEFT JOIN read_csv('{RATINGS}', {TSV}) r USING (tconst)
    WHERE b.titleType = 'movie'
) TO '{ALL.as_posix()}' (FORMAT PARQUET);
""")
n_all, n_rated = con.execute(f"SELECT count(*), count(num_votes) FROM read_parquet('{ALL.as_posix()}')").fetchone()
print(f"Wrote {ALL.relative_to(ROOT)}  ({n_all:,} phim, {n_rated:,} có rating, {time.time() - t0:.0f}s)")
