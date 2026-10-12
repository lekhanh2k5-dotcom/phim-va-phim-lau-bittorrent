"""
Stage 3: làm sạch + gộp hai nguồn ghép + dựng bảng phân tích.

NGUỒN 1 — MagnetDB (mã phim movieMatchTitleId, cấp FILE), lọc bỏ các ca gán sai rõ ràng:
  A. Chỉ giữ PHIM (IMDb titleType = 'movie').
  B. Bỏ file có số mùa/tập (S01E02...) -> tập phim bộ bị gán nhầm vào phim lẻ cùng tên.
  C. Bỏ file < 100MB -> clip, trailer, sample, không phải bản phim.
  D. Năm ghi trong tên file (nếu có) phải khớp năm phim ±1, vd. "Великолепная Пятерка 2019"
     (phim bộ Nga) -> Gang of Roses (2003).
  E. Tên tách từ file phải giống ÍT NHẤT MỘT tên của phim (tên gốc, tên tiếng Anh, tên theo
     từng nước trong title.akas, tên Nga chuyển chữ Latin) >= SIM_MIN (60). Loại
     "1. Introduction.mp4" -> The Intruder, "VTS_01_1.VOB"... Cờ `strict` = >= SIM_STRICT (75).
  E2. Số PHẦN phim phải khớp: tên file kết thúc bằng 2-9 / II-IX mà không tên nào của phim
     chứa số đó -> sai phần, vd. "Mockingjay Part 2" -> Part 1, "Пункт назначения 4" -> phần 1.

NGUỒN 2 — tự ghép tên torrent (04_match_torrent_names.py, cấp TORRENT): tên + năm khớp
  chính xác một phim IMDb duy nhất; bỏ các ca "mơ hồ" (nhiều phim trùng tên ±1 năm).

CHUNG cho cả hai (cấp torrent):
  F. Torrent không thể xuất hiện TRƯỚC khi phim tồn tại: bỏ nếu phát hiện sớm hơn
     PRE_RELEASE_DAYS (60) ngày so với lần ra mắt sớm nhất trên TMDb (kể cả liên hoan phim),
     hoặc trước năm sản xuất IMDb - 1 nếu thiếu ngày.
  G. Hai nguồn MÂU THUẪN (torrent 1 phim, MagnetDB nói X, tên torrent nói Y) -> bỏ cả hai.
  H. Tên torrent có từ khóa phim bộ (Season, Сезон, S01...) -> bỏ.
  I. Tên torrent ghi năm nhưng không năm nào khớp năm phim ±1 (trừ gói nhiều phim) -> bỏ.
  J. Bản chất lượng X không thể có trước ngày phát hành định dạng X: WEB trước ngày Digital,
     BluRay trước ngày Digital/đĩa, bất kỳ bản nào trước lần ra mắt đầu tiên -> torrent giả.
     Giữ trong torrents_clean (cờ `implausible`) nhưng không tính vào movie_analysis.
  Gói nhiều phim (`is_pack`): torrent ghép ra >1 phim, hoặc tên có "Trilogy", "Collection",
  "Сборник", khoảng năm "1984-2009"...

Đầu ra:
  data_clean/torrents_clean.parquet   1 dòng = 1 cặp (torrent, phim) sau làm sạch
  data_clean/movie_analysis.parquet   1 dòng = 1 phim: IMDb + TMDb + thống kê torrent
  data_clean/cleaning_log.csv         số dòng còn lại sau từng bước lọc (đưa vào báo cáo)

Cửa sổ phân tích ổn định của crawler: 2021-04-01 -> 2024-09-29 (xem README mục 9).

Chạy:  python src/09_build_tables.py
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

import duckdb
import pandas as pd
from rapidfuzz import fuzz

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT     = Path(__file__).resolve().parent.parent
DC       = ROOT / "data_clean"
SLICE    = (DC / "magnetdb_matched_slice.parquet").as_posix()
NAMES_PQ = (DC / "name_matches.parquet").as_posix()
MOVIES   = (DC / "movies.parquet").as_posix()
TMDB     = (DC / "tmdb_movies.parquet").as_posix()
RELDATES = (DC / "tmdb_release_dates.parquet").as_posix()
INDEX    = (DC / "imdb_title_index.parquet").as_posix()

MIN_FILE_MB      = 100
PRE_RELEASE_DAYS = 60   # torrent sớm hơn lần ra mắt đầu tiên quá số ngày này = gán nhầm
SIM_MIN          = 60
SIM_STRICT       = 75
STABLE_START     = "2021-04-01"
STABLE_END       = "2024-09-29"

NORM = r"trim(regexp_replace(lower(strip_accents({c})), '[^\pL\pN]+', ' ', 'g'))"

# Chất lượng bản phát hành (cột quality của MagnetDB) -> nhóm
QUALITY_TIER = {
    "Cam": "pre_release", "Telesync": "pre_release", "Telecine": "pre_release",
    "Workprint": "pre_release", "Screener": "pre_release",
    "WEB-DL": "web", "WEBRip": "web", "WEBCap": "web", "VODRip": "web",
    "Digital Distribution Copy": "web", "HD-Rip": "web",
    "Blu-ray": "disc", "BDRip": "disc", "BRRip": "disc", "DVD-Rip": "disc",
    "DVD-R": "disc", "HD DVD": "disc",
    "HDTV": "tv", "DSRip": "tv", "PDTV": "tv", "TVRip": "tv", "AHDTV": "tv",
    "Pay-Per-View Rip": "tv",
}
# Cùng các nhóm đó, nhận diện từ TÊN torrent (khi MagnetDB không có nhãn quality)
NAME_TIER = [
    ("pre_release", r"(?i)\b(?:hd)?(?:cam|camrip|ts|telesync|tc|telecine|scr|dvdscr|screener|predvd|workprint)\b"),
    ("web",         r"(?i)\b(?:web[-. ]?dl|webrip|web|amzn|nf|dsnp|hmax|itunes|hdrip)\b"),
    ("disc",        r"(?i)\b(?:blu-?ray|bdrip|brrip|bdremux|remux|bd|dvdrip|dvd5|dvd9|dvd)\b"),
    ("tv",          r"(?i)\b(?:hdtv|satrip|tvrip|dsrip|pdtv|iptvrip)\b"),
]
TV_WORDS   = r"(?i)(\bS\d{1,2}\s?E\d{1,3}\b|\bS\d{1,2}\b|season|сезон|серии|серия|episode|сериал)"
PACK_WORDS = re.compile(r"(?i)(?:trilog|quadrilog|duolog|dilog|antholog|collection|colecci|coleç|"
                        r"collezion|сборник|коллекц|трилог|дилог|антолог|boxset|box set|"
                        r"complete|合集|全集|saga\b|\b\d\s?-\s?\d\b)")
YEAR_RANGE = re.compile(r"(?<!\d)(?:19|20)\d\d\s*[-–]\s*(?:19|20)\d\d(?!\d)")
YEARS      = re.compile(r"(?<![\dx])(19[2-9]\d|20[0-2]\d)(?![\dpx])", re.I)

con = duckdb.connect()
log = []


def step(source, name, table, file_level=True):
    q = (f"SELECT count(*), count(DISTINCT torrent_id), count(DISTINCT imdb_id) FROM {table}")
    files, tors, movies = con.execute(q).fetchone()
    log.append({"source": source, "step": name, "files": files if file_level else None,
                "torrents": tors, "movies": movies})
    shown = f"files={files:>9,}  " if file_level else " " * 17
    print(f"  {name:<52} {shown}torrents={tors:>9,}  movies={movies:>7,}")


con.execute(f"""
    CREATE TABLE first_release AS
    SELECT m.imdb_id, m.start_year,
           least(min(r.release_date), any_value(t.release_date)) AS earliest_release
    FROM read_parquet('{MOVIES}') m
    LEFT JOIN read_parquet('{RELDATES}') r USING (imdb_id)
    LEFT JOIN read_parquet('{TMDB}') t USING (imdb_id)
    GROUP BY m.imdb_id, m.start_year
