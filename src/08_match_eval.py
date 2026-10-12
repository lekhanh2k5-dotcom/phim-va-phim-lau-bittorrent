"""
Stage 2d: pipeline match TỰ VIẾT (tên file -> IMDb tconst) và đánh giá so với MagnetDB.

Cách làm:
  1. guessit tách title / year / type (movie|episode) từ tên file.
  2. Chuẩn hóa tên (bỏ dấu, lowercase, bỏ ký tự đặc biệt) — làm trong DuckDB cho cả
     hai phía để đảm bảo cùng một quy tắc.
  3. Tra CHÍNH XÁC trong chỉ mục tên IMDb (primaryTitle + originalTitle + title.akas
     của mọi phim movie/tvMovie/video có rating), lọc năm ±1, chọn phim nhiều vote nhất.
  4. Không có -> so GẦN ĐÚNG bằng rapidfuzz trong khối cùng năm ±1 (ngưỡng FUZZY_CUTOFF).
     Không có năm -> chỉ so với phim >= 1000 vote (tránh quét cả triệu tên).
  5. File có số mùa (S01E02...) -> không match (pipeline này chỉ nhận PHIM).
  Xử lý thêm: đĩa DVD/Blu-ray (lấy tên thư mục chứa VIDEO_TS/BDMV), tên có dấu "-"
  (ghép alternative_title), số thứ tự đầu tên ("01 Неизвестный").

"Ground truth" = movieMatchTitleId của MagnetDB. Nó KHÔNG phải nhãn người gán và có lỗi
(vd. "1. Introduction.mp4" -> The Intruder), nên số đo ở đây là MỨC ĐỒNG THUẬN; các ca
bất đồng được xuất ra để gán nhãn tay (xem match_audit.csv).

Đơn vị đánh giá: tên file DUY NHẤT (bỏ trùng path) mà MagnetDB gán vào một PHIM.

Đầu ra:
  data_clean/match_eval.parquet   từng tên file: parse, dự đoán, phương pháp, điểm, đúng/sai
  data_clean/match_audit.csv      mẫu các ca bất đồng, cột manual_label để điền tay

Chạy:  python src/08_match_eval.py [--n 20000] [--seed 42]
"""

import argparse
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from guessit import guessit
from rapidfuzz import fuzz, process

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT     = Path(__file__).resolve().parent.parent
FILES_PQ = (ROOT / "data_clean/matched_files.parquet").as_posix()
MOVIES   = (ROOT / "data_clean/movies.parquet").as_posix()
CATALOG  = (ROOT / "data_clean/imdb_catalog.parquet").as_posix()
INDEX_PQ = ROOT / "data_clean/imdb_title_index.parquet"   # tạo bởi 03_imdb_catalog.py
OUT_PQ   = ROOT / "data_clean/match_eval.parquet"
AUDIT    = ROOT / "data_clean/match_audit.csv"

FUZZY_CUTOFF   = 90     # điểm rapidfuzz tối thiểu (0-100)
NO_YEAR_VOTES  = 1000   # file không có năm: chỉ so gần đúng với phim >= ngưỡng vote này
AUDIT_SIZE     = 200

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=20000, help="số tên file duy nhất để đánh giá")
ap.add_argument("--seed", type=int, default=42)
args = ap.parse_args()

# Cùng một quy tắc chuẩn hóa cho tên IMDb và tên tách từ file.
NORM = r"trim(regexp_replace(lower(strip_accents({col})), '[^\pL\pN]+', ' ', 'g'))"
con = duckdb.connect()

# ---- 1. Chỉ mục tên IMDb (tạo bởi 03_imdb_catalog.py) -------------------------
if not INDEX_PQ.exists():
    raise SystemExit("Chưa có imdb_title_index.parquet -> chạy src/03_imdb_catalog.py trước.")
idx = con.execute(f"SELECT * FROM read_parquet('{INDEX_PQ.as_posix()}') WHERE norm <> ''").df()
print(f"Title index: {len(idx):,} (tên chuẩn hóa, tconst) — {idx['tconst'].nunique():,} phim")

# token_sort_ratio = ratio trên chuỗi đã sắp xếp từ. Sắp xếp sẵn 1 lần cho mọi tên IMDb
# rồi dùng fuzz.ratio theo lô (cdist, đa luồng) -> nhanh hơn hàng chục lần.
def sort_key(s):
    return " ".join(sorted(s.split()))


