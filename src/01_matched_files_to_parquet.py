"""
MagnetDB - Stage 0a: matchedVideos_sample.csv -> Parquet (KHÔNG cần file .db).

Theo tài liệu MagnetDB, matchedVideos_sample.csv không phải mẫu ngẫu nhiên mà là
TOÀN BỘ các dòng của bảng files thỏa isVideo = 1 AND matchScore > 138
(1,562,572 dòng). Vì vậy phần "file + match IMDb" đã có sẵn, chỉ thiếu thời gian
(discovered_on nằm trong bảng torrents -> xem 02_extract_torrent_times.py).

Đầu ra: data_clean/matched_files.parquet  (1 dòng = 1 FILE video, không phải 1 torrent)

Chạy:  python src/01_matched_files_to_parquet.py
"""

from pathlib import Path
import sys
import duckdb

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT     = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data_raw/magnetdb/matchedVideos_sample.csv"
OUT_PATH = ROOT / "data_clean/matched_files.parquet"

con = duckdb.connect()
con.execute(f"""
COPY (
    SELECT
        CAST(id AS BIGINT)            AS file_id,
        CAST(torrent_id AS BIGINT)    AS torrent_id,
        CAST(size AS BIGINT)          AS file_size,
        path,
        movieMatchTitleId             AS imdb_id,        -- IMDb ttID = ground-truth match
        movieMatchTitle               AS match_title,
        CAST(matchScore AS DOUBLE)    AS match_score,
        title                         AS parsed_title,   -- tách từ tên file (có thể lỗi mã hóa)
        TRY_CAST(year AS INTEGER)     AS parsed_year,
        quality,                                         -- WEBRip / BDRip / CAM ...
        resolution,
        codec,
        language,
        season,
        episode,
        (season IS NOT NULL OR episode IS NOT NULL) AS is_tv_hint,  -- lọc chính thức bằng IMDb titleType
        genre,
        network,
        encoder,
        site,
        website,
        filetype,
        CAST(encodingError AS INTEGER) AS encoding_error
    FROM read_csv('{CSV_PATH.as_posix()}', all_varchar = true, nullstr = 'NA',
                  header = true, quote = '"', escape = '"', strict_mode = false)
) TO '{OUT_PATH.as_posix()}' (FORMAT PARQUET);
""")

n, n_torrents, n_titles, n_tv = con.execute(f"""
    SELECT count(*), count(DISTINCT torrent_id), count(DISTINCT imdb_id), sum(is_tv_hint::INT)
    FROM read_parquet('{OUT_PATH.as_posix()}')
""").fetchone()

print(f"Wrote {OUT_PATH.relative_to(ROOT)}")
print(f"  file rows:            {n:,}   (tài liệu: 1,562,572)")
print(f"  distinct torrents:    {n_torrents:,}")
print(f"  distinct IMDb titles: {n_titles:,}")
print(f"  rows có season/ep:    {n_tv:,}   (gợi ý TV)")