""")
NOT_BEFORE_RELEASE = f"""
    CASE WHEN r.earliest_release IS NOT NULL
         THEN x.discovered_at_utc >= r.earliest_release - INTERVAL {PRE_RELEASE_DAYS} DAY
         WHEN r.start_year IS NOT NULL
         THEN year(x.discovered_at_utc) >= r.start_year - 1
         ELSE TRUE END"""

# =========================== NGUỒN 1: MagnetDB =============================
print("Nguồn 1 — MagnetDB (cấp file):")
con.execute(f"CREATE TABLE f0 AS SELECT * FROM read_parquet('{SLICE}')")
step("magnetdb", "0. slice 2019-04 -> 2024-09 (mọi loại)", "f0")
con.execute(f"CREATE TABLE f1 AS SELECT * FROM f0 SEMI JOIN read_parquet('{MOVIES}') USING (imdb_id)")
step("magnetdb", "A. chỉ PHIM (titleType=movie)", "f1")
con.execute("CREATE TABLE f2 AS SELECT * FROM f1 WHERE NOT is_tv_hint")
step("magnetdb", "B. bỏ file có số mùa/tập", "f2")
con.execute(f"CREATE TABLE f2b AS SELECT * FROM f2 WHERE file_size >= {MIN_FILE_MB} * 1e6")
step("magnetdb", f"C. bỏ file < {MIN_FILE_MB}MB", "f2b")
con.execute(f"""
    CREATE TABLE f3 AS SELECT f.* FROM f2b f JOIN read_parquet('{MOVIES}') m USING (imdb_id)
    WHERE f.parsed_year IS NULL OR m.start_year IS NULL OR abs(f.parsed_year - m.start_year) <= 1