exact = defaultdict(list)                 # norm -> [(tconst, year, votes)]
fuzzy_cands = defaultdict(list)           # sort_key -> [(tconst, year, votes)]
by_year = defaultdict(set)                # year -> {sort_key}
popular = set()                           # sort_key của phim nhiều vote (file không có năm)
for norm, tconst, year, votes in idx.itertuples(index=False):
    year = None if pd.isna(year) else int(year)
    cand = (tconst, year, votes)
    exact[norm].append(cand)
    key = sort_key(norm)
    fuzzy_cands[key].append(cand)
    if year is not None:
        by_year[year].add(key)
    if votes >= NO_YEAR_VOTES:
        popular.add(key)


def pick(cands, year):
    """Trong các phim cùng tên: ưu tiên khớp năm ±1, rồi nhiều vote nhất."""
    if year is not None:
        cands = [c for c in cands if c[1] is not None and abs(c[1] - year) <= 1]
    return max(cands, key=lambda c: c[2])[0] if cands else None


def match_all(variants, years, is_tv):
    """variants[i] = các cách viết tên đã chuẩn hóa của file i, theo thứ tự ưu tiên.
    Pass 1: tra chính xác từng cách viết. Pass 2: so gần đúng theo lô (gom file cùng năm)
    với cách viết đầu tiên (đầy đủ nhất)."""
    out = [None] * len(variants)
    pending = defaultdict(list)            # year|None -> [row index]
    for i, (vs, year, tv) in enumerate(zip(variants, years, is_tv)):
        if tv:
            out[i] = (None, "tv_episode", None)
            continue
        if not vs:
            out[i] = (None, "no_title", None)
            continue
        for v in vs:
            if v in exact and (hit := pick(exact[v], year)):
                out[i] = (hit, "exact", 100.0)
                break
        else:
            pending[year].append(i)

    for year, rows in pending.items():
        pool = (by_year[year - 1] | by_year[year] | by_year[year + 1]) if year is not None else popular
        choices = list(pool)
        queries = [sort_key(variants[i][0]) for i in rows]
        scores = process.cdist(queries, choices, scorer=fuzz.ratio, dtype=np.uint8,
                               score_cutoff=FUZZY_CUTOFF, workers=-1)
        best = scores.argmax(axis=1)
        for i, j, row in zip(rows, best, scores):
            hit = pick(fuzzy_cands[choices[j]], year) if row[j] >= FUZZY_CUTOFF else None
            out[i] = (hit, "fuzzy", float(row[j])) if hit else (None, "no_match", None)
    return out


# ---- 2. Mẫu đánh giá ------------------------------------------------------
con.execute(f"SELECT setseed({(args.seed % 1000) / 1000})")
sample = con.execute(f"""
    WITH uniq AS (
        SELECT path, any_value(f.imdb_id) AS truth, any_value(f.match_score) AS magnet_score,
               bool_or(f.is_tv_hint) AS is_tv_hint, count(*) AS n_dup
        FROM read_parquet('{FILES_PQ}') f SEMI JOIN read_parquet('{MOVIES}') m USING (imdb_id)
        GROUP BY path
    )
    SELECT * FROM uniq ORDER BY random() LIMIT {args.n}
""").df()
print(f"Sample: {len(sample):,} tên file duy nhất (truth = PHIM theo MagnetDB)")

# ---- 3. Parse + match -----------------------------------------------------
DISC_DIRS = {"video_ts", "bdmv"}           # cấu trúc đĩa DVD / Blu-ray


def parse(path):
    parts = [x for x in path.replace("\\", "/").split("/") if x]
    # VIDEO_TS/VTS_01_1.VOB -> tên phim nằm ở thư mục CHỨA VIDEO_TS
    for k, part in enumerate(parts):
        if part.lower() in DISC_DIRS and k > 0:
            parts = parts[:k]
            break
    try:
        g = guessit("/".join(parts[-2:]))     # thư mục cha + tên file
    except Exception:
        g = {}
    title, alt = g.get("title"), g.get("alternative_title")
    variants = []
    if isinstance(title, str):
        # "L'era Glaciale 2 - Il Disgelo": guessit cắt phần sau dấu "-" thành alternative_title
        if alt:
            variants.append(" ".join([title, *([alt] if isinstance(alt, str) else map(str, alt))]))
        variants.append(title)
    year = g.get("year") if isinstance(g.get("year"), int) else None
    # Chỉ coi là phim bộ khi có số MÙA (S01E02). "126-Christopher Columbus" bị guessit
    # gọi là episode 126 nhưng thực ra là số thứ tự trong bộ sưu tập.
    return {"g_title": variants[-1] if variants else None, "g_alt": variants[0] if alt else None,
            "g_year": year, "g_tv": "season" in g, "raw_variants": variants}


