"""
Stage 2c: danh sách PHIM từ cả hai nguồn ghép.

Nguồn:
  - MagnetDB: data_clean/matched_files.parquet (movieMatchTitleId, matchScore > 138)
  - Tự ghép tên torrent: data_clean/name_matches.parquet (bỏ các ca "mơ hồ")
Chỉ giữ titleType = 'movie'.

Đầu ra: data_clean/movies.parquet — 1 dòng / phim: thông tin IMDb + số torrent theo nguồn
        (thô, trước làm sạch). Dùng cho 06_fetch_tmdb (danh sách gọi API) và 09.

Chạy:  python src/05_build_movie_list.py
"""

from pathlib import Path
import sys
import duckdb

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT     = Path(__file__).resolve().parent.parent
BASICS   = (ROOT / "data_raw/imdb/title.basics.tsv.gz").as_posix()
RATINGS  = (ROOT / "data_raw/imdb/title.ratings.tsv.gz").as_posix()
FILES_PQ = (ROOT / "data_clean/matched_files.parquet").as_posix()
NAMES_PQ = (ROOT / "data_clean/name_matches.parquet").as_posix()
MOVIES   = ROOT / "data_clean/movies.parquet"

TSV = "delim = '\t', quote = '', nullstr = '\\N', all_varchar = true, header = true"

con = duckdb.connect()
con.execute(f"""
COPY (
    WITH mdb AS (
        SELECT imdb_id, count(DISTINCT torrent_id) AS n_torrents_magnetdb
        FROM read_parquet('{FILES_PQ}') GROUP BY imdb_id
    ),
    nm AS (
        SELECT imdb_id, count(*) AS n_torrents_name_match
        FROM read_parquet('{NAMES_PQ}') WHERE NOT ambiguous GROUP BY imdb_id
    ),
    ids AS (SELECT imdb_id FROM mdb UNION SELECT imdb_id FROM nm)
    SELECT b.tconst AS imdb_id, b.primaryTitle AS title, b.originalTitle AS original_title,
           TRY_CAST(b.startYear AS INTEGER) AS start_year,
           TRY_CAST(b.runtimeMinutes AS INTEGER) AS runtime_min,
           b.genres, b.isAdult = '1' AS is_adult,
           CAST(r.averageRating AS DOUBLE) AS avg_rating, CAST(r.numVotes AS INTEGER) AS num_votes,
           coalesce(mdb.n_torrents_magnetdb, 0) AS n_torrents_magnetdb,
           coalesce(nm.n_torrents_name_match, 0) AS n_torrents_name_match
    FROM ids
    JOIN read_csv('{BASICS}', {TSV}) b ON b.tconst = ids.imdb_id
    LEFT JOIN read_csv('{RATINGS}', {TSV}) r ON r.tconst = ids.imdb_id
    LEFT JOIN mdb USING (imdb_id)
    LEFT JOIN nm USING (imdb_id)
    WHERE b.titleType = 'movie'
      -- bỏ mục IMDb chỉ là sự kiện/chương trình (vd. "UEFA Champions League Final", thể loại
      -- chỉ có Sport): torrent trận bóng khớp tên nhưng đây không phải phim
      AND NOT list_has_all(['Sport', 'News', 'Reality-TV', 'Talk-Show', 'Game-Show'],
                           string_split(coalesce(b.genres, 'x'), ','))
    ORDER BY num_votes DESC NULLS LAST
) TO '{MOVIES.as_posix()}' (FORMAT PARQUET);
""")

print(f"Wrote {MOVIES.relative_to(ROOT)}")
print(con.sql(f"""
    SELECT count(*) AS movies,
           count(*) FILTER (WHERE n_torrents_magnetdb > 0)   AS from_magnetdb,
           count(*) FILTER (WHERE n_torrents_name_match > 0) AS from_name_match,
           count(*) FILTER (WHERE n_torrents_magnetdb > 0 AND n_torrents_name_match > 0) AS both,
           count(*) FILTER (WHERE start_year >= 2019)        AS released_2019_plus,
           count(*) FILTER (WHERE num_votes >= 1000)         AS votes_1k
    FROM read_parquet('{MOVIES.as_posix()}')
"""))