""")
step("magnetdb", "D. năm trong tên file khớp năm phim (±1)", "f3")

# ---- E / E2. Độ giống tên + số phần --------------------------------------------
CYR = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
LAT = ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "i", "k", "l", "m", "n", "o", "p",
       "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "iu", "ia"]
TRANSLIT = dict(zip(CYR, LAT))
ROMAN = {"ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9"}

names = defaultdict(set)
for tconst, norm in con.execute(f"""
        SELECT tconst, norm FROM read_parquet('{INDEX}')
        SEMI JOIN read_parquet('{MOVIES}') m ON tconst = m.imdb_id
        UNION ALL   -- phim không có trong chỉ mục (chưa có rating) vẫn có tên chính
        SELECT imdb_id, {NORM.format(c='title')} FROM read_parquet('{MOVIES}')
        UNION ALL
        SELECT imdb_id, {NORM.format(c='original_title')} FROM read_parquet('{MOVIES}')
        """).fetchall():
    if not norm:
        continue
    names[tconst].add(norm)
    if re.search("[а-я]", norm):   # tên Nga -> thêm bản Latin ("хоббит" -> "khobbit")
        names[tconst].add("".join(TRANSLIT.get(ch, ch) for ch in norm))


def sequel_number(text):
    """Số phần ở CUỐI tên ("mockingjay part 2", "пункт назначения 4", "rocky iii") -> "2"/"4"/"3"."""
    last = text.split()[-1] if text.split() else ""
    if last.isdigit() and 2 <= int(last) <= 9:
        return last
    return ROMAN.get(last)


def has_number(name, num):
    tokens = name.split()
    return num in tokens or any(ROMAN.get(t) == num for t in tokens)


# Tên lấy từ MagnetDB parsed_title (phần sau dấu "/" cuối); trống thì dùng tên file. {p} = alias bảng.
PT = ("coalesce(nullif(" + NORM.format(c="split_part({p}parsed_title, '/', -1)") + ", ''), "
      + NORM.format(c="regexp_replace(split_part({p}path, '/', -1), '[.][^.]+$', '')") + ")")
pairs = con.execute(f"SELECT DISTINCT imdb_id, {PT.format(p='')} AS pt FROM f3").df()
pairs["title_sim"] = [max((fuzz.token_set_ratio(pt, n) for n in names.get(i, ())), default=0)
                      for i, pt in zip(pairs["imdb_id"], pairs["pt"])]
seq = [sequel_number(pt) for pt in pairs["pt"]]
pairs["sequel_ok"] = [s is None or any(has_number(n, s) for n in names.get(i, ()))
                      for i, s in zip(pairs["imdb_id"], seq)]
con.register("pairs", pairs)
con.execute(f"""
    CREATE TABLE f4 AS
    SELECT f.*, p.title_sim, p.title_sim >= {SIM_STRICT} AS strict, p.sequel_ok
    FROM f3 f JOIN pairs p ON p.imdb_id = f.imdb_id AND p.pt = {PT.format(p='f.')}
    WHERE p.title_sim >= {SIM_MIN}