t0 = time.time()
sample = pd.concat([sample, pd.DataFrame([parse(p) for p in sample["path"]])], axis=1)
print(f"guessit: {time.time() - t0:.0f}s")

# Chuẩn hóa mọi cách viết bằng cùng hàm NORM của DuckDB; thêm bản bỏ số thứ tự đầu
# ("01 Неизвестный" -> "Неизвестный"), chỉ dùng sau bản gốc nên "21 Jump Street" vẫn đúng.
flat = pd.DataFrame([(i, k, v) for i, vs in enumerate(sample["raw_variants"]) for k, v in enumerate(vs)],
                    columns=["i", "k", "v"])
con.register("flat", flat)
flat = con.execute(f"SELECT i, k, {NORM.format(col='v')} AS norm FROM flat").df()
variants = [[] for _ in range(len(sample))]
for i, _, norm in flat.sort_values(["i", "k"]).itertuples(index=False):
    for v in (norm, re.sub(r"^\d{1,3} ", "", norm)):
        if v and v not in variants[i]:
            variants[i].append(v)
sample["norm"] = [vs[0] if vs else None for vs in variants]
sample = sample.drop(columns="raw_variants")

t0 = time.time()
res = match_all(variants, [None if pd.isna(y) else int(y) for y in sample["g_year"]], sample["g_tv"])
sample[["pred", "method", "fuzzy_score"]] = pd.DataFrame(res, index=sample.index)
print(f"match:   {time.time() - t0:.0f}s")

sample["correct"] = sample["pred"] == sample["truth"]
sample["script"] = sample["path"].str.contains(r"[Ѐ-ӿ]", regex=True).map(
    {True: "cyrillic", False: "latin/other"})
sample.to_parquet(OUT_PQ, index=False)

# ---- 4. Metrics -------------------------------------------------------------
def metrics(df):
    n, n_pred, n_ok = len(df), df["pred"].notna().sum(), df["correct"].sum()
    p = n_ok / n_pred if n_pred else 0.0
    r = n_ok / n if n else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return pd.Series({"n": n, "predicted": n_pred, "agree": n_ok,
                      "precision": round(p, 3), "recall": round(r, 3), "f1": round(f1, 3)})

print("\n== Overall (đồng thuận với MagnetDB)")
print(metrics(sample).to_string())
print("\n== Theo phương pháp")
print(sample.groupby("method")[["correct"]].agg(["count", "mean"]).round(3).to_string())
print("\n== Theo loại chữ trong tên file")
print(sample.groupby("script").apply(metrics, include_groups=False).to_string())
print("\n== Theo cờ TV (MagnetDB gán file có season/episode vào PHIM)")
print(sample.groupby("is_tv_hint").apply(metrics, include_groups=False).to_string())

# ---- 5. Mẫu bất đồng để gán nhãn tay ---------------------------------------
cat = con.execute(f"SELECT tconst, primaryTitle, start_year FROM read_parquet('{CATALOG}')").df()
names = dict(zip(cat["tconst"], cat["primaryTitle"] + " (" + cat["start_year"].astype("Int64").astype(str) + ")"))
movie_names = con.execute(f"SELECT imdb_id, title || ' (' || start_year || ')' FROM read_parquet('{MOVIES}')").fetchall()
names.update(dict(movie_names))
dis = sample[~sample["correct"]].sample(min(AUDIT_SIZE, (~sample["correct"]).sum()), random_state=args.seed)
audit = pd.DataFrame({
    "path": dis["path"], "guessit_title": dis["g_title"], "guessit_year": dis["g_year"],
    "magnetdb_imdb": dis["truth"], "magnetdb_title": dis["truth"].map(names),
    "magnetdb_score": dis["magnet_score"].round(1),
    "ours_imdb": dis["pred"], "ours_title": dis["pred"].map(names), "ours_method": dis["method"],
    "manual_label": "",   # điền: magnetdb | ours | both_wrong | unsure
})
audit.to_csv(AUDIT, index=False, encoding="utf-8-sig")
print(f"\nWrote {OUT_PQ.relative_to(ROOT)} và {AUDIT.relative_to(ROOT)} ({len(audit)} ca bất đồng để gán nhãn tay)")
