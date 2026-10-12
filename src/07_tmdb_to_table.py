"""
Stage 2c: chuyển cache JSON của TMDb (data_raw/tmdb_cache/*.json) thành bảng Parquet.

Đầu ra:
  data_clean/tmdb_movies.parquet          1 dòng / phim: kinh tế + các mốc phát hành tóm tắt
  data_clean/tmdb_release_dates.parquet   dạng dài: imdb_id, country, type, release_date
  data_clean/tmdb_watch_providers.parquet dạng dài: imdb_id, country, kind, provider (JustWatch)

Loại release_dates của TMDb: 1 Premiere, 2 Theatrical (limited), 3 Theatrical,
4 Digital, 5 Physical, 6 TV.
Có thể chạy khi 06 chưa xong — chỉ xử lý những phim đã cache.

Chạy:  python src/07_tmdb_to_table.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252

ROOT      = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data_raw/tmdb_cache"
OUT_DIR   = ROOT / "data_clean"

movies, releases, providers = [], [], []
for path in CACHE_DIR.glob("*.json"):
    rec = json.loads(path.read_text(encoding="utf-8"))
    imdb_id = rec["imdb_id"]
    d = rec.get("details")
    if not rec.get("found") or not d:
        movies.append({"imdb_id": imdb_id, "tmdb_found": False})
        continue

    for c in d.get("release_dates", {}).get("results", []):
        for r in c["release_dates"]:
            releases.append({"imdb_id": imdb_id, "country": c["iso_3166_1"],
                             "type": r["type"], "release_date": r["release_date"][:10],
                             "note": r.get("note") or None})

    for country, kinds in d.get("watch/providers", {}).get("results", {}).items():
        for kind in ("flatrate", "free", "ads", "rent", "buy"):
            for p in kinds.get(kind, []):
                providers.append({"imdb_id": imdb_id, "country": country, "kind": kind,
                                  "provider": p["provider_name"]})

    movies.append({
        "imdb_id":           imdb_id,
        "tmdb_found":        True,
        "tmdb_id":           d["id"],
        "tmdb_title":        d.get("title"),
        "original_language": d.get("original_language"),
        "origin_country":    ",".join(d.get("origin_country") or []) or None,
        "tmdb_genres":       ",".join(g["name"] for g in d.get("genres") or []) or None,
        "in_collection":     d.get("belongs_to_collection") is not None,  # phim thuộc series
        "collection_name":   (d.get("belongs_to_collection") or {}).get("name"),
        "production_companies": ",".join(c["name"] for c in d.get("production_companies") or []) or None,
        "production_countries": ",".join(c["iso_3166_1"] for c in d.get("production_countries") or []) or None,
        "release_date":      d.get("release_date") or None,
        "budget":            d.get("budget") or None,    # TMDb dùng 0 cho "không rõ"
        "revenue":           d.get("revenue") or None,
        "runtime":           d.get("runtime") or None,
        "popularity":        d.get("popularity"),
        "tmdb_vote_count":   d.get("vote_count"),
        "tmdb_vote_avg":     d.get("vote_average"),
    })

mv = pd.DataFrame(movies)
rd = pd.DataFrame(releases, columns=["imdb_id", "country", "type", "release_date", "note"])
wp = pd.DataFrame(providers, columns=["imdb_id", "country", "kind", "provider"])
rd["release_date"] = pd.to_datetime(rd["release_date"], errors="coerce")
mv["release_date"] = pd.to_datetime(mv["release_date"], errors="coerce")


def first_date(types, country=None, name=None):
    sub = rd[rd["type"].isin(types)]
    if country:
        sub = sub[sub["country"] == country]
    return sub.groupby("imdb_id")["release_date"].min().rename(name)


summary = pd.concat([
    first_date([2, 3], name="first_theatrical"),          # sớm nhất trên thế giới
    first_date([2, 3], "US", name="us_theatrical"),
    first_date([4], name="first_digital"),                # mốc "có cách xem hợp pháp online"
    first_date([4], "US", name="us_digital"),
    first_date([5], name="first_physical"),
    rd.groupby("imdb_id")["country"].nunique().rename("n_release_countries"),
], axis=1)

flat = wp[wp["kind"].isin(["flatrate", "free", "ads"])]   # xem được không cần mua/thuê lẻ
summary = summary.join(pd.concat([
    wp.groupby("imdb_id")["country"].nunique().rename("n_countries_any_provider"),
    flat.groupby("imdb_id")["country"].nunique().rename("n_countries_streaming"),
    flat[flat["country"] == "US"].groupby("imdb_id")["provider"]
        .agg(lambda s: ",".join(sorted(set(s)))).rename("us_streaming_providers"),
], axis=1), how="outer")

mv = mv.merge(summary, left_on="imdb_id", right_index=True, how="left")
mv["us_streaming_now"] = mv["us_streaming_providers"].notna()
for col in ["n_release_countries", "n_countries_any_provider", "n_countries_streaming"]:
    mv[col] = mv[col].fillna(0).astype(int)

mv.to_parquet(OUT_DIR / "tmdb_movies.parquet", index=False)
rd.to_parquet(OUT_DIR / "tmdb_release_dates.parquet", index=False)
wp.to_parquet(OUT_DIR / "tmdb_watch_providers.parquet", index=False)

found = mv[mv["tmdb_found"]]
print(f"Phim đã cache:          {len(mv):,}   (tìm thấy trên TMDb: {len(found):,})")
print(f"  có ngày ra rạp:       {found['first_theatrical'].notna().mean():.0%}")
print(f"  có ngày Digital:      {found['first_digital'].notna().mean():.0%}")
print(f"  có revenue:           {found['revenue'].notna().mean():.0%}")
print(f"  có budget:            {found['budget'].notna().mean():.0%}")
print(f"  đang streaming ở Mỹ:  {found['us_streaming_now'].mean():.0%}")
print(f"release_dates rows:     {len(rd):,}")
print(f"watch_providers rows:   {len(wp):,}")