""")
step("magnetdb", f"E. tên file giống tên phim >= {SIM_MIN}", "f4")
con.execute("CREATE TABLE f4b AS SELECT * FROM f4 WHERE sequel_ok")
step("magnetdb", "E2. số phần phim khớp (Part 2 ≠ Part 1)", "f4b")

tier_case = "CASE quality " + " ".join(f"WHEN '{q}' THEN '{t}'" for q, t in QUALITY_TIER.items()) \
            + " ELSE NULL END"
con.execute(f"""
CREATE TABLE tor_m AS
SELECT torrent_id, imdb_id,
       any_value(discovered_at_utc) AS discovered_at_utc,
       any_value(torrent_name)      AS torrent_name,
       any_value(total_size)        AS total_size,
       count(*)                     AS n_files,
       -- ưu tiên nhãn "pre_release" nếu có file nào là CAM/TS
       coalesce(max({tier_case}) FILTER (WHERE {tier_case} = 'pre_release'), max({tier_case})) AS file_tier,
       any_value(language)          AS language,
       max(title_sim)               AS title_sim,
       bool_or(strict)              AS strict
FROM f4b GROUP BY torrent_id, imdb_id
""")
step("magnetdb", "   -> cặp (torrent, phim)", "tor_m", file_level=False)
# Lưu nguồn 1 sau làm sạch, TRƯỚC khi gộp — để đo độ đồng thuận độc lập với nguồn 2
con.execute(f"COPY (SELECT torrent_id, imdb_id FROM tor_m) TO '{(DC / 'magnetdb_clean_pairs.parquet').as_posix()}' (FORMAT PARQUET)")

# =========================== NGUỒN 2: tên torrent ===========================
print("\nNguồn 2 — tự ghép tên torrent (cấp torrent):")
con.execute(f"""CREATE TABLE n0 AS SELECT * FROM read_parquet('{NAMES_PQ}')""")
step("name_match", "0. ghép được (tên + năm khớp IMDb)", "n0", file_level=False)
con.execute(f"CREATE TABLE n1 AS SELECT * FROM n0 WHERE NOT ambiguous")
step("name_match", "bỏ ca mơ hồ (>1 phim trùng tên ±1 năm)", "n1", file_level=False)
con.execute(f"CREATE TABLE tor_n AS SELECT * FROM n1 SEMI JOIN read_parquet('{MOVIES}') USING (imdb_id)")
step("name_match", "A. chỉ PHIM (titleType=movie)", "tor_n", file_level=False)

# =========================== GỘP + lọc chung ================================
print("\nGộp hai nguồn (cấp torrent):")
con.execute("""
CREATE TABLE u0 AS
SELECT coalesce(m.torrent_id, n.torrent_id) AS torrent_id,
       coalesce(m.imdb_id, n.imdb_id)       AS imdb_id,
       coalesce(m.discovered_at_utc, n.discovered_at_utc) AS discovered_at_utc,
       coalesce(m.torrent_name, n.torrent_name) AS torrent_name,
       coalesce(m.total_size, n.total_size)  AS total_size,
       m.n_files, m.file_tier, m.language, m.title_sim,
       coalesce(m.strict, TRUE) AS strict,   -- ghép tên torrent = khớp chính xác tên
       CASE WHEN m.torrent_id IS NOT NULL AND n.torrent_id IS NOT NULL THEN 'both'
            WHEN m.torrent_id IS NOT NULL THEN 'magnetdb' ELSE 'name_match' END AS source
FROM tor_m m FULL OUTER JOIN tor_n n USING (torrent_id, imdb_id)
""")
step("combined", "hợp hai nguồn", "u0", file_level=False)

con.execute(f"""
CREATE TABLE u1 AS SELECT x.* FROM u0 x JOIN first_release r USING (imdb_id)
WHERE {NOT_BEFORE_RELEASE}
""")
step("combined", f"F. không xuất hiện trước ra mắt > {PRE_RELEASE_DAYS} ngày", "u1", file_level=False)

# G. Mâu thuẫn: torrent mà MagnetDB chỉ gán 1 phim, tên torrent lại ra phim khác.
con.execute("""
CREATE TABLE conflict AS
SELECT torrent_id FROM u1
GROUP BY torrent_id
HAVING count(DISTINCT imdb_id) FILTER (WHERE source IN ('magnetdb', 'both')) = 1
   AND count(DISTINCT imdb_id) FILTER (WHERE source = 'name_match') >= 1
   AND count(*) FILTER (WHERE source = 'both') = 0
""")
con.execute("CREATE TABLE u2 AS SELECT * FROM u1 ANTI JOIN conflict USING (torrent_id)")
step("combined", "G. bỏ torrent hai nguồn mâu thuẫn", "u2", file_level=False)

con.execute(f"CREATE TABLE u3 AS SELECT * FROM u2 WHERE NOT regexp_matches(coalesce(torrent_name, ''), '{TV_WORDS}')")
step("combined", "H. bỏ tên torrent có từ khóa phim bộ", "u3", file_level=False)

# I + pack + quality từ tên: xử lý bằng Python (regex có lookaround)
u = con.execute("""SELECT u3.*, m.start_year, count(*) OVER (PARTITION BY torrent_id) AS n_movies_in_torrent
                   FROM u3 JOIN read_parquet('""" + MOVIES + """') m USING (imdb_id)""").df()
name = u["torrent_name"].fillna("")
# Bỏ đuôi file và tên trang web trước khi dò từ khóa chất lượng: ".ts" là định dạng file,
# "www.5MovieRulz.tc" là tên miền — không phải bản TeleSync / TeleCine.
name_noext = (name.str.replace(r"(?i)\.(mkv|mp4|avi|ts|m4v|wmv|mov|mpg|iso)$", "", regex=True)
                  .str.replace(r"(?i)(?:https?://)?(?:www\.)?[a-z0-9-]+\.(?:com|net|org|tc|cc|me|io|to|se|mx|pl|ru|uno|win|tel|cz|world|one|mu|trade|co|tv|am|ag|is|club|xyz|info)\b", " ", regex=True))
u["is_pack"] = (u["n_movies_in_torrent"] > 1) | name.str.contains(PACK_WORDS) | name.str.contains(YEAR_RANGE)


def year_ok(n, start_year, pack):
    if pack or pd.isna(start_year):
        return True
    ys = [int(y) for y in YEARS.findall(n)]
    return not ys or any(abs(y - start_year) <= 1 for y in ys)


u["name_year_ok"] = [year_ok(n, y, p) for n, y, p in zip(name, u["start_year"], u["is_pack"])]
u["name_tier"] = None
for tier, pat in reversed(NAME_TIER):          # thứ tự ưu tiên: pre_release > web > disc > tv
    u.loc[name_noext.str.contains(pat, regex=True), "name_tier"] = tier
u["quality_tier"] = u["file_tier"].where(u["file_tier"].notna() & (u["file_tier"] != "pre_release"), u["name_tier"])
u.loc[(u["file_tier"] == "pre_release") | (u["name_tier"] == "pre_release"), "quality_tier"] = "pre_release"
u["quality_tier"] = u["quality_tier"].fillna("unknown")
con.register("u_df", u)
con.execute("CREATE TABLE u4 AS SELECT * FROM u_df WHERE name_year_ok")
step("combined", "I. năm trên tên torrent khớp năm phim (trừ gói)", "u4", file_level=False)

# J. Bản chất lượng X không thể có trước ngày phát hành định dạng X (theo TMDb, mọi nước):
#    WEB trước ngày Digital, BluRay/DVD trước ngày Digital/đĩa, bất kỳ bản nào trước lần ra
#    mắt đầu tiên -> torrent giả/mạo danh (vd. 7 bản "Quantumania BluRay" cùng 0.67GB, 2 tháng
#    trước khi ra rạp). Giữ trong bảng torrent (cờ `implausible`) nhưng không tính ở cấp phim.
con.execute(f"""
CREATE TABLE tor AS
SELECT u.* EXCLUDE (name_year_ok, n_movies_in_torrent, start_year, file_tier, name_tier),
       u.discovered_at_utc BETWEEN '{STABLE_START}' AND '{STABLE_END}' AS in_stable_window,
       coalesce(
           (u.quality_tier = 'web'  AND u.discovered_at_utc < t.first_digital - INTERVAL 7 DAY)
        OR (u.quality_tier = 'disc' AND u.discovered_at_utc <
                least(coalesce(t.first_digital, t.first_physical), coalesce(t.first_physical, t.first_digital))
                - INTERVAL 7 DAY)
        OR (u.discovered_at_utc < r.earliest_release),
       FALSE) AS implausible
FROM u4 u
LEFT JOIN read_parquet('{TMDB}') t USING (imdb_id)
LEFT JOIN first_release r USING (imdb_id)
""")
con.execute("CREATE TEMP VIEW tor_ok AS SELECT * FROM tor WHERE NOT implausible")
step("combined", "J. bỏ torrent không hợp lý (bản nét trước ngày phát hành)", "tor_ok", file_level=False)
con.execute(f"COPY tor TO '{(DC / 'torrents_clean.parquet').as_posix()}' (FORMAT PARQUET)")
print()
print(con.sql("""SELECT source, count(*) AS torrents, count(DISTINCT imdb_id) AS movies,
                        count(*) FILTER (WHERE in_stable_window) AS torrents_stable
                 FROM tor GROUP BY ROLLUP(source) ORDER BY source"""))

# =========================== Bảng cấp phim ===================================
con.execute(f"""
COPY (
WITH s AS (
    SELECT imdb_id,
           count(*) FILTER (WHERE in_stable_window)                         AS n_torrents_stable,
           count(*) FILTER (WHERE in_stable_window AND strict)              AS n_torrents_stable_strict,
           count(*) FILTER (WHERE in_stable_window AND NOT is_pack)         AS n_torrents_stable_nopack,
           count(*) FILTER (WHERE in_stable_window AND source <> 'name_match') AS n_torrents_stable_magnetdb,
           count(DISTINCT lower(torrent_name)) FILTER (WHERE in_stable_window) AS n_names_stable,
           count(*)                                                         AS n_torrents_all,
           min(discovered_at_utc)                                           AS first_torrent_at,
           arg_min(quality_tier, discovered_at_utc)                         AS first_torrent_tier,
           min(discovered_at_utc) FILTER (WHERE quality_tier NOT IN ('pre_release', 'unknown'))
                                                                            AS first_hq_torrent_at,
           count(*) FILTER (WHERE quality_tier = 'pre_release')             AS n_pre_release
    FROM tor_ok GROUP BY imdb_id
)
SELECT m.imdb_id, m.title, m.original_title, m.start_year, m.runtime_min, m.genres, m.is_adult,
       m.avg_rating, m.num_votes,
       t.* EXCLUDE (imdb_id),
       s.* EXCLUDE (imdb_id),
       -- độ trễ (ngày) — chỉ có nghĩa khi mốc phát hành nằm trong cửa sổ ổn định
       date_diff('day', t.first_theatrical, s.first_torrent_at::DATE)    AS leak_days_after_theatrical,
       date_diff('day', t.first_theatrical, s.first_hq_torrent_at::DATE) AS hq_leak_days_after_theatrical,
       date_diff('day', t.first_theatrical, t.first_digital)             AS digital_days_after_theatrical,
       t.first_theatrical BETWEEN '{STABLE_START}' AND '{STABLE_END}'     AS theatrical_in_stable,
       t.first_digital    BETWEEN '{STABLE_START}' AND '{STABLE_END}'     AS digital_in_stable
FROM read_parquet('{MOVIES}') m
LEFT JOIN read_parquet('{TMDB}') t USING (imdb_id)
JOIN s USING (imdb_id)
ORDER BY n_torrents_stable DESC
) TO '{(DC / 'movie_analysis.parquet').as_posix()}' (FORMAT PARQUET)
""")

pd.DataFrame(log).to_csv(DC / "cleaning_log.csv", index=False, encoding="utf-8-sig")

mv = con.execute(f"SELECT * FROM read_parquet('{(DC / 'movie_analysis.parquet').as_posix()}')").df()
print(f"\nWrote torrents_clean.parquet, movie_analysis.parquet ({len(mv):,} phim), cleaning_log.csv")
print(f"  phim có torrent trong cửa sổ ổn định: {(mv['n_torrents_stable'] > 0).sum():,}")
print(f"  có dữ liệu TMDb:                       {mv['tmdb_found'].fillna(False).sum():,}")
print(f"  ra rạp trong cửa sổ ổn định:           {mv['theatrical_in_stable'].fillna(False).sum():,}")
print(f"  ra Digital trong cửa sổ ổn định:       {mv['digital_in_stable'].fillna(False).sum():,}")
print("\nTop 15 phim theo số torrent (cửa sổ ổn định, sau làm sạch):")
print(mv[["imdb_id", "title", "start_year", "num_votes", "n_torrents_stable", "n_torrents_stable_magnetdb",
          "n_pre_release"]].head(15).to_string(index=False))
